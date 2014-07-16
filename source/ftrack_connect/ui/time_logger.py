# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

from PySide import QtGui, QtCore

import ftrack_connect.ui.application
import ftrack_connect.ui.widget.timer
import ftrack_connect.ui.widget.overlay
from ftrack_connect.ui.widget.time_log_list import TimeLogList as _TimeLogList


def register(connect):
    '''Register publish plugin to ftrack connect.'''
    timeLogger = TimeLogger()
    connect.addPlugin(timeLogger)

    # TEMP: Dev only.
    timeLogger.requestApplicationFocus.emit(timeLogger)


class TimerOverlay(ftrack_connect.ui.widget.overlay.Overlay):
    '''Overlay for timer widget.'''

    def __init__(self, parent):
        '''Initialise.'''
        super(TimerOverlay, self).__init__(parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        message = QtGui.QLabel('Select a task to activate timer.')
        message.setWordWrap(True)
        message.setAlignment(QtCore.Qt.AlignVCenter)
        layout.addWidget(message)

        self.setStyleSheet('''
            QFrame#overlay {
                border: 1px dashed #ddd;
                background-color:rgba(255, 255, 255, 200);
            }

            QFrame#overlay QLabel {
                background: transparent;
            }
        ''')


class TimeLogger(ftrack_connect.ui.application.ApplicationPlugin):
    '''Base widget for ftrack connect time logger plugin.'''

    def __init__(self, *args, **kwargs):
        '''Instantiate the time logger.'''
        super(TimeLogger, self).__init__(*args, **kwargs)
        self.setObjectName('timeLogger')

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self.activeLabel = QtGui.QLabel('Currently running')
        self.activeLabel.setProperty('title', True)
        layout.addWidget(self.activeLabel)

        self._timerEnabled = False
        self.timer = ftrack_connect.ui.widget.timer.Timer()
        layout.addWidget(self.timer)

        self.timerPlaceholder = TimerOverlay(self.timer)

        self.assignedTimeLogList = _TimeLogList(title='Assigned')
        layout.addWidget(self.assignedTimeLogList, stretch=1)

        self._updateAssignedList()

    def _updateAssignedList(self):
        '''Update assigned list.'''
        self.assignedTimeLogList.clearItems()

        # Local import to allow configuring of ftrack API at runtime.
        import ftrack

        # TODO: Get logged in user from ftrack API.
        username = os.environ.get('LOGNAME')
        if not username:
            return

        assignedTasks = ftrack.User(
            os.environ.get('LOGNAME')
        ).getTasks(
            states=['IN_PROGRESS', 'BLOCKED']
        )

        for task in assignedTasks:
            self.assignedTimeLogList.addItem({
                'title': task.getName(),
                'description': self._getPath(task),
                'data': task
            })

    def _getPath(self, entity):
        '''Return path to *entity*.'''
        parents = entity.getParents()
        parents.reverse()

        path = [parent.getName() for parent in parents]
        return ' / '.join(path)

    def getName(self):
        '''Return name of widget.'''
        return 'Log Time'

    def enableTimer(self):
        '''Enable the timer widget.'''
        self._timerEnabled = True
        self.timerPlaceholder.setHidden(True)

    def disableTimer(self):
        '''Disable the timer widget.'''
        self._timerEnabled = False
        self.timerPlaceholder.setHidden(False)

    def toggleTimer(self):
        '''Toggle whether timer is enabled or not.'''
        if self._timerEnabled:
            self.disableTimer()
        else:
            self.enableTimer()
