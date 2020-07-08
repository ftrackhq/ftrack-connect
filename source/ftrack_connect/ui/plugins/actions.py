# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from Qt import QtWidgets, QtCore

import ftrack_connect.ui.application
import ftrack_connect.ui.widget.overlay
import ftrack_connect.ui.widget.actions


def register(connect):
    '''Register actions plugin to ftrack connect.'''
    actions = Actions()
    connect.addPlugin(actions, actions.getName())


class Actions(ftrack_connect.ui.application.ApplicationPlugin):
    '''Base widget for ftrack connect actions plugin.'''

    def __init__(self, parent=None):
        '''Instantiate the actions widget.'''
        super(Actions, self).__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.actionsView = ftrack_connect.ui.widget.actions.Actions()
        layout.addWidget(self.actionsView)
