# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import inspect
import sys
import json

import arrow
from PySide import QtGui
import ftrack_legacy
import ftrack

# TODO: The Session should not be created here.
session = ftrack.Session()


class Notification(QtGui.QWidget):
    '''Represent a notification.'''

    #: Unique identifier for the notification class.
    _type = None

    def __init__(
        self, event=None, date=None, parent=None
    ):
        '''Initialise widget with initial component *event* and *parent*.'''
        super(Notification, self).__init__(parent=parent)
        self.horizontalLayout = QtGui.QHBoxLayout()
        verticalLayout = QtGui.QVBoxLayout()

        self.setLayout(self.horizontalLayout)

        self.horizontalLayout.addLayout(verticalLayout, stretch=1)

        self.textLabel = QtGui.QLabel()
        verticalLayout.addWidget(self.textLabel)

        self.dateLabel = QtGui.QLabel()
        verticalLayout.addWidget(self.dateLabel)

        if hasattr(self, '_buttonText'):
            self.actionButton = QtGui.QPushButton(self._buttonText)
            self.actionButton.clicked.connect(self._onButtonClicked)
            self.horizontalLayout.addWidget(self.actionButton)

        self.setDate(event['created_at'])

        self.setEvent(event)

    def _load(self):
        '''Load notification data to display.'''
        raise NotImplementedError()

    def value(self):
        '''Return dictionary with component data.'''
        return {
            'text': self.textLabel.text(),
            'type': self._type
        }

    def load(self):
        '''Load notification content.'''
        self._load()

    def setEvent(self, event):
        '''Set *event*.'''
        self._event = event

        self.load()

    def setText(self, text):
        '''Set *text*.'''
        self.textLabel.setText(text)

    def setDate(self, date):
        '''Set *date*.'''
        self._date = arrow.get(date)
        self.dateLabel.setText(
            self._date.humanize()
        )

    def _onButtonClicked(self):
        '''Handle button clicked.'''
        ftrack_legacy.EVENT_HUB.publish(
            ftrack_legacy.Event(
                'ftrack.crew.notification.{0._type}'.format(self),
                data=self.value()
            ),
            synchronous=True
        )


class VersionNotification(Notification):
    '''Represent version notification.'''

    _type = 'version'

    _buttonText = 'Load version'

    def _load(self):
        '''Internal load of data from event.'''
        self.setText('New version available')
        version = session.query(
            'select asset.name, version from AssetVersion where id is '
            '"{0}"'.format(self._event['parent_id'])
        ).all()

        self.setText(
            (
                'Version <span style="color: #E6E6E6">{1}</span> of '
                '<span style="color: #E6E6E6">{0}</span> available.'
            ).format(
                version[0]['asset']['name'], version[0]['version']
            )
        )

    def value(self):
        '''Override and add extra information.'''
        value = super(VersionNotification, self).value()

        value['version_id'] = self._event['parent_id']

        return value


class StatusNotification(Notification):
    '''Represent version notification.'''

    _type = 'status'

    def _load(self):
        '''Internal load of data from event.'''

        data = json.loads(self._event['data'])

        status = session.query('TaskStatus where id is "{0}"'.format(
            data['statusid']['new'])
        ).all()

        parentName = 'Unknown'
        if self._event['parent_type'] == 'task':
            parentName = session.query(
                'select name from Context '
                'where id is "{0}"'.format(
                    self._event['parent_id']
                )
            ).all()[0]['name']

        if status:
            status = status[0]

            self.setText(
                u'Status of <span style="color: #E6E6E6;">{2}</span> changed '
                'to <span style="color: #E6E6E6;">{1}</span>'.format(
                    status['color'], status['name'], parentName
                )
            )


class PropertyNotification(Notification):
    '''Represent property notification.'''

    _type = 'property'

    _buttonText = 'Update'

    def _load(self):
        '''Internal load of data from event.'''
        data = json.loads(self._event['data'])
        value = data['value']

        self.attributeName = self._event['action'].split('.')[-1]

        self.oldValue = value['old']
        self.newValue = value['new']

        self.setText(
            u'Attribute <span style="color: #E6E6E6;">{0}</span>'
            ' changed from <span style="color: #E6E6E6;">{1}</span> to '
            '<span style="color: #E6E6E6;">{2}</span>'.format(
                self._event['action'].split('.')[-1],
                self.oldValue,
                self.newValue
            )
        )

    def value(self):
        '''Override and add extra information.'''
        value = super(PropertyNotification, self).value()

        value.update({
            'new_value': self.newValue,
            'old_value': self.oldValue,
            'attribute_name': self.attributeName
        })

        return value


class AssignmentNotification(Notification):
    '''Represent property notification.'''

    _type = 'assignment'

    _buttonText = 'Open'

    def _load(self):
        '''Internal load of data from event.'''
        self._taskId = self._event['parent_id']

        task = session.query(
            'select name, parent.name from Task where id is "{0}"'.format(
                self._taskId
            )
        ).all()[0]

        self.setText(
            u'Assigned to <span style="color: #E6E6E6;">{0}</span> on '
            '<span style="color: #E6E6E6;">{1}</span>'.format(
                task['name'],
                task['parent']['name']
            )
        )

    def value(self):
        '''Override and add extra information.'''
        value = super(AssignmentNotification, self).value()

        value.update({
            'task_id': self._taskId
        })

        return value


def _mapNotifications():
    '''Return dictionary with all notification subclasses.'''
    notifications = {}
    for clsName, cls in inspect.getmembers(
        sys.modules[__name__], inspect.isclass
    ):
        if issubclass(cls, Notification):
            notifications[cls._type] = cls

    return notifications

notifications = _mapNotifications()
