# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import getpass

from PySide import QtCore
import ftrack


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

        # getpass.getuser is used to reflect how the ftrack api get the current
        # user.
        currentUser = ftrack.User(
            getpass.getuser()
        )

        self._currentUserId = currentUser.getId()

        ftrack.TOPICS.subscribe('ftrack.connect', self._callback)
        ftrack.TOPICS.wait()
