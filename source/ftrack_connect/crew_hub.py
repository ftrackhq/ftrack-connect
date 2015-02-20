# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import threading
import time
import uuid
import logging

import ftrack


class CrewHub(object):
    '''Class representing a crew hub.

    A CrewHub can be used to keep track of who else is active and working on the
    same or related tasks. The crew hub takes care of discovering others and
    sending/recieving heartbeats from them. The methods isInterested and
    onHeartbeat should be implemented to recieve information about anyone who is
    interesting.
    '''

    # The interval between heartbeats.
    HEARTBEAT_INTERVAL = 10

    def __init__(self, onPresence=None, onHeartbeat=None, onExit=None):
        '''Initialise crew hub.'''
        super(CrewHub, self).__init__()
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._subscriptions = {}
        self._callbacks = {
            'presence': onPresence,
            'exit': onExit,
            'heartbeat': onHeartbeat
        }

    def enter(self, data):
        '''Broadcast presence with *data* and start sending out heartbeats.'''
        self._myData = data
        data['session_id'] = uuid.uuid1().hex

        ftrack.EVENT_HUB.publish(
            ftrack.Event(
                topic='ftrack.presence_enter',
                data=self._myData
            ),
            onReply=self._onEnterReplyEvent
        )

        self._initiateHartbeats()

        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.presence_enter',
            self._onPresenceEvent
        )

    def _onEnterReplyEvent(self, event):
        '''Handle reply to enter event.'''
        if self.isInterested(event['data']):
            self._registerHeartbeatListener(event['data'])

    def _onPresenceEvent(self, event):
        '''Respond to presense event with my data.'''
        if self.isInterested(event['data']):
            self._registerHeartbeatListener(event['data'])

        return self._myData

    def isInterested(self, data):
        '''Return True if interested in *data*.'''
        return True

    def _registerHeartbeatListener(self, data):
        '''Register listener for heartbeat for *data*.'''
        subscription = ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.presence_heartbeat',
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

        if self._callbacks['presence'] is not None:
            self._callbacks['presence'](data)

    def _onHeartbeat(self, event):
        '''Increase subscription time for *event*.'''
        sessionId = event['data']['session_id']
        self._subscriptions[sessionId]['time'] = time.time()

        if self._callbacks['heartbeat'] is not None:
            self._callbacks['heartbeat'](event['data'])

    def _initiateHartbeats(self):
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
                topic='ftrack.presence_heartbeat',
                target='session_id={0}'.format(self._myData['session_id']),
                data=self._myData
            )
            ftrack.EVENT_HUB.publish(event)

            for key, value in self._subscriptions.items():
                if time.time() > value['time'] + self.HEARTBEAT_INTERVAL * 2 + 1:
                    ftrack.EVENT_HUB.unsubscribe(value['subscription'])

                    if self._callbacks['exit'] is not None:
                        self._callbacks['exit'](value['data'])

                    del self._subscriptions[key]

            time.sleep(self.HEARTBEAT_INTERVAL)

    def getSubscriptions(self):
        '''Return subscriptions and their data.'''
        return [
            subscription['data'] for subscription in self._subscriptions.values()
        ]
