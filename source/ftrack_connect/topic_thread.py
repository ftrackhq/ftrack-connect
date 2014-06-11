# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

from PySide import QtCore
import ftrack

ftrack.setup()


class TopicThread(QtCore.QThread):
    '''Thread to subscribe to ftrack topics hub.'''
    ftrackConnectEvent = QtCore.Signal(object)

    def _callback(self, topic, _meta_, data):
        '''Generic callback for all ftrack.connect events.

        .. note::
            Events not triggered by the current logged in user will be dropped.

        '''
        # Drop all events triggered by other users.
        if not _meta_.get('userId') == self._currentUserId:
            return

        self.ftrackConnectEvent.emit(data)

    def run(self):
        '''Subscribe to ftrack.connect events and run the thread.'''

        currentUser = ftrack.User(
            os.environ['LOGNAME']
        )

        self._currentUserId = currentUser.getId()

        ftrack.TOPICS.subscribe('ftrack.connect', self._callback)
        ftrack.TOPICS.wait()
