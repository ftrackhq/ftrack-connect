# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtCore
import ftrack


class EventHubThread(QtCore.QThread):
    '''Listen for events from ftrack's event hub.'''

    def run(self):
        '''Listen for events.'''
        ftrack.EVENT_HUB.wait()
