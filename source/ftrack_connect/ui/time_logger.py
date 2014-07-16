# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import ftrack_connect.ui.application


def register(connect):
    '''Register publish plugin to ftrack connect.'''
    timeLogger = TimeLogger()
    connect.addPlugin(timeLogger)


class TimeLogger(ftrack_connect.ui.application.ApplicationPlugin):
    '''Base widget for ftrack connect time logger plugin.'''

    def __init__(self, *args, **kwargs):
        '''Instantiate the time logger.'''
        super(TimeLogger, self).__init__(*args, **kwargs)

    def getName(self):
        '''Return name of widget.'''
        return 'Log Time'
