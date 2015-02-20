# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import uuid
import datetime

import arrow
from PySide import QtGui, QtCore

import ftrack_connect.ui.widget.label

class UserExtended(QtGui.QWidget):

    def __init__(self, name, userId, applications, group=None, parent=None
    ):
        '''Initialise widget with initial component *value* and *parent*.'''
        super(UserExtended, self).__init__(parent=parent)

        self.applicationInfoWidget = QtGui.QLabel()

        self._name = name
        self._userId = userId
        self._applications = applications

        self.setLayout(QtGui.QVBoxLayout())

        self.nameLabel = ftrack_connect.ui.widget.label.Label()
        # self.nameLabel.setSizePolicy(
        #     QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        # )
        self.layout().addWidget(self.nameLabel, stretch=0)

        self.activityLabel = ftrack_connect.ui.widget.label.Label()
        self.layout().addWidget(self.activityLabel, stretch=0)

        self.layout().addWidget(self.applicationInfoWidget, stretch=0)

        self.chatLabel = ftrack_connect.ui.widget.label.Label()
        self.layout().addWidget(self.chatLabel, stretch=1)

        self.updateInfo(name, userId, applications)

    def updateInfo(self, name, userId, applications):
        if applications:
            applicationNames = []

            for application in applications.values():
                applicationNames.append(application.get('label'))

            self.applicationInfoWidget.setText(
                'Applications: ' + ', '.join(applicationNames)
            )
        else:
            self.applicationInfoWidget.setText(
                'User is offline'
            )

        self.nameLabel.setText(name)
        self._userId = userId


class User(QtGui.QWidget):
    '''Represent a component.'''

    itemClicked = QtCore.Signal(object)

    def __init__(self, name, userId, applications=None, group=None, parent=None
    ):
        '''Initialise widget with initial component *value* and *parent*.'''
        super(User, self).__init__(parent)
        if applications is None:
            applications = {}

        self._name = name
        self._userId = userId
        self._applications = applications

        self.setLayout(QtGui.QVBoxLayout())

        self.nameLabel = ftrack_connect.ui.widget.label.Label()
        self.nameLabel.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        )
        self.nameLabel.setText(name)
        self.layout().addWidget(self.nameLabel)

        self.activityLabel = ftrack_connect.ui.widget.label.Label()
        self.layout().addWidget(self.activityLabel)

        self._refreshStyles()
        self._updateActivity()

    def _isOnline(self):
        filterTime = datetime.datetime.utcnow() - datetime.timedelta(seconds=30)
        return any(
            application['timestamp'] >= filterTime
            for application in self._applications.values()
        )

    def _refreshStyles(self):
        if self._isOnline():
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
        text = '-'

        if self._applications:
            activity = min(
                application.get('activity')
                for application in self._applications.values()
            )
            text = arrow.get(activity).humanize()

        self.activityLabel.setText(text)

    def mousePressEvent(self, event):
        self.itemClicked.emit(self.value())

    def value(self):
        '''Return dictionary with component data.'''
        return {
            'user_id': self._userId,
            'name': self._name,
            'applications': self._applications
        }

    def setValue(self, value):
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
