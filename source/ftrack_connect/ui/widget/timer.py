# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import time as _time
import math

from PySide import QtGui, QtCore

import ftrack_connect.ui.widget.line_edit
import ftrack_connect.ui.widget.label
import ftrack_connect.error


class Timer(QtGui.QFrame):
    '''Timer for logging time.'''

    #: Signal when timer started passing elapsed time.
    started = QtCore.Signal(object)

    #: Signal when timer stopped passing elapsed time.
    stopped = QtCore.Signal(object)

    #: Signal when timer paused passing elapsed time.
    paused = QtCore.Signal(object)

    #: Signal when timer resumed passing elapsed time.
    resumed = QtCore.Signal(object)

    #: Timer stopped state.
    STOPPED = 'STOPPED'

    #: Timer paused state.
    PAUSED = 'PAUSED'

    #: Time running state.
    RUNNING = 'RUNNING'

    def __init__(self, title=None, description=None, time=0, parent=None):
        '''Initialise timer.

        *title* should be the title entry to display for the time log whilst
        *description* can provide an optional longer description.

        *time* should be the initial value to set elapsed time to.

        *parent* should be the optional parent of this widget.

        '''
        super(Timer, self).__init__(parent=parent)
        self.setObjectName('timer')

        self._state = self.STOPPED
        self._timer = None
        self._tick = None
        self._tickInterval = 50
        self._elapsed = 0

        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        self.labelLayout = QtGui.QVBoxLayout()
        layout.addLayout(self.labelLayout, stretch=1)

        self.titleLabel = ftrack_connect.ui.widget.label.Label()
        self.titleLabel.setProperty('title', True)
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

    def _updateInterface(self):
        '''Update interface to reflect current state and force style refresh.'''
        state = self.state()
        if state is self.RUNNING:
            self.toggleButton.setText('Stop')
            self.toggleButton.setProperty('mode', 'stop')
        elif state is self.STOPPED:
            self.toggleButton.setText('Start')
            self.toggleButton.setProperty('mode', 'start')

        # Force re-evaluation of dynamic stylesheet values based on new
        # properties.
        self.toggleButton.style().unpolish(self.toggleButton)
        self.toggleButton.style().polish(self.toggleButton)
        self.toggleButton.update()

    def _startTimer(self):
        '''Start internal timer.'''
        self._tick = _time.time()
        self._timer = self.startTimer(self._tickInterval)

    def _stopTimer(self):
        '''Stop internal timer.'''
        if self._timer is not None:
            self.killTimer(self._timer)

        self._timer = None
        self._tick = None

    def timerEvent(self, event):
        '''Handle timer *event*.'''
        if self._tick is not None:
            now = _time.time()
            self.setTime(
                self._elapsed + (now - self._tick)
            )
            self._tick = now

    def start(self):
        '''Start the timer.

        Raise :exc:`ftrack_connect.error.InvalidState` if timer is not currently
        stopped.

        '''
        state = self.state()
        if state is not self.STOPPED:
            raise ftrack_connect.error.InvalidState(
                'Cannot start timer in {0} state.'.format(state)
            )

        self._startTimer()
        self._state = self.RUNNING
        self.started.emit(self.time())

        self._updateInterface()

    def stop(self):
        '''Stop the timer.

        Raise :exc:`ftrack_connect.error.InvalidState` if timer is already
        stopped.

        '''
        state = self.state()
        if state is self.STOPPED:
            raise ftrack_connect.error.InvalidState(
                'Cannot stop timer in {0} state.'.format(state)
            )

        if state is not self.PAUSED:
            # Ensure correct time recorded. Note: Not done when transitioning
            # from PAUSED to STOPPED as time entered in PAUSED state should be
            # taken as is.
            self.timerEvent(QtCore.QTimerEvent(0))

        self._stopTimer()
        self._state = self.STOPPED
        self.stopped.emit(self.time())

        self._updateInterface()

    def pause(self):
        '''Pause the timer without updating state.

        Raise :exc:`ftrack_connect.error.InvalidState` if timer is not running.

        '''
        state = self.state()
        if state is not self.RUNNING:
            raise ftrack_connect.error.InvalidState(
                'Cannot pause timer in {0} state.'.format(state)
            )

        self._stopTimer()
        self._state = self.PAUSED
        self.paused.emit(self.time())

    def resume(self):
        '''Resume a paused timer without updating state.

        Raise :exc:`ftrack_connect.error.InvalidState` if timer is not paused.

        '''
        state = self.state()
        if state is not self.PAUSED:
            raise ftrack_connect.error.InvalidState(
                'Cannot resume timer in {0} state.'.format(state)
            )

        self._startTimer()
        self._state = self.RUNNING
        self.resumed.emit(self.time())

    def state(self):
        '''Return current state of timer.

        Possible states are:

            * :attr:`STOPPED`
            * :attr:`PAUSED`
            * :attr:`RUNNING`

        .. note::

            State can only be changed using the provided control methods (
            :meth:`start`, :meth:`stop`, :meth:`pause`, :meth:`resume`.

        '''
        return self._state

    def toggle(self):
        '''Toggle the timer state between stopped and started.

        .. note::

            If timer is paused will transition to stopped state.

        '''
        state = self.state()
        if state is self.STOPPED:
            self.start()
        else:
            self.stop()

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
        self.setTime(value.get('time', 0))

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
        '''Return time elapsed in seconds.'''
        return self._elapsed

    def setTime(self, time):
        '''Set *time* elapsed in seconds.'''
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
