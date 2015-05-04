# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import getpass

import ftrack
from PySide import QtCore, QtGui

from harness import Harness

import ftrack_connect.ui.widget.crew
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
            'Assigned', 'Related', 'Contributors', 'Others'
        )

        widget = QtGui.QWidget()
        widget.setLayout(QtGui.QVBoxLayout())
        widget.setMinimumSize(QtCore.QSize(600, 600))

        self.crewHub = MyCrewHub()
        self.crew = ftrack_connect.ui.widget.crew.Crew(
            self.groups, hub=self.crewHub
        )
        widget.layout().addWidget(self.crew)

        for user in self.users:
            self.crew.addUser(
                user.getName(), user.getId()
            )

        user = ftrack.getUser(getpass.getuser())
        data = {
            'user': {
                'name': user.getName(),
                'id': user.getId()
            },
            'application': {
                'identifier': 'ftrack',
                'label': 'ftrack'
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
