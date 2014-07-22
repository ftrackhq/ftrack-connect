# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import operator

from PySide import QtGui, QtCore

import ftrack_connect.ui.application
import ftrack_connect.ui.widget.timer
import ftrack_connect.ui.widget.overlay
from ftrack_connect.ui.widget.time_log_list import TimeLogList as _TimeLogList


def register(connect):
    '''Register publish plugin to ftrack connect.'''
    timeLogger = TimeLogger()
    connect.addPlugin(timeLogger)


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

        # TODO: See if there is a way to stop Sass converting the rgba string
        # to the wrong value.
        self.setStyleSheet('''
            #ftrack-connect-window TimerOverlay {
                background-color: rgba(255, 255, 255, 200);
            }
        ''')


class TimeLogger(ftrack_connect.ui.application.ApplicationPlugin):
    '''Base widget for ftrack connect time logger plugin.'''

    def __init__(self, *args, **kwargs):
        '''Instantiate the time logger.'''
        super(TimeLogger, self).__init__(*args, **kwargs)
        self.setObjectName('timeLogger')

        self._activeEntity = None

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self.activeLabel = QtGui.QLabel('Currently running')
        self.activeLabel.setProperty('title', True)
        layout.addWidget(self.activeLabel)

        self._timerEnabled = False
        self.timer = ftrack_connect.ui.widget.timer.Timer()
        layout.addWidget(self.timer)

        self.timerPlaceholder = TimerOverlay(self.timer)

        # TODO: Add theme support.
        reloadIcon = QtGui.QIcon(
            QtGui.QPixmap(':/ftrack/image/light/reload')
        )

        assignedTimeLogUpdateButton = QtGui.QPushButton(reloadIcon, '')
        assignedTimeLogUpdateButton.setFlat(True)
        assignedTimeLogUpdateButton.setToolTip('Refresh list')
        assignedTimeLogUpdateButton.clicked.connect(self._updateAssignedList)

        self.assignedTimeLogList = _TimeLogList(
            title='Assigned', headerWidgets=[assignedTimeLogUpdateButton]
        )
        layout.addWidget(self.assignedTimeLogList, stretch=1)

        # Connect events.
        self.timer.stopped.connect(self._onCommitTime)
        self.timer.timeEdited.connect(self._onCommitTime)

        self.assignedTimeLogList.itemSelected.connect(
            self._onSelectTimeLog
        )

        self._updateAssignedList()

    def _updateAssignedList(self):
        '''Update assigned list.'''
        self.assignedTimeLogList.clearItems()

        # Local import to allow configuring of ftrack API at runtime.
        import ftrack

        # TODO: Get logged in user from ftrack API.
        # NOTE: The specific environment variable is used as it is explicitly
        # set post login by the application.
        username = os.environ.get('LOGNAME')
        if not username:
            return

        assignedTasks = ftrack.User(username).getTasks(
            states=['NOT_STARTED', 'IN_PROGRESS', 'BLOCKED']
        )

        formattedTasks = [dict({
            'title': task.getName(),
            'description': self._getPath(task),
            'data': task
        }) for task in assignedTasks]

        formattedTasks = sorted(
            formattedTasks, key=operator.itemgetter('description', 'title')
        )

        for task in formattedTasks:
            self.assignedTimeLogList.addItem(task)

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

    def _onSelectTimeLog(self, timeLog):
        '''Handle time log selection.'''
        if timeLog:
            entity = timeLog.data()
            if entity == self._activeEntity:
                return

            # Stop current timer to ensure value persisted.
            if self.timer.state() is not self.timer.STOPPED:
                self.timer.stop()

            # TODO: Store on Timer as data.
            self._activeEntity = entity

            if self._activeEntity:
                loggedHoursToday = 0
                timeReport = self._activeEntity.getLoggedHours()
                if timeReport is not None:
                    loggedHoursToday = timeReport.getHours()

                timeInSeconds = loggedHoursToday * 60.0 * 60.0

                self.timer.setValue({
                    'title': timeLog.title(),
                    'description': timeLog.description(),
                    'time': timeInSeconds
                })
                self.enableTimer()
                self.timer.start()
            else:
                self.disableTimer()
        else:
            self.disableTimer()

    def _onCommitTime(self, time):
        '''Commit *time* value to backend..'''
        if self._activeEntity:
            timeInHours = time / 60.0 / 60.0
            self._activeEntity.setLoggedHours(timeInHours)
