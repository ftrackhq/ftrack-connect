# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import arrow
from PySide import QtGui, QtCore
import ftrack

import ftrack_connect.ui.widget.label
import ftrack_connect.ui.widget.thumbnail


class UserExtended(QtGui.QWidget):
    '''Extended user information.'''

    def __init__(
        self, name, userId, applications, group=None, parent=None
    ):
        '''Initialise widget with initial component *value* and *parent*.'''
        super(UserExtended, self).__init__(parent=parent)

        self.applicationInfoWidget = QtGui.QLabel()

        self._name = name
        self._userId = userId
        self._applications = applications

        self.setLayout(QtGui.QVBoxLayout())

        self.nameLabel = ftrack_connect.ui.widget.label.Label()
        self.layout().addWidget(self.nameLabel, stretch=0)

        self.activityLabel = ftrack_connect.ui.widget.label.Label()
        self.layout().addWidget(self.activityLabel, stretch=0)

        self.layout().addWidget(self.applicationInfoWidget, stretch=0)

        self.chatLabel = ftrack_connect.ui.widget.label.Label()
        self.layout().addWidget(self.chatLabel, stretch=1)

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
        else:
            self.applicationInfoWidget.setText(
                'User is offline'
            )

        self.nameLabel.setText(name)
        self._userId = userId


class User(QtGui.QWidget):
    '''Represent a user.'''

    #: Item click signal.
    itemClicked = QtCore.Signal(object)

    def __init__(
        self, name, userId, applications=None, group=None, parent=None
    ):
        '''Initialise widget with initial component *value* and *parent*.'''
        super(User, self).__init__(parent)
        if applications is None:
            applications = {}

        self._name = name
        self._userId = userId
        self._applications = applications

        self.setObjectName('user')

        self.setLayout(QtGui.QHBoxLayout())

        thumbnailUrl = ftrack.User(userId).getThumbnail()
        self.thumbnail = ftrack_connect.ui.widget.thumbnail.Thumbnail()
        self.thumbnail.setFixedWidth(30)
        self.thumbnail.setFixedHeight(30)
        self.thumbnail.loadFromUrl(thumbnailUrl)
        self.layout().addWidget(self.thumbnail)

        nameAndActivity = QtGui.QWidget()
        nameAndActivity.setLayout(QtGui.QVBoxLayout())

        self.nameLabel = ftrack_connect.ui.widget.label.Label()
        self.nameLabel.setText(name)
        self.nameLabel.setObjectName('name')
        nameAndActivity.layout().addWidget(self.nameLabel)

        self.activityLabel = ftrack_connect.ui.widget.label.Label()
        nameAndActivity.layout().addWidget(self.activityLabel)

        self.layout().addWidget(nameAndActivity)

        self._refreshStyles()
        self._updateActivity()

    @property
    def online(self):
        '''Return if user is online or not.'''
        return len(self._applications.values()) > 0

    def _refreshStyles(self):
        '''Refresh styles for the user.'''
        if self.online:
            self.setStyleSheet('''
                QLabel {
                    color: black !important;
                }
            ''')
        else:
            self.setStyleSheet('''
                QLabel {
                    color: grey !important;
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
        '''Return dictionary with component data.'''
        return {
            'user_id': self._userId,
            'name': self._name,
            'applications': self._applications
        }

    def setValue(self, value):
        '''Set *value* and update UI.'''
        self._applications = value.get('applications', {})
        self.nameLabel.setText(value['name'])
        self._updateActivity()
        self._refreshStyles()

    def id(self):
        '''Return current id.'''
        return self._id

    def setId(self, componentId):
        '''Set id to *componentId*.'''
        self._id = componentId
