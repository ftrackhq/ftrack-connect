# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import time as _time

from PySide import QtGui, QtCore

import ftrack_connect.ui.widget.line_edit
import ftrack_connect.ui.widget.label


class Timer(QtGui.QWidget):
    '''Timer for logging time.'''

    def __init__(self, title=None, description=None, time=0, parent=None):
        '''Initialise widget with initial component *value* and *parent*.'''
        super(Timer, self).__init__(parent=parent)
        self._timer = None
        self._tick = None
        self._elapsed = 0

        self.setLayout(QtGui.QVBoxLayout())

        self.titleLabel = ftrack_connect.ui.widget.label.Label()
        self.layout().addWidget(self.titleLabel)

        self.descriptionLabel = ftrack_connect.ui.widget.label.Label()
        self.layout().addWidget(self.descriptionLabel)

        self.timeField = ftrack_connect.ui.widget.line_edit.LineEdit()
        self.timeField.setDisabled(True)
        self.layout().addWidget(self.timeField)

        self.toggleButton = QtGui.QPushButton('Start')
        self.layout().addWidget(self.toggleButton)

        self.setSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed
        )

        # Connect events.
        self.toggleButton.clicked.connect(self.toggle)

        # Set initial values.
        self.setValue({
            'title': title,
            'description': description,
            'time': time
        })

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
            self._timer = self.startTimer(500)

            self.toggleButton.setText('Stop')

    def stop(self):
        '''Stop the timer.'''
        if self.isRunning():
            self.killTimer(self._timer)
            self._timer = None

            self.timerEvent(QtCore.QTimerEvent(0))
            self._tick = None

            self.toggleButton.setText('Start')

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
        '''Reset timer.'''
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
        self.timeField.setText(str(self._elapsed))
