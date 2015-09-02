# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import logging
import datetime
import operator

from PySide import QtGui
import ftrack_api

import ftrack_connect.ui.widget.label
import ftrack_connect.ui.widget.user_list
import ftrack_connect.ui.widget.user
import ftrack_connect.ui.widget.chat
import ftrack_connect.error


logger = logging.getLogger(__name__)
_session = ftrack_api.Session()


def defaultClassifier(userId):
    '''Default user classifier.'''
    return 'others'


class Crew(QtGui.QWidget):
    '''User presence widget.'''

    def __init__(
            self, groups, user, hub=None, classifier=None, parent=None
    ):
        '''Instantiate widget with and *groups* and *userId*.

        If *hub* is configured the Crew widget will connect listeners for::

            *onEnter*: enter event.
            *onHeartbeat*: hearbeat event.
            *onExit*: exit event.

        '''
        super(Crew, self).__init__(parent)

        self.setObjectName('crew')
        self.setContentsMargins(0, 0, 0, 0)

        self.user = user
        self.conversationUserId = None
        self.currentConversation = None

        self.hub = hub

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        # If not classifier is specified return default `other` group.
        if not classifier:
            classifier = defaultClassifier

        self._classifier = classifier

        # Setup signal handlers if hub is configured.
        if hub:
            hub.onEnter.connect(self.onEnter)
            hub.onHeartbeat.connect(self.onHeartbeat)
            hub.onExit.connect(self.onExit)

        groups = [group.lower() for group in groups]

        if 'others' not in groups:
            groups.append('others')

        if 'offline' not in groups:
            groups.append('offline')

        self._groups = groups

        self.userList = ftrack_connect.ui.widget.user_list.UserList(
            groups=self._groups
        )

        self.userContainer = QtGui.QFrame()
        self.userContainer.setObjectName('user-container')
        self.userContainer.setLayout(QtGui.QVBoxLayout())
        self.userContainer.layout().setContentsMargins(0, 0, 0, 0)

        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self._extendedUser = None
        self.chat = ftrack_connect.ui.widget.chat.Chat()
        self.chat.chatMessageSubmitted.connect(self.onChatMessageSubmitClicked)

        self.userContainer.layout().addWidget(
            self.chat, stretch=1
        )

        self.layout().addWidget(
            self.userList, stretch=1
        )
        self.layout().addWidget(
            self.userContainer, stretch=3
        )

        self.userContainer.hide()

        self.userList.setMinimumWidth(180)
        self.userList.itemClicked.connect(self.onConversationSelected)

        # Setup signal handlers if hub is configured.
        if hub:
            hub.onEnter.connect(self.onEnter)
            hub.onHeartbeat.connect(self.onHeartbeat)
            hub.onExit.connect(self.onExit)
            hub.onMessageReceived.connect(self.onMessageReceived)

    def classifyOnlineUsers(self):
        '''Classify all online users and move them to correct group.'''
        users = self.userList.users()

        for user in users:
            group = self._classifier(user._userId)
            if group != user.group and user.online:
                user.group = group

                self.userList.updatePosition(user)

    def addUser(self, name, userId, group='offline'):
        '''Add user with *name*, *userId* and *group*.'''
        self.logger.debug(u'Adding user to user list: {0}'.format(name))
        if self.userList.userExists(userId):
            self.logger.debug(
                u'User with id {0} already exists'.format(userId)
            )
            return False

        self.userList.addUser({
            'name': name,
            'userId': userId,
            'group': group
        })

        return True

    def onEnter(self, data):
        '''Handle enter events with *data*.

        Structure of a data
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
            session_id=<uuid>
            timestamp=<datetime>
        }
        '''
        if not self.userList.userExists(data['user']['id']):
            self.userList.addUser({
                'name': data['user']['name'],
                'userId': data['user']['id'],
                'group': 'offline'
            })

        user = self.userList.getUser(data['user']['id'])

        group = self._classifier(user._userId)
        user.group = group

        user.addSession(data)

        self.userList.updatePosition(user)

    def onHeartbeat(self, data):
        '''Handle heartbeat events with *data*.'''
        user = self.userList.getUser(data['user']['id'])

        if user:
            try:
                user.updateSession(data)
            except ftrack_connect.error.CrewSessionError:
                self.onEnter(data)

    def onExit(self, data):
        '''Handle exit events with *data*.'''
        user = self.userList.getUser(data['user']['id'])
        if user:
            user.removeSession(data['session_id'])

        self.userList.updatePosition(user)

    def onMessageReceived(self, message):
        '''Handle *message* received.'''
        sender = message['sender']['id']
        if sender == self.conversationUserId:
            self.chat.addMessage(
                dict(
                    text=message['text'],
                    name=message['sender']['name']
                )
            )

    def onChatMessageSubmitClicked(self, messageText):
        '''Handle message submitted clicked.'''

        try:
            self.persistMessage(messageText)
        except Exception:
            pass
        else:
            message = self.hub.sendMessage(
                self.conversationUserId, messageText
            )

            self.chat.addMessage(
                dict(
                    text=message['text'],
                    name=message['sender']['name'],
                    me=True
                )
            )

    def onConversationSelected(self, value):
        '''Handle conversation selected events.'''
        self.updateCurrentConversation(value['userId'])

        if self._extendedUser is None:
            self._extendedUser = ftrack_connect.ui.widget.user.UserExtended(
                value.get('name'),
                self.conversationUserId,
                value.get('applications')
            )

            self.userContainer.layout().insertWidget(0, self._extendedUser)
            self.userContainer.show()
        else:
            self._extendedUser.updateInformation(
                value.get('name'),
                self.conversationUserId,
                value.get('applications')
            )

        messages = _session.query(
            'select text, created_by.first_name, created_by.last_name, '
            'created_by_id, created_at from Message where '
            'conversation_id is "{0}"'.format(
            self.self.currentConversation['id']
        )).all()

        formattedMessages = sorted([
            dict(
                text=message['text'],
                name='{0} {1}'.format(
                    message['created_by']['first_name'],
                    message['created_by']['last_name']
                ),
                me=message['created_by_id'] == self.user.getId(),
                created_at=message['created_at']
            )
            for message in messages
        ], key=operator.itemgetter('created_at'))

        self.chat.load(formattedMessages)

    def persistMessage(self, message):
        '''Persist *message* to current conversation.'''
        self.currentConversation.session.create('Message', {
            'text': message,
            'conversation_id': self.currentConversation['id']
        })
        self.currentConversation.session.commit()

    def updateCurrentConversation(self, otherId):
        '''Update currently active conversation with *otherId*.

        Will get or create conversation for current user and user with
        *otherId*.

        The last_visit attribute will be updated to now.

        '''
        self.conversationUserId = otherId

        self.logger.debug('Retrieving conversation for ("{0}", "{1}")'.format(
            self.user.getId(), self.conversationUserId
        ))
        conversation = _session.query(
            'select id, participants.resource_id from Conversation '
            'where participants any (resource_id is "{user_id}") and '
            'participants any (resource_id is "{other_id}")'.format(
                user_id=self.user.getId(), other_id=self.conversationUserId
            )
        ).first()

        if not conversation:
            self.logger.debug('Conversation not found, creating new.')
            conversation = _session.create('Conversation')
            conversation['participants'].append(
                _session.create('Participant', {
                    'resource_id': self.conversationUserId,
                    'last_visit': datetime.datetime.now()
                })
            )
            conversation['participants'].append(
                _session.create('Participant', {
                    'resource_id': self.user.getId(),
                    'last_visit': datetime.datetime.now()
                })
            )

        for participant in conversation['participants']:
            if participant['resource_id'] == self.user.getId():
                participant['last_visit'] = datetime.datetime.now()

        conversation.session.commit()

        self.currentConversation = conversation
