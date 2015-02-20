# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import uuid
import random
import datetime

from PySide import QtGui, QtCore
import ftrack

import ftrack_connect.ui.widget.label
import ftrack_connect.ui.widget.user_list
import ftrack_connect.ui.widget.user

class UserPresence(QtGui.QWidget):

    def __init__(self, users, groups, parent=None):
        '''Instantiate widget with *users* and *groups*.'''
        super(UserPresence, self).__init__(parent)

        self._users = users
        self._groups = groups

        self.userList = ftrack_connect.ui.widget.user_list.UserList(
            groups=self._groups
        )
        self.userList.setObjectName('time-log-list')

        self.userInfoContainer = QtGui.QWidget()
        self.userInfoContainer.setLayout(QtGui.QVBoxLayout())
        # self.userInfoContainer.setSizePolicy(
        #     QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        # )

        self.setLayout(QtGui.QHBoxLayout())
        self._userInfo = None

        self.layout().addWidget(
            self.userList, stretch=1
        )
        self.layout().addWidget(
            self.userInfoContainer, stretch=1
        )
        self.userList.setFixedWidth(150)
        self.userList.itemClicked.connect(self._itemClickedHandler)

        for user, group in self._users:
            self.userList.addItem({
                'name': user.getName(),
                'userId': user.getId(),
                'group': group
            })

    def _handlePresenceEvent(self, presenceEnterEvent):
        '''Handle *presenceEnterEvent* from hub.
        
        Structure of a presenceEnterEvent
        {
            user
                id
                name
                thumbnail
            application
                identifier
                label
                activity
            context
                containers
                project_id
            session_id <uuid>
            timestamp <datetime>
        }
        '''
        self.userList.addSession(
            presenceEnterEvent['user']['id'],
            presenceEnterEvent['session_id'],
            presenceEnterEvent['timestamp'],
            presenceEnterEvent['application']
        )

    def _handleHeartbeatEvent(self, presenceHeartbeatEvent):
        self.userList.updateSession(
            presenceHeartbeatEvent['session_id'],
            presenceHeartbeatEvent['timestamp'],
            presenceHeartbeatEvent['activity']
        )

    def _handleExitEvent(self, sessionId):
        pass

    def _itemClickedHandler(self, value):
        if self._userInfo is None:
            self._userInfo = ftrack_connect.ui.widget.user.UserExtended(
                value.get('name'),
                value.get('user_id'),
                value.get('applications')
            )

            self.userInfoContainer.layout().addWidget(self._userInfo)

        self._userInfo.updateInfo(
            value.get('name'),
            value.get('user_id'),
            value.get('applications')
        )
