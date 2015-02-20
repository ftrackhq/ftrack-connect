# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import random
import uuid
import datetime
import getpass

import ftrack
from PySide import QtCore, QtGui

from harness import Harness

import ftrack_connect.ui.widget.user_presence
import ftrack_connect.crew_hub


class MyCrewHub(ftrack_connect.crew_hub.CrewHub):

    def isInterested(self, data):
        if (
            self._myData['context']['project_id'] ==
            data['context']['project_id']
        ):
            return True

        return False


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
        ftrack.setup()
        import ftrack_connect.event_hub_thread
        self.eventHubThread = ftrack_connect.event_hub_thread.EventHubThread()
        self.eventHubThread.start()

        self.users = ftrack.getUsers()
        self.groups = ('Assigned', 'Related', 'Others', 'Contributors', 'Others')
        self.sessionIds = set()

        widget = QtGui.QWidget()
        widget.setLayout(QtGui.QVBoxLayout())
        widget.setMinimumSize(QtCore.QSize(400, 600))

        self.userPresence = ftrack_connect.ui.widget.user_presence.UserPresence(
            self.groups
        )
        widget.layout().addWidget(self.userPresence)

        for user in self.users:
            self.userPresence.addUser(
                user.getName(), user.getId(), random.choice(self.groups)
            )

        self.crewHub = MyCrewHub(
            onPresence=self._onPresence,
            onHeartbeat=self._onHeartbeat,
            onExit=self._onExit
        )

        user = ftrack.getUser(getpass.getuser())
        data = {
            'user': {
                'name': user.getName(),
                'id': user.getId()
            },
            'application': {
                'identifier': 'nuke',
                'label': 'Nuke'
            },
            'context': {
                'project_id': 'my_project_id',
                'containers': []
            }
        }

        self.crewHub.enter(data)

        return widget

    def _onPresence(self, data):
        self.sessionIds.add(data['session_id'])
        data['timestamp'] = datetime.datetime.utcnow()
        self.userPresence._handlePresenceEvent(data)

    def _onHeartbeat(self, data):
        self.userPresence._handleHeartbeatEvent({
            'timestamp': datetime.datetime.utcnow(),
            'activity': (
                datetime.datetime.utcnow() -
                datetime.timedelta(seconds=random.randint(1, 120))
            ),
            'session_id': data['session_id']
        })

    def _onExit(self, data):
        self.userPresence._handleExitEvent(data['session_id'])

if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
