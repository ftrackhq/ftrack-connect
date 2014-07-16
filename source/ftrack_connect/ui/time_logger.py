# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui

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

        self.timer = ftrack_connect.ui.widget.timer.Timer()
        layout.addWidget(self.timer)

        layout.addStretch(1)

    def getName(self):
        '''Return name of widget.'''
        return 'Log Time'
