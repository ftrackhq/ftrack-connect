# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import uuid
import logging
import webbrowser

from PySide import QtGui

import ftrack_connect.ui.widget.label
import ftrack_connect.ui.widget.user_list
import ftrack_connect.ui.widget.user
import ftrack_connect.ui.widget.chat


CHAT_MESSAGES = dict()


def addMessageHistory(id, message):
    '''Add *message* to history with *id*.'''
    if id not in CHAT_MESSAGES:
        CHAT_MESSAGES[id] = []

    CHAT_MESSAGES[id].append(message)


def getMessageHistory(id):
    '''Return message history.'''
    return CHAT_MESSAGES.get(id, [])


def defaultClassifier(userId, applications):
    '''Default user classifier.'''
    return 'others', False


class Crew(QtGui.QWidget):
    '''User presence widget.'''

    def __init__(self, groups, hub=None, classifier=None, parent=None):
        '''Instantiate widget with *users* and *groups*.

        If *hub* is configured the Crew widget will connect listeners for::

            *onEnter*: enter event.
            *onHeartbeat*: hearbeat event.
            *onExit*: exit event.

        '''
        super(Crew, self).__init__(parent)

        self.setObjectName('crew')
        self.setContentsMargins(0, 0, 0, 0)

        self.currentUserId = None
        self.hub = hub

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        # If not classifier is specified return default `other` group.
        if not classifier:
            classifier = defaultClassifier

        self._classifier = classifier

        # Setup signal handlers if hub is configured.
        if hub:
            hub.onEnter.connect(self.onEnter)
            hub.onHeartbeat.connect(self.onHeartbeat)
            hub.onExit.connect(self.onExit)
            hub.onVideoConference.connect(self.onVideoConference)

        groups = [group.lower() for group in groups]

        if 'others' not in groups:
            groups.append('others')

        if 'offline' not in groups:
            groups.append('offline')

        self._groups = groups

        self.userList = ftrack_connect.ui.widget.user_list.UserList(
            groups=self._groups
        )

        self.userContainer = QtGui.QFrame()
        self.userContainer.setObjectName('user-container')
        self.userContainer.setLayout(QtGui.QVBoxLayout())
        self.userContainer.layout().setContentsMargins(0, 0, 0, 0)

        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self._extendedUser = None
        self.chat = ftrack_connect.ui.widget.chat.Chat()
        self.chat.chatMessageSubmitted.connect(self.onChatMessageSubmitClicked)

        self.userContainer.layout().addWidget(
            self.chat, stretch=1
        )

        self.layout().addWidget(
            self.userList, stretch=1
        )
        self.layout().addWidget(
            self.userContainer, stretch=3
        )

        self.userContainer.hide()

        self.userList.setMinimumWidth(180)
        self.userList.itemClicked.connect(self._itemClickedHandler)

        # Setup signal handlers if hub is configured.
        if hub:
            hub.onEnter.connect(self.onEnter)
            hub.onHeartbeat.connect(self.onHeartbeat)
            hub.onExit.connect(self.onExit)
            hub.onMessageReceived.connect(self.onMessageReceived)

    def classifyOnlineUsers(self):
        '''Classify all online users and move them to correct group.'''
        users = self.userList.users()

        for user in users:
            applications = user.value()['applications']
            group, highlight = self._classifier(user._userId, applications)
            if group != user.group and user.online:
                user.group = group
                uset.setHighlight(highlight)

                self.userList.updatePosition(user)

    def addUser(self, name, userId, group='offline'):
        '''Add user with *name*, *userId* and *group*.'''
        self.logger.debug(u'Adding user to user list: {0}'.format(name))
        if self.userList.userExists(userId):
            self.logger.debug(
                u'User with id {0} already exists'.format(userId)
            )
            return False

        self.userList.addUser({
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
        if not self.userList.userExists(data['user']['id']):
            self.userList.addUser({
                'name': data['user']['name'],
                'userId': data['user']['id'],
                'group': 'offline'
            })

        user = self.userList.getUser(data['user']['id'])

        user.addSession(
            data['session_id'], data['timestamp'], data['context'],
            data['application']
        )

        applications = user.value()['applications']

        group, highlight = self._classifier(user._userId, applications)
        user.group = group
        user.setHighlight(highlight)

        self.userList.updatePosition(user)

    def _onConferenceRequestClicked(self, userId):
        '''Handle conference clicked event and emit event from event hub.'''
        service = {
            'name': 'room',
            'data': 'https://room.co/#/ftrack-{0}'.format(
                uuid.uuid4().hex[0:16]
            )
        }

        self.hub.requestVideoConference(userId, service)
        webbrowser.open(service['data'])

    def onVideoConference(self, data):
        '''Handle video conference event with *data*.'''
        message = QtGui.QMessageBox()
        message.setText('Room conference                                     ')
        message.setInformativeText(
            ('{0} has requested a video conference with you. Do you want to '
            'join?').format(data['sender']['name'])
        )
        message.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        message.setDefaultButton(QtGui.QMessageBox.Yes)
        result = message.exec_()

        if result == QtGui.QMessageBox.Yes:
            webbrowser.open(data['service']['data'])

    def onHeartbeat(self, data):
        '''Handle heartbeat events with *data*.'''
        user = self.userList.getUser(data['user']['id'])
        if user:
            user.updateSession(
                data['session_id'], data['timestamp'], data.get('activity')
            )

    def onExit(self, data):
        '''Handle exit events with *data*.'''
        user = self.userList.getUser(data['user']['id'])
        if user:
            user.removeSession(data['session_id'])

        self.userList.updatePosition(user)

    def onMessageReceived(self, message):
        '''Handle *message* received.'''
        sender = message['sender']['id']
        addMessageHistory(sender, message)

        if sender == self.currentUserId:
            self.chat.addMessage(message)

    def onChatMessageSubmitClicked(self, messageText):
        '''Handle message submitted clicked.'''
        message = self.hub.sendMessage(self.currentUserId, messageText)
        message['me'] = True
        addMessageHistory(message['receiver'], message)
        self.chat.addMessage(message)

    def _itemClickedHandler(self, value):
        '''Handle item clicked event.'''
        self.currentUserId = value['userId']

        if self._extendedUser is None:
            self._extendedUser = ftrack_connect.ui.widget.user.UserExtended(
                value.get('name'),
                self.currentUserId,
                value.get('applications')
            )
            self._extendedUser.conferenceRequest.connect(
                self._onConferenceRequestClicked
            )

            self.userContainer.layout().insertWidget(0, self._extendedUser)
            self.userContainer.show()
        else:
            self._extendedUser.updateInformation(
                value.get('name'),
                self.currentUserId,
                value.get('applications')
            )

        self.chat.load(getMessageHistory(self.currentUserId))
