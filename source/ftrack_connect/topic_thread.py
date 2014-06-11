# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtCore
import ftrack

ftrack.setup()


class TopicThread(QtCore.QThread):
    '''Thread to subscribe to ftrack topics hub.'''
    ftrackConnectEvent = QtCore.Signal(object)

    def _callback(self, topic, **data):
        '''Generic callback for all ftrack.connect events.'''
        self.ftrackConnectEvent.emit(
            data.get('data', {})
        )

    def run(self):
        '''Subscribe to ftrack.connect events and run the thread.'''
        ftrack.TOPICS.subscribe('ftrack.connect', self._callback)
        ftrack.TOPICS.wait()
