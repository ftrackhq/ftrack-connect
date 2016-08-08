# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import operator
import logging

from Qt import QtWidgets

import ftrack_connect.ui.widget.label
import ftrack_connect.ui.widget.user_list
import ftrack_connect.ui.widget.user
import ftrack_connect.ui.widget.chat
import ftrack_connect.error
import ftrack_connect.ui.widget.overlay


logger = logging.getLogger(__name__)


def defaultClassifier(userId):
    '''Default user classifier.'''
    return 'others'


class Crew(QtWidgets.QWidget):
    '''User presence widget.'''

    def __init__(
            self, groups, user, hub, classifier=None, parent=None
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
        self._currentConversationUserId = None
        self._currentConversationId = None

        self.hub = hub

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        # If not classifier is specified return default `other` group.
        if not classifier:
            classifier = defaultClassifier

        self._classifier = classifier

        self.hub.onEnter.connect(self.onEnter)
        self.hub.onHeartbeat.connect(self.onHeartbeat)
        self.hub.onExit.connect(self.onExit)
        self.hub.onConversationMessagesLoaded.connect(
            self.onConversationLoaded
        )
        self.hub.onConversationUpdated.connect(self.onConversationUpdated)
        self.hub.onConversationSeen.connect(self.onConversationSeen)

        groups = [group.lower() for group in groups]

        if 'others' not in groups:
            groups.append('others')

        if 'offline' not in groups:
            groups.append('offline')

        self._groups = groups

        self.userList = ftrack_connect.ui.widget.user_list.UserList(
            groups=self._groups
        )

        self.userContainer = QtWidgets.QFrame()
        self.userContainer.setObjectName('user-container')
        self.userContainer.setLayout(QtWidgets.QVBoxLayout())
        self.userContainer.layout().setContentsMargins(0, 0, 0, 0)

        self.setLayout(QtWidgets.QHBoxLayout())
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

    def onConversationUpdated(self, conversationId):
        '''Handle *message* received.'''
        if conversationId == self._currentConversationId:

            messages = self.hub.getConversationUpdates(
                conversationId, clear=True
            )

            for message in messages:
                self.chat.addMessage(
                    dict(
                        text=message['text'],
                        name=message['sender']['name'],
                        me=message['sender']['id'] == self.user.getId()
                    )
                )

            self.hub.markConversationAsSeen(conversationId, self.user.getId())

        else:
            self.updateConversationCount(conversationId)

    def onChatMessageSubmitClicked(self, messageText):
        '''Handle message submitted clicked.'''
        message = self.hub.sendMessage(
            self._currentConversationUserId,
            messageText,
            self._currentConversationId
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
        conversation = self.hub.getConversation(
            self.user.getId(), value['userId']
        )
        self._currentConversationUserId = value['userId']
        self._currentConversationId = conversation['id']

        if self._extendedUser is None:
            self._extendedUser = ftrack_connect.ui.widget.user.UserExtended(
                value.get('name'),
                self._currentConversationUserId,
                value.get('applications')
            )

            self.userContainer.layout().insertWidget(0, self._extendedUser)
            self.userContainer.show()
        else:
            self._extendedUser.updateInformation(
                value.get('name'),
                self._currentConversationUserId,
                value.get('applications')
            )

        self.chat.showOverlay()
        self.hub.loadMessages(conversation['id'])

    def onConversationLoaded(self, conversationId, messages):
        '''Handle conversation loaded events.'''
        if conversationId == self._currentConversationId:
            formattedMessages = sorted([
                dict(
                    text=message['text'],
                    name=u'{0} {1}'.format(
                        message['created_by']['first_name'],
                        message['created_by']['last_name']
                    ),
                    me=message['created_by_id'] == self.user.getId(),
                    created_at=message['created_at']
                )
                for message in messages
            ], key=operator.itemgetter('created_at'))

            self.chat.hideOverlay()
            self.chat.load(formattedMessages)

            self.hub.markConversationAsSeen(conversationId, self.user.getId())

    def onConversationSeen(self, event):
        '''Handle conversation seen *event*.'''
        self.updateConversationCount(event['conversation'])

    def updateConversationCount(self, conversationId):
        '''Update conversation count for *conversationId*.'''
        messages = self.hub.getConversationUpdates(conversationId)
        participants = self.hub.getParticipants(conversationId)

        for participant in participants:
            if participant['resource_id'] != self.user.getId():
                user = self.userList.getUser(participant['resource_id'])
                if user:
                    user.setCount(len(messages))
