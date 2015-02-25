# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import random
import getpass
import uuid

import ftrack
from PySide import QtCore, QtGui

from harness import Harness

import ftrack_connect.ui.widget.user_presence
import ftrack_connect.crew_hub
import ftrack_connect.event_hub_thread


class MyCrewHub(ftrack_connect.crew_hub.SignalCrewHub):

    def isInterested(self, data):
        return True


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        ftrack.setup()

        self.eventHubThread = ftrack_connect.event_hub_thread.EventHubThread()
        self.eventHubThread.start()

        self.users = [
            user for user in ftrack.getUsers() if (
                user.get('username') != getpass.getuser()
            )
        ]
        self.groups = (
            'Assigned', 'Related', 'Others', 'Contributors', 'Others'
        )

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

        self.crewHub = MyCrewHub()

        self.crewHub.onEnter.connect(self.userPresence.onEnter)
        self.crewHub.onHeartbeat.connect(self.userPresence.onHeartbeat)
        self.crewHub.onExit.connect(self.userPresence.onExit)

        user = ftrack.getUser(getpass.getuser())
        data = {
            'session_id': uuid.uuid1().hex,
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

if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
