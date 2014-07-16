# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import time as _time
import math

from PySide import QtGui, QtCore

import ftrack_connect.ui.widget.line_edit
import ftrack_connect.ui.widget.label


class Timer(QtGui.QFrame):
    '''Timer for logging time.'''

    def __init__(self, title=None, description=None, time=0, parent=None):
        '''Initialise timer.

        *title* should be the title entry to display for the time log whilst
        *description* can provide an optional longer description.

        *time* should be the initial value to set elapsed time to.

        *parent* should be the optional parent of this widget.

        '''
        super(Timer, self).__init__(parent=parent)
        self.setObjectName('timer')

        self._timer = None
        self._tick = None
        self._elapsed = 0

        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        self.labelLayout = QtGui.QVBoxLayout()
        layout.addLayout(self.labelLayout, stretch=1)

        self.titleLabel = ftrack_connect.ui.widget.label.Label()
        self.titleLabel.setObjectName('title')
        self.labelLayout.addWidget(self.titleLabel)

        self.descriptionLabel = ftrack_connect.ui.widget.label.Label()
        self.labelLayout.addWidget(self.descriptionLabel)

        self.timeField = ftrack_connect.ui.widget.line_edit.LineEdit()
        self.timeField.setObjectName('timeField')
        self.timeField.setDisabled(True)
        self.timeField.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.timeField)

        self.toggleButton = QtGui.QPushButton('Start')
        self.toggleButton.setObjectName('primary')
        self.toggleButton.setProperty('mode', 'start')

        layout.addWidget(self.toggleButton)

        self.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed
        )

        # Connect events.
        self.toggleButton.clicked.connect(self.toggle)

        # Set initial values.
        self.setValue({
            'title': title,
            'description': description,
            'time': time
        })

    def _updateState(self):
        '''Update internal state and force style refresh.'''
        if self.isRunning():
            self.toggleButton.setText('Stop')
            self.toggleButton.setProperty('mode', 'stop')
        else:
            self.toggleButton.setText('Start')
            self.toggleButton.setProperty('mode', 'start')

        # Force re-evaluation of dynamic stylesheet values based on new
        # properties.
        self.toggleButton.style().unpolish(self.toggleButton)
        self.toggleButton.style().polish(self.toggleButton)
        self.toggleButton.update()

    def timerEvent(self, event):
        '''Handle timer *event*.'''
        if self._tick is not None:
            now = _time.time()
            self.setTime(
                self._elapsed + (now - self._tick)
            )
            self._tick = now

    def start(self):
        '''Start the timer.'''
        if not self.isRunning():
            self._tick = _time.time()
            self._timer = self.startTimer(50)
            self._updateState()

    def stop(self):
        '''Stop the timer.'''
        if self.isRunning():
            self.killTimer(self._timer)
            self._timer = None

            self.timerEvent(QtCore.QTimerEvent(0))
            self._tick = None

            self._updateState()

    def isRunning(self):
        '''Return whether timer is currently running.'''
        return self._timer is not None

    def toggle(self):
        '''Toggle the timer state.'''
        if self.isRunning():
            self.stop()
        else:
            self.start()

    def reset(self):
        '''Reset timer and elapsed time.'''
        self.stop()
        self._elapsed = 0

    def clear(self):
        '''Clear all values.'''
        self.setValue({})

    def value(self):
        '''Return dictionary with component data.'''
        return {
            'title': self.title(),
            'description': self.description(),
            'time': self.time()
        }

    def setValue(self, value):
        '''Set all attributes from *value*.'''
        self.setTitle(value.get('title', None))
        self.setDescription(value.get('description', None))
        self.setTime(value.get('time', None))

    def title(self):
        '''Return title.'''
        return self.titleLabel.text()

    def setTitle(self, title):
        '''Set *title*.'''
        self.titleLabel.setText(title)

    def description(self):
        '''Return description.'''
        return self.descriptionLabel.text()

    def setDescription(self, description):
        '''Set *description*.'''
        self.descriptionLabel.setText(description)

    def time(self):
        '''Return time elapsed.'''
        return self._elapsed

    def setTime(self, time):
        '''Set *time* elapsed.'''
        self._elapsed = time
        hours, remainder = divmod(time, 3600)
        minutes, seconds = divmod(remainder, 60)

        hours = int(hours)
        minutes = int(minutes)
        seconds = int(math.ceil(seconds))

        if seconds == 60:
            minutes += 1
            seconds = 0

        if minutes == 60:
            hours += 1
            minutes = 0

        if not hours and not minutes:
            text = '{0} sec'.format(seconds)
        elif not hours:
            text = '{0:02d}:{1:02d} min'.format(minutes, seconds)
        else:
            text = '{0:02d}:{1:02d}:{2:02d}'.format(hours, minutes, seconds)

        self.timeField.setText(text)
