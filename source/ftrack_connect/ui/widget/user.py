# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import arrow
from PySide import QtGui, QtCore
import copy

import ftrack_connect.ui.widget.label
import ftrack_connect.ui.widget.thumbnail


class UserExtended(QtGui.QFrame):
    '''Extended user information.'''

    conferenceRequest = QtCore.Signal(object)

    def __init__(
        self, name, userId, applications, group=None, parent=None
    ):
        '''Initialise widget with initial component *value* and *parent*.'''
        super(UserExtended, self).__init__(parent=parent)

        self.applicationInfoWidget = QtGui.QLabel()

        self._userId = userId
        self._applications = applications

        self.setLayout(QtGui.QVBoxLayout())

        topRow = QtGui.QWidget()
        topRow.setLayout(QtGui.QHBoxLayout())

        self.user = User(name, userId, group=None, applications=applications)
        topRow.layout().addWidget(self.user, stretch=1)
        self.videoConferenceStart = QtGui.QPushButton(
            QtGui.QIcon(
                QtGui.QPixmap(':/ftrack/image/dark/phone')
            ),
            ''
        )
        topRow.layout().addWidget(self.videoConferenceStart, stretch=0)

        self.layout().addWidget(topRow, stretch=0)
        self.layout().addWidget(self.applicationInfoWidget, stretch=0)

        self.videoConferenceStart.clicked.connect(self._onConferenceClicked)

        self.updateInformation(name, userId, applications)

    def _onConferenceClicked(self):
        '''Handle conference clicked event.'''
        self.conferenceRequest.emit(self._userId)

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


class User(QtGui.QFrame):
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

        self.setLayout(QtGui.QHBoxLayout())

        self.thumbnail = ftrack_connect.ui.widget.thumbnail.User()
        self.thumbnail.setFixedWidth(30)
        self.thumbnail.setFixedHeight(30)
        self.thumbnail.load(userId)
        self.layout().addWidget(self.thumbnail)

        self.layout().setContentsMargins(0, 0, 0, 0)

        nameAndActivity = QtGui.QWidget()
        nameAndActivity.setLayout(QtGui.QVBoxLayout())
        nameAndActivity.layout().setContentsMargins(0, 0, 0, 0)

        self.nameLabel = ftrack_connect.ui.widget.label.Label()
        self.nameLabel.setText(name)
        self.nameLabel.setObjectName('name')
        nameAndActivity.layout().addWidget(self.nameLabel)

        self.activityLabel = ftrack_connect.ui.widget.label.Label()
        self.activityLabel.setObjectName('user-activity')
        nameAndActivity.layout().addWidget(self.activityLabel)

        self.layout().addWidget(nameAndActivity)

        self._highlight = False

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
        style = ''
        if self.online:
            style += '''
                QLabel#name {
                    color: white !important;
                }
            '''

            if True:
                self.activityLabel.setStyleSheet('''
                    QLabel {
                        color: rgba(238, 99, 76, 200) !important;
                    }
                ''')
        else:
            style += '''
                QLabel {
                    color: #585858 !important;
                }
            '''


        self.setStyleSheet(style)

    def setHighlight(self, highlight):
        '''Highlight user background if *highlight* is true.'''
        self._highlight = highlight
        self._refreshStyles()

    def _updateActivity(self):
        '''Update activity.'''
        text = 'offline'

        if self.online:
            text = ''

        if self._applications:
            latest_active_application = self._applications.values()[0]
            for application in self._applications.values():
                if (application.get('activity') < latest_active_application.get('activity')):
                    latest_active_application = application

            activity = latest_active_application.get('activity')
            context_name = latest_active_application.get('context_name')
            if context_name:
                context_name += ' '
            else:
                context_name = ''

            text = '{context_name}'.format(
                context_name=context_name
#                time=arrow.get(activity).humanize()
            )

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

    def addSession(self, sessionId, timestamp, context, application):
        '''Add new session.'''
        value = self.value()

        application = copy.deepcopy(application)
        application['timestamp'] = timestamp
        application['context'] = context
        value['applications'][sessionId] = application

        self.setValue(value)

    def updateSession(self, sessionId, timestamp, activity):
        '''Update a session with *sessionId*.'''
        value = self.value()

        value['applications'][sessionId]['timestamp'] = timestamp
        value['applications'][sessionId]['activity'] = activity

        self.setValue(value)

    def removeSession(self, sessionId):
        '''Remove session with *sessionId*.'''
        value = self.value()
        if sessionId in value['applications']:
            del value['applications'][sessionId]

            self.setValue(value)
