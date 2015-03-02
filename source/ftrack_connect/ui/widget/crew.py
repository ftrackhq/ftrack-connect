# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import logging

from PySide import QtGui

import ftrack_connect.ui.widget.label
import ftrack_connect.ui.widget.user_list
import ftrack_connect.ui.widget.user
import ftrack_connect.ui.widget.chat


CHAT_MESSAGES = dict()


class Crew(QtGui.QWidget):
    '''User presence widget.'''

    def __init__(self, groups, hub=None, parent=None):
        '''Instantiate widget with *users* and *groups*.

        If *hub* is configured the Crew widget will connect listeners for::

            *onEnter*: enter event.
            *onHeartbeat*: hearbeat event.
            *onExit*: exit event.

        '''
        super(Crew, self).__init__(parent)

        self.hub = hub

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._groups = groups

        self.userList = ftrack_connect.ui.widget.user_list.UserList(
            groups=self._groups
        )

        self.userContainer = QtGui.QWidget()
        self.userContainer.setLayout(QtGui.QVBoxLayout())

        self.setLayout(QtGui.QHBoxLayout())

        self._extendedUser = None
        self.chat = ftrack_connect.ui.widget.chat.Chat(parent)
        self.chat.chatMessageSubmitted.connect(self.onChatMessageSubmitClicked)

        self.layout().addWidget(
            self.userList, stretch=1
        )
        self.layout().addWidget(
            self.userContainer, stretch=1
        )
        self.userList.setFixedWidth(200)
        self.userList.itemClicked.connect(self._itemClickedHandler)

        # Setup signal handlers if hub is configured.
        if hub:
            hub.onEnter.connect(self.onEnter)
            hub.onHeartbeat.connect(self.onHeartbeat)
            hub.onExit.connect(self.onExit)
            hub.onMessageReceived.connect(self.onMessageReceived)

    def addUser(self, name, userId, group):
        '''Add user with *name*, *userId* and *group*.'''
        self.logger.debug(u'Adding user to user list: {0}'.format(name))
        if self.userList.userExists(userId):
            self.logger.debug(
                u'User with id {0} already exists'.format(userId)
            )
            return False

        self.userList.addItem({
            'name': name,
            'userId': userId,
            'group': group
        })

        return True

    def onEnter(self, data):
        '''Handle enter events with *data*.

        Structure of a data
        {
            user=dict(
                id
                name
                thumbnail
            ),
            application=dict(
                identifier
                label
                activity
            ),
            context=dict(
                containers
                project_id
            ),
            session_id=<uuid>
            timestamp=<datetime>
        }
        '''
        self.userList.addSession(
            data['user']['id'], data['session_id'], data['timestamp'],
            data['application']
        )

    def onHeartbeat(self, data):
        '''Handle heartbeat events with *data*.'''
        self.userList.updateSession(
            data['session_id'], data['timestamp'], data.get('activity')
        )

    def onExit(self, data):
        '''Handle exit events with *data*.'''
        self.userList.removeSession(data['session_id'])

    def onMessageReceived(self, message):
        self.chat.addMessage(message)

    def onChatMessageSubmitClicked(self, messageText):
        message = self.hub.sendMessage(self.currentUserId, messageText)
        self.chat.addMessage(message)

    def _itemClickedHandler(self, value):
        '''Handle item clicked event.'''
        self.currentUserId = value['user_id']

        if self._extendedUser is None:
            self._extendedUser = ftrack_connect.ui.widget.user.UserExtended(
                value.get('name'),
                self.currentUserId,
                value.get('applications')
            )

            self.userContainer.layout().addWidget(self._extendedUser)
            self.userContainer.layout().addWidget(self.chat)
        else:
            self._extendedUser.updateInformation(
                value.get('name'),
                self.currentUserId,
                value.get('applications')
            )

        self.chat.load(
            self.currentUserId, CHAT_MESSAGES.get(self.currentUserId, [])
        )
