# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import threading
import time
import uuid
import logging
import datetime
import getpass

from PySide import QtCore
import ftrack


class CrewHub(object):
    '''Class representing a crew hub.

    A CrewHub can be used to keep track of who else is active and working on
    the same or related tasks. The crew hub takes care of discovering others
    and sending/recieving heartbeats from them. The methods isInterested and
    onHeartbeat should be implemented to recieve information about anyone who
    is interesting.

    '''

    # The interval between heartbeats.
    HEARTBEAT_INTERVAL = 10

    # Timeout for pruning inactive users.
    PRUNE_TIMEOUT = HEARTBEAT_INTERVAL * 2 + 1

    def __init__(self, onPresence=None, onHeartbeat=None, onExit=None):
        '''Initialise crew hub.'''
        super(CrewHub, self).__init__()
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._subscriptions = {}
        self._data = dict(session_id=uuid.uuid1().hex)

    @property
    def data(self):
        '''Data for my crew hub and should be of the following structure.

        {
            user=dict(
                id
                name
                thumbnail
            ),
            application=dict(
                identifier
                label
                activity
            ),
            context=dict(
                containers
                project_id
            ),
            session_id=<uuid.uui1.hex>
            timestamp=<datetime>
        }

        '''
        data = self._data.copy()

        data['timestamp'] = str(datetime.datetime.utcnow())

        return data

    def enter(self, data=None):
        '''Broadcast presence with *data* and start sending out heartbeats.'''

        if not data:
            data = dict()

        self._data.update(data)

        subscriptionExpression = (
            'topic=ftrack.crew.presence-enter '
            'and source.user.username != {0}'.format(
                getpass.getuser()
            )
        )

        ftrack.EVENT_HUB.subscribe(
            subscriptionExpression,
            self._onPresenceEvent
        )

        ftrack.EVENT_HUB.publish(
            ftrack.Event(
                topic='ftrack.crew.presence-enter',
                data=self.data
            ),
            onReply=self._onEnterReplyEvent
        )

        self._initiateHeartbeats()

    def _onEnterReplyEvent(self, event):
        '''Handle reply to enter event.'''
        if self.isInterested(event['data']):
            self._registerHeartbeatListener(event['data'])

            if hasattr(self, '_onEnter'):
                self._onEnter(event['data'])

    def _onPresenceEvent(self, event):
        '''Respond to presense event with my data.'''
        if self.isInterested(event['data']):
            self._registerHeartbeatListener(event['data'])

            if hasattr(self, '_onEnter'):
                self._onEnter(event['data'])

        return self.data

    def isInterested(self, data):
        '''Return True if interested in *data*.'''
        raise NotImplementedError()

    def _registerHeartbeatListener(self, data):
        '''Register listener for heartbeat for *data*.'''
        subscription = ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.crew.presence-heartbeat',
            self._onHeartbeat,
            subscriber={
                'session_id': data['session_id']
            }
        )

        self._subscriptions[data['session_id']] = {
            'data': data,
            'subscription': subscription,
            'time': time.time()
        }

    def _onHeartbeat(self, event):
        '''Increase subscription time for *event*.'''
        sessionId = event['data']['session_id']
        self._subscriptions[sessionId]['time'] = time.time()

    def _initiateHeartbeats(self):
        '''Initiate heartbeats.'''
        self.heartbeatThread = threading.Thread(
            target=self._sendHeartbeat
        )
        self.heartbeatThread.daemon = True
        self.heartbeatThread.start()

    def _sendHeartbeat(self):
        '''Send out heartbeats every 30 seconds.'''
        while True:

            event = ftrack.Event(
                topic='ftrack.crew.presence-heartbeat',
                target='session_id={0}'.format(self._data['session_id']),
                data=self.data
            )

            ftrack.EVENT_HUB.publish(event)

            for key, value in self._subscriptions.items():
                if time.time() > value['time'] + self.PRUNE_TIMEOUT:
                    ftrack.EVENT_HUB.unsubscribe(value['subscription'])

                    if hasattr(self, '_onExit'):
                        self._onExit(value['data'])

                    del self._subscriptions[key]

            time.sleep(self.HEARTBEAT_INTERVAL)

    def getSubscriptions(self):
        '''Return subscriptions and their data.'''
        return [
            subscription['data'] for subscription in self._subscriptions.values()
        ]


class SignalCrewHub(CrewHub, QtCore.QObject):
    '''Crew hub using Qt signals.'''

    #: Signal to emit on heartbeat.
    onHeartbeat = QtCore.Signal(object)

    #: Signal to emit on presence enter event.
    onEnter = QtCore.Signal(object)

    #: Signal to emit on presence exit event.
    onExit = QtCore.Signal(object)

    def _onHeartbeat(self, event):
        '''Increase subscription time for *event*.'''
        super(SignalCrewHub, self)._onHeartbeat(event)
        self.onHeartbeat.emit(event['data'])

    def _onEnter(self, data):
        '''Handle enter events.'''
        self.onEnter.emit(data)

    def _onExit(self, data):
        '''Handle exit events.'''
        self.onExit.emit(data)
