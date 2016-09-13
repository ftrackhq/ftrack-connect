# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import threading
import time
import uuid
import datetime
import getpass
import collections
import logging

import arrow

import ftrack_connect.asynchronous

from QtExt import QtCore
import ftrack
import ftrack_api


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

    def __init__(self):
        '''Initialise crew hub.'''
        super(CrewHub, self).__init__()
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._subscriptions = {}
        self._session_id = uuid.uuid1().hex
        self._data = dict(session_id=self._session_id)
        self._last_activity = None

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
        data['activity'] = self._last_activity

        return data

    @property
    def sender(self):
        '''Return sender data.'''
        user = self.data['user']

        return {
            'name': user['name'],
            'id': user['id']
        }

    def enter(self, data=None):
        '''Broadcast presence with *data* and start sending out heartbeats.'''

        if not data:
            data = dict()

        self._data.update(data)

        # Set last activity when logging in the first time.
        # This will give the other user an indication on how long you've
        # been online.
        # TODO: Update this value when user is active in host application.
        self._last_activity = str(datetime.datetime.utcnow())

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
        self._initiateChatSubscription()

    def _initiateChatSubscription(self):
        '''Subscribe to chat message events.'''
        topic = 'topic=ftrack.chat.message and data.receiver={0}'.format(
            self.sender['id']
        )
        ftrack.EVENT_HUB.subscribe(
            topic,
            self._onChatMessage
        )

    def _onEnterReplyEvent(self, event):
        '''Handle reply to enter event.'''
        if self.isInterested(event['data']):
            self._registerHeartbeatListener(event['data'])

            self._onEnter(event['data'])

    def _onPresenceEvent(self, event):
        '''Respond to presense event with my data.'''
        if self.isInterested(event['data']):
            self._registerHeartbeatListener(event['data'])

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

                    self._onExit(value['data'])

                    del self._subscriptions[key]

            time.sleep(self.HEARTBEAT_INTERVAL)

    def _onChatMessage(self, event):
        '''Handle message events.'''
        pass

    def sendMessage(self, receiverId, text, conversationId=None):
        '''Send *text* to subscribers.'''
        data = dict(
            sender=self.sender,
            text=text,
            receiver=receiverId,
            conversation=conversationId,
            date=str(datetime.datetime.utcnow()),
            id=str(uuid.uuid1())
        )
        ftrack.EVENT_HUB.publish(
            ftrack.Event(
                topic='ftrack.chat.message',
                data=data
            )
        )

        return data

    def getSubscriptions(self):
        '''Return subscriptions and their data.'''
        return [
            subscription['data'] for subscription in self._subscriptions.values()
        ]

    def _onEnter(self, data):
        '''Handle on enter events.

            Override this method to implement custom logic for presence enter
            events.
        '''
        pass

    def _onExit(self, data):
        '''Handle on exit events.

            Override this method to implement custom logic for presence exit
            events.
        '''
        pass


class ConversationHub(CrewHub):
    '''Crew hub holding conversation state.'''

    def __init__(self, *args, **kwargs):
        '''Initialise hub.'''

        self._conversations = collections.defaultdict(list)
        self._session = ftrack_api.Session(
            auto_connect_event_hub=False
        )
        super(ConversationHub, self).__init__(*args, **kwargs)

    @property
    def compatibleServerVersion(self):
        '''Return True if server is compatible with conversations.'''
        return 'Conversation' in self._session.types

    def enter(self, *args, **kwargs):
        '''Enter hub.'''
        super(ConversationHub, self).enter(*args, **kwargs)

        subscriptionExpression = (
            'topic=ftrack.conversation.seen '
            'and source.user.username={0} '
            'and data.session_id!={1}'.format(
                getpass.getuser(), self._session_id
            )
        )

        ftrack.EVENT_HUB.subscribe(
            subscriptionExpression,
            self._onConversationSeen
        )

    def _onConversationSeen(self, event):
        '''Handle conversation seen events.

            Override this method to implement custom logic for conversation
            seen events.
        '''
        pass

    def _onConversationMessagesLoaded(self, conversationId, messages):
        '''Handle messages loaded for conversation.

            Override this method to implement custom logic for conversation
            messages loaded events.
        '''
        pass

    def _onConversationUpdated(self, conversationId):
        '''Handle conversation with *conversationId* updated.'''
        pass

    def _onChatMessage(self, event):
        '''Handle chat message event.'''
        self._conversations[
            event['data']['conversation']
        ].append(event['data'])

        self._onConversationUpdated(event['data']['conversation'])

    @ftrack_connect.asynchronous.asynchronous
    def loadMessages(self, conversationId):
        '''Asyncrounous load messages for *conversationId*.

        Will trigger `_onConversationMessagesLoaded` once loaded.

        '''
        messages = self._session.query(
            'select text, created_by.first_name, created_by.last_name, '
            'created_by_id, created_at from Message where '
            'conversation_id is "{0}"'.format(
                conversationId
            )
        ).all()

        self._onConversationMessagesLoaded(conversationId, messages)


    def getConversationUpdates(self, conversationId, clear=False):
        '''Return new messages for *conversationId*.

        Optional *clear* can be specified to remove messages once retrieved.

        '''

        messages = self._conversations[conversationId][:]

        if clear:
            self._conversations[conversationId] = []

        self.logger.debug(u'Return conversation updates for {0}\nMessages: {1}'.format(
            conversationId, messages
        ))
        return messages

    def getParticipants(self, conversationId):
        '''Return participants for conversation with *conversationId*.'''
        return self._session.query(
            'select resource_id from Participant where '
            'conversation_id is "{0}"'.format(
                conversationId
            )
        )

    def getConversation(self, userId, otherId):
        '''Return conversation for *userId* and *otherUserId*.

        Will get or create conversation for *userId* and user with
        *otherId*.

        '''
        self.logger.debug('Retrieving conversation for ("{0}", "{1}")'.format(
            userId, otherId
        ))

        conversation = self._session.query(
            'select id, participants.resource_id from Conversation '
            'where participants any (resource_id is "{user_id}") and '
            'participants any (resource_id is "{other_id}")'.format(
                user_id=userId, other_id=otherId
            )
        ).first()

        if not conversation:
            self.logger.debug('Conversation not found, creating new.')
            conversation = self._session.create('Conversation')
            conversation['participants'].append(
                self._session.create('Participant', {
                    'resource_id': userId,
                    'last_visit': datetime.datetime.now()
                })
            )
            conversation['participants'].append(
                self._session.create('Participant', {
                    'resource_id': otherId,
                    'last_visit': datetime.datetime.now()
                })
            )

        conversation.session.commit()

        return conversation

    def sendMessage(self, receiverId, text, conversationId):
        '''Send and persist new message.'''

        self._session.create('Message', {
            'text': text,
            'conversation_id': conversationId
        })
        self._session.commit()

        return super(ConversationHub, self).sendMessage(
            receiverId, text, conversationId=conversationId
        )

    @ftrack_connect.asynchronous.asynchronous
    def markConversationAsSeen(self, conversationId, resourceId):
        '''Asyncrounous mark conversations as seen.

        *conversationId* should be the id of the conversation and *participantId*
        the id of the participant in that conversation.

        '''
        participant = self._session.query(
            'select last_visit from Participant where resource_id is '
            '"{0}" and conversation_id is "{1}"'.format(
                resourceId, conversationId
            )
        ).first()

        self._conversations[conversationId] = []

        if participant:
            participant['last_visit'] = datetime.datetime.now()
            participant.session.commit()

            event = ftrack.Event(
                topic='ftrack.conversation.seen',
                data=dict(
                    conversation=conversationId,
                    user_id=resourceId,
                    session_id=self._session_id
                )
            )

            ftrack.EVENT_HUB.publish(event)
            self._onConversationSeen(event)

    @ftrack_connect.asynchronous.asynchronous
    def populateUnreadConversations(self, userId, otherIds=None):
        '''Populate count for conversations between *userId* and *otherIds*.'''
        if not otherIds:
            otherIds = []

        for _id in otherIds:
            participant = self._session.query(
                'select last_visit, conversation_id, resource_id from '
                'Participant where resource_id is "{0}" and '
                'conversation.participants any (resource_id is "{1}")'.format(
                    userId, _id
                )
            ).first()

            if not participant:
                continue

            messages = self._session.query(
                'select created_at, conversation_id, text, created_by.id, '
                'created_by.first_name, created_by.last_name from Message where '
                'conversation_id is "{0}" and created_at > "{1}" and '
                'created_by_id != "{2}"'.format(
                    participant['conversation_id'],
                    arrow.get(participant['last_visit']).naive.replace(
                        microsecond=0
                    ).isoformat(),
                    participant['resource_id']
                )
            ).all()

            for message in messages:
                self._conversations[message['conversation_id']].append(
                    dict(
                        text=message['text'],
                        sender=dict(
                            name=u'{0} {1}'.format(
                                message['created_by']['first_name'],
                                message['created_by']['last_name']
                            ),
                            id=message['created_by']['id']
                        ),
                        created_at=message['created_at']
                    )
                )

            if messages:
                self._onConversationUpdated(participant['conversation_id'])



class SignalConversationHub(ConversationHub, QtCore.QObject):
    '''Crew hub using Qt signals.'''

    #: Signal to emit on heartbeat.
    onHeartbeat = QtCore.Signal(object)

    #: Signal to emit on presence enter event.
    onEnter = QtCore.Signal(object)

    #: Signal to emit on presence exit event.
    onExit = QtCore.Signal(object)

    #: Signal to emit on conversations messagages loaded.
    onConversationMessagesLoaded = QtCore.Signal(object, object)

    #: Signal to emit on conversations messagages loaded.
    onConversationUpdated = QtCore.Signal(object)

    #: Signal to emit on conversation seen.
    onConversationSeen = QtCore.Signal(object)

    def _onHeartbeat(self, event):
        '''Increase subscription time for *event*.'''
        super(SignalConversationHub, self)._onHeartbeat(event)
        self.onHeartbeat.emit(event['data'])

    def _onEnter(self, data):
        '''Handle enter events.'''
        self.onEnter.emit(data)

    def _onExit(self, data):
        '''Handle exit events.'''
        self.onExit.emit(data)

    def _onConversationMessagesLoaded(self, conversationId, messages):
        '''Handle messages loaded for conversation.'''
        self.onConversationMessagesLoaded.emit(conversationId, messages)

    def _onConversationUpdated(self, conversationId):
        '''Handle conversation with *conversationId* updated.'''
        self.logger.debug('onConversationUpdated emitted for {0}'.format(
            conversationId
        ))
        self.onConversationUpdated.emit(conversationId)

    def _onConversationSeen(self, event):
        '''Handle conversation seen event.'''
        self.logger.debug('Handle conversation seen event: {0}'.format(
            event['data']
        ))

        self._conversations[event['data']['conversation']] = []
        self.onConversationSeen.emit(event['data'])
