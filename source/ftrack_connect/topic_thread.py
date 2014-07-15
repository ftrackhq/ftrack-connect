# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import getpass

from PySide import QtCore
import ftrack


class TopicThread(QtCore.QThread):
    '''Thread to subscribe to ftrack topics hub.

    The topic thread subscribes to all "ftrack.connect" events and emits a
    signal with the event data.

    .. code-block:: python

        def _onFtrackConnectEvent(data):
            # Do something with data

        thread = TopicThread()
        thread.ftrackConnectEvent.connect(_onFtrackConnectEvent)

    '''

    def run(self):
        '''Run the topic thread.'''
        ftrack.TOPICS.wait()
