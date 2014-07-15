# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore


def register(connect):
    '''Register publish plugin to ftrack connect.'''
    timeLogger = TimeLogger()
    connect.add(timeLogger)


class TimeLogger(QtGui.QWidget):
    '''Base widget for ftrack connect time logger plugin.'''

    requestFocus = QtCore.Signal(object)
    requestClose = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        '''Instantiate the time logger.'''
        super(TimeLogger, self).__init__(*args, **kwargs)

    def getName(self):
        '''Return name of widget.'''
        return 'Log Time'
