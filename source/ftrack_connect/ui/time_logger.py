# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore

import ftrack_connect.ui.application
import ftrack_connect.ui.widget.timer


def register(connect):
    '''Register publish plugin to ftrack connect.'''
    timeLogger = TimeLogger()
    connect.addPlugin(timeLogger)

    # TEMP: Dev only.
    timeLogger.requestApplicationFocus.emit(timeLogger)


class TimeLogger(ftrack_connect.ui.application.ApplicationPlugin):
    '''Base widget for ftrack connect time logger plugin.'''

    def __init__(self, *args, **kwargs):
        '''Instantiate the time logger.'''
        super(TimeLogger, self).__init__(*args, **kwargs)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        self._timerVisible = True
        self.timer = ftrack_connect.ui.widget.timer.Timer()
        layout.addWidget(self.timer)

        layout.addStretch(1)

    def getName(self):
        '''Return name of widget.'''
        return 'Log Time'

    def showTimer(self):
        '''Show the timer widget.'''
        self._timerVisible = True

        startGeometry = QtCore.QRect(self.timer.geometry())
        endGeometry = QtCore.QRect(
            startGeometry.x(), 0,
            startGeometry.width(), startGeometry.height()
        )
        self._animateTimer(startGeometry, endGeometry)

    def hideTimer(self):
        '''Hide the timer widget.'''
        self._timerVisible = False

        startGeometry = QtCore.QRect(self.timer.geometry())
        endGeometry = QtCore.QRect(
            startGeometry.x(), -startGeometry.height(),
            startGeometry.width(), startGeometry.height()
        )
        self._animateTimer(startGeometry, endGeometry)

    def toggleTimer(self):
        '''Toggle whether timer is hidden or not.'''
        if self._timerVisible:
            self.hideTimer()
        else:
            self.showTimer()

    def _animateTimer(self, startGeometry, endGeometry):
        '''Animate the timer.'''
        self._timerAnimation = QtCore.QPropertyAnimation(self.timer, 'geometry')
        self._timerAnimation.setDuration(200)
        self._timerAnimation.setStartValue(startGeometry)
        self._timerAnimation.setEndValue(endGeometry)
        self._timerAnimation.start()
