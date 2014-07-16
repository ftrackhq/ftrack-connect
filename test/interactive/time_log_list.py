# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack
import os

from PySide import QtGui
import ftrack

import ftrack_connect.ui.widget.time_log_list
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        allAssignedTasks = ftrack.User(
            os.environ.get('LOGNAME')
        ).getTasks(
            states=['IN_PROGRESS', 'BLOCKED']
        )

        assignedTasksList = ftrack_connect.ui.widget.time_log_list.TimeLogList(
            title='Assigned tasks'
        )

        layout.addWidget(assignedTasksList, stretch=1)

        for task in allAssignedTasks:
            assignedTasksList.addItem({
                'link': task
            })

        divider = QtGui.QFrame()
        divider.setFrameShape(QtGui.QFrame.HLine)
        layout.addWidget(divider)

        self.selectedTasklabel = QtGui.QLabel()
        assignedTasksList.itemSelected.connect(self._setLabelText)

        layout.addWidget(self.selectedTasklabel)

        return widget

    def _setLabelText(self, task):
        self.selectedTasklabel.setText(
            task.title()
        )
if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
