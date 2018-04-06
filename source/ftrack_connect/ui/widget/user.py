# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import arrow
from QtExt import QtWidgets, QtCore
import copy

import ftrack_connect.error
import ftrack_connect.ui.widget.label
import ftrack_connect.ui.widget.thumbnail


class UserExtended(QtWidgets.QFrame):
    '''Extended user information.'''

    def __init__(
        self, name, userId, applications, group=None, parent=None
    ):
        '''Initialise widget with initial component *value* and *parent*.'''
        super(UserExtended, self).__init__(parent=parent)

        self.applicationInfoWidget = QtWidgets.QLabel()

        self._userId = userId
        self._applications = applications

        self.setLayout(QtWidgets.QVBoxLayout())

        self.user = User(name, userId, group=None, applications=applications)
        self.layout().addWidget(self.user)

        self.layout().addWidget(self.applicationInfoWidget, stretch=0)

        self.updateInformation(name, userId, applications)

    def updateInformation(self, name, userId, applications):
        '''Update widget with *name*, *userId* and *applications*.'''
        if applications:
            applicationNames = []

            for application in applications.values():
                applicationNames.append(application.get('label'))

            self.applicationInfoWidget.setText(
                u'Applications: {0}'.format(', '.join(applicationNames))
            )
            self.applicationInfoWidget.show()
        else:
            self.applicationInfoWidget.hide()

        self._userId = userId

        self.user.setValue({
            'name': name,
            'userId': userId,
            'applications': applications
        })


class User(QtWidgets.QFrame):
    '''Represent a user.'''

    #: Item click signal.
    itemClicked = QtCore.Signal(object)

    def __init__(
        self, name, userId, group=None, applications=None, parent=None
    ):
        '''Initialise widget with initial component *value* and *parent*.'''
        super(User, self).__init__(parent)
        if applications is None:
            applications = {}

        self._userId = userId
        self._applications = applications
        self._group = group

        self.setObjectName('user')

        self.setLayout(QtWidgets.QHBoxLayout())

        self.thumbnail = ftrack_connect.ui.widget.thumbnail.User()
        self.thumbnail.setFixedWidth(30)
        self.thumbnail.setFixedHeight(30)
        self.thumbnail.load(userId)
        self.layout().addWidget(self.thumbnail)

        self.layout().setContentsMargins(0, 0, 0, 0)

        nameAndActivity = QtWidgets.QWidget()
        nameAndActivity.setLayout(QtWidgets.QVBoxLayout())
        nameAndActivity.layout().setContentsMargins(0, 0, 0, 0)

        self.countLabel = QtWidgets.QLabel()
        self.countLabel.setObjectName('user-conversation-count')
        self.countLabel.hide()

        self.nameLabel = ftrack_connect.ui.widget.label.Label()
        self.nameLabel.setText(name)
        self.nameLabel.setObjectName('name')
        nameAndActivity.layout().addWidget(self.nameLabel)

        self.activityLabel = ftrack_connect.ui.widget.label.Label()
        self.activityLabel.setObjectName('user-activity')

        self.nameAndCountLayout = QtWidgets.QHBoxLayout()
        self.nameAndCountLayout.addWidget(self.nameLabel, stretch=1)
        self.nameAndCountLayout.addWidget(self.countLabel, stretch=0)
        self.nameAndCountLayout.addSpacing(5)

        nameAndActivity.layout().addLayout(self.nameAndCountLayout)
        nameAndActivity.layout().addWidget(self.activityLabel)

        self.layout().addWidget(nameAndActivity)

        self._refreshStyles()
        self._updateActivity()

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value):
        self._group = value

    @property
    def online(self):
        '''Return if user is online or not.'''
        return len(self._applications.values()) > 0

    def _refreshStyles(self):
        '''Refresh styles for the user.'''
        if self.online:
            self.setStyleSheet('''
                QLabel#name {
                    color: white !important;
                }
            ''')
        else:
            self.setStyleSheet('''
                QLabel {
                    color: #585858 !important;
                }
            ''')

    def _updateActivity(self):
        '''Update activity.'''
        text = 'offline'

        if self.online:
            text = ''

        if self._applications:
            activity = min(
                application.get('activity')
                for application in self._applications.values()
            )
            text = arrow.get(activity).humanize()

        self.activityLabel.setText(text)

    def mousePressEvent(self, event):
        '''Handle mouse preseed event.'''
        self.itemClicked.emit(self.value())

    def value(self):
        '''Return dictionary with user data.'''
        return {
            'userId': self._userId,
            'name': self.nameLabel.text(),
            'applications': self._applications,
            'group': self.group
        }

    def setValue(self, value):
        '''Set *value* and update UI.'''
        self._applications = value.get('applications', {})
        self.nameLabel.setText(value['name'])

        if self._userId != value['userId']:
            self.thumbnail.load(value['userId'])

        self._userId = value['userId']
        self._updateActivity()
        self._refreshStyles()

    def id(self):
        '''Return current id.'''
        return self._id

    def setId(self, componentId):
        '''Set id to *componentId*.'''
        self._id = componentId

    def addSession(self, data):
        '''Add new session.'''
        value = self.value()

        sessionId = data['session_id']
        application = copy.deepcopy(data['application'])
        application['timestamp'] = data['timestamp']

        value['applications'][sessionId] = application
        value['applications'][sessionId]['timestamp'] = data['timestamp']
        value['applications'][sessionId]['activity'] = data['activity']

        self.setValue(value)

    def updateSession(self, data):
        '''Update a session with *sessionId*.'''

        self.addSession(data)

    def removeSession(self, sessionId):
        '''Remove session with *sessionId*.'''
        value = self.value()
        if sessionId in value['applications']:
            del value['applications'][sessionId]

            self.setValue(value)

    def setCount(self, count=0):
        '''Set *count*.

        .. note::

            If set to `0` the label will be hidden.

        '''
        self.countLabel.setText(str(count))

        if count:
            self.countLabel.show()
        else:
            self.countLabel.hide()