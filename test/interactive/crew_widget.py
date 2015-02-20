# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import random
import uuid
import datetime

import ftrack
from PySide import QtCore, QtGui

from harness import Harness

import ftrack_connect.ui.widget.user_presence

class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def generatePresence(self):
        user = random.choice(self.users)
        session_id = str(uuid.uuid4())
        activity = (
            datetime.datetime.utcnow() -
            datetime.timedelta(seconds = random.randint(1, 120))
        )

        return {
            'user': {
                'id': user.getId(),
                'thumbnail': user.get('thumbid'),
                'name': user.getName()
            },
            'application': random.choice([
                {
                    'name': 'nuke',
                    'label': 'Nuke 9.0v4',
                    'activity': activity
                }, {
                    'name': 'maya',
                    'label': 'Maya 2015',
                    'activity': activity
                }, {
                    'name': 'nuke_studio',
                    'label': 'NukeStudio 9.0v3',
                    'activity': activity
                }
            ]),
            'context': {},
            'timestamp': datetime.datetime.utcnow(),
            'session_id': session_id
        }

    def constructWidget(self):
        '''Return widget instance to test.'''
        self.users = ftrack.getUsers()
        self.groups = ('Assigned', 'Related', 'Others',)
        self.sessionIds = set()

        widget = QtGui.QWidget()
        widget.setLayout(QtGui.QVBoxLayout())
        widget.setMinimumSize(QtCore.QSize(400, 600))

        usersAndGroups = []
        for user in self.users:
            usersAndGroups.append(
                (user, random.choice(self.groups))
            )

        self.userPresence = ftrack_connect.ui.widget.user_presence.UserPresence(
            usersAndGroups, self.groups
        )
        widget.layout().addWidget(self.userPresence)


        presenceButton = QtGui.QPushButton('Enter')
        widget.layout().addWidget(presenceButton)
        presenceButton.clicked.connect(self._addPresence)

        heartbeatButton = QtGui.QPushButton('Heartbeat')
        widget.layout().addWidget(heartbeatButton)
        heartbeatButton.clicked.connect(self._addHeartbeat)

        exitButton = QtGui.QPushButton('Exit')
        widget.layout().addWidget(exitButton)
        exitButton.clicked.connect(self._addExit)

        return widget

    def _addPresence(self):
        presence = self.generatePresence()
        self.sessionIds.add(presence['session_id'])
        self.userPresence._handlePresenceEvent(presence)

    def _addHeartbeat(self):
        sessionId = random.choice(list(self.sessionIds))
        self.userPresence._handleHeartbeatEvent({
            'timestamp': datetime.datetime.utcnow(),
            'activity': (
                datetime.datetime.utcnow() -
                datetime.timedelta(seconds = random.randint(1, 120))
            ),
            'session_id': sessionId
        })

    def _addExit(self):
        sessionId = self.sessionIds.pop()
        self.userPresence._handleExitEvent(sessionId)

if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
