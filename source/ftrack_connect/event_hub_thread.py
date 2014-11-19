# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtCore


class EventHubThread(QtCore.QThread):
    '''Listen for events from ftrack's event hub.'''

    def run(self):
        '''Listen for events.'''
        # Deferred import to allow server configuration to be set in UI.
        import ftrack

        ftrack.EVENT_HUB.wait()
