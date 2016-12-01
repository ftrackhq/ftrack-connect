# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from QtExt import QtCore


class EventHubThread(QtCore.QThread):
    '''Listen for events from ftrack's event hub.'''

    def run(self):
        '''Listen for events.'''
        # Deferred import to allow server configuration to be set in UI.
        import ftrack

        ftrack.EVENT_HUB.wait()


class NewApiEventHubThread(QtCore.QThread):
    '''Listen for events from ftrack's event hub.'''

    def start(self, session):
        '''Start thread for *session*.'''
        self._session = session
        super(NewApiEventHubThread, self).start()

    def run(self):
        '''Listen for events.'''
        self._session.event_hub.wait()
