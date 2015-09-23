# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import getpass

import ftrack
from PySide import QtCore, QtGui

from harness import Harness

import ftrack_connect.ui.widget.crew
import ftrack_connect.crew_hub
import ftrack_connect.event_hub_thread
import ftrack_connect.ui.theme


class MyCrewHub(ftrack_connect.crew_hub.SignalConversationHub):

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
        user = ftrack.getUser(getpass.getuser())

        self.crewHub = MyCrewHub()
        self.crew = ftrack_connect.ui.widget.crew.Crew(
            self.groups, user, hub=self.crewHub
        )
        widget.layout().addWidget(self.crew)

        userIds = []
        for user in self.users:
            userIds.append(user.getId())
            self.crew.addUser(
                user.getName(), user.getId()
            )

        user = ftrack.getUser(getpass.getuser())
        self.crewHub.populateUnreadConversations(user.getId(), userIds)

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

        widget.activateWindow()
        widget.show()
        widget.raise_()

        ftrack_connect.ui.theme.applyTheme(widget, 'integration')
        return widget

if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
