# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import logging

from PySide import QtGui

import ftrack_connect.ui.widget.label
import ftrack_connect.ui.widget.user_list
import ftrack_connect.ui.widget.user


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

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        # Setup signal handlers if hub is configured.
        if hub:
            hub.onEnter.connect(self.onEnter)
            hub.onHeartbeat.connect(self.onHeartbeat)
            hub.onExit.connect(self.onExit)

        self._groups = groups

        self.userList = ftrack_connect.ui.widget.user_list.UserList(
            groups=self._groups
        )

        self.userInformation = QtGui.QWidget()
        self.userInformation.setLayout(QtGui.QVBoxLayout())

        self.setLayout(QtGui.QHBoxLayout())
        self._userInfo = None

        self.layout().addWidget(
            self.userList, stretch=1
        )
        self.layout().addWidget(
            self.userInformation, stretch=1
        )
        self.userList.setFixedWidth(200)
        self.userList.itemClicked.connect(self._itemClickedHandler)

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

    def _itemClickedHandler(self, value):
        '''Handle item clicked event.'''
        if self._userInfo is None:
            self._userInfo = ftrack_connect.ui.widget.user.UserExtended(
                value.get('name'),
                value.get('user_id'),
                value.get('applications')
            )

            self.userInformation.layout().addWidget(self._userInfo)

        self._userInfo.updateInformation(
            value.get('name'),
            value.get('user_id'),
            value.get('applications')
        )
