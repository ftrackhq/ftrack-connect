# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from collections import defaultdict

from PySide import QtGui, QtCore
import ftrack
import ftrack.formatter

from ftrack_connect.ui.widget.notification import _notifications
from ftrack_connect.ui.widget.notification import Notification as _Notification
import ftrack_connect.ui.widget.item_list
import ftrack_connect.ui.widget.overlay
import ftrack_connect.worker

_typeMapper = {
    'asset.published': 'version',
    'change.status.shot': 'status',
    'change.status.task': 'status'
}


class NotificationList(ftrack_connect.ui.widget.item_list.ItemList):
    '''List notification.

    The notification list is managed using an internal model.

    '''

    def __init__(self, parent=None):
        '''Initialise widget with *parent*.'''
        super(NotificationList, self).__init__(
            widgetFactory=self._createNotificationWidget,
            widgetItem=lambda widget: widget.value(),
            parent=parent
        )
        self.list.setSelectionMode(
            QtGui.QAbstractItemView.NoSelection
        )
        self.list.setShowGrid(False)

        self.label = QtGui.QLabel('Notifications')
        self.layout().insertWidget(0, self.label)

    def _createNotificationWidget(self, item):
        '''Return notification widget for *item*.

        *item* should be a mapping of keyword arguments to pass to
        :py:class:`ftrack_connect.ui.widget.notification.Notification`.

        '''
        if item is None:
            item = {}

        _type = item.pop('type', None)
        notificationClass = _notifications.get(_type)

        if not notificationClass:
            notificationClass = _Notification

        return notificationClass(**item)

    def addItem(self, item, row=None):
        '''Add *item* at *row*.

        If *row* is not specified, then append item to end of list.

        '''
        if row is None:
            row = self.count()

        super(NotificationList, self).addItem(item, row=row)


class Notification(QtGui.QWidget):
    '''In-App Notification widget.'''

    #: Signal that a loading operation has started.
    loadStarted = QtCore.Signal()

    #: Signal that a loading operation has ended.
    loadEnded = QtCore.Signal()

    def __init__(self, parent=None):
        '''Initialise widget with *parent*'''
        super(Notification, self).__init__(parent=parent)

        self._context = defaultdict(list)

        layout = QtGui.QVBoxLayout()

        toolbar = QtGui.QHBoxLayout()

        self.setLayout(layout)

        reloadIcon = QtGui.QIcon(
            QtGui.QPixmap(':/ftrack/image/light/reload')
        )

        self.reloadButton = QtGui.QPushButton(reloadIcon, '')
        self.reloadButton.setFlat(True)
        self.reloadButton.clicked.connect(self.reload)

        notesRadio = QtGui.QCheckBox('Show notes')
        changesRadio = QtGui.QCheckBox('Show changes')

        toolbar.addWidget(notesRadio, stretch=1)
        toolbar.addWidget(changesRadio, stretch=1)
        toolbar.addWidget(self.reloadButton, stretch=0)

        layout.addLayout(toolbar)

        self._list = NotificationList(self)
        self._list.setObjectName('time-log-list')
        layout.addWidget(self._list, stretch=1)

        self.overlay = ftrack_connect.ui.widget.overlay.BusyOverlay(
            self, message='Loading'
        )

        self.overlay.hide()

        self.loadStarted.connect(self._onLoadStarted)
        self.loadEnded.connect(self._onLoadEnded)

    def _onLoadStarted(self):
        '''Handle load started.'''
        self.reloadButton.setEnabled(False)
        self.overlay.show()

    def _onLoadEnded(self):
        '''Handle load ended.'''
        self.overlay.hide()
        self.reloadButton.setEnabled(True)

    def addNotification(self, notification, row=None):
        '''Add *notification* on *row*.'''
        self._list.addItem(notification, row)

    def addContext(self, contextId, contextType, _reload=True):
        '''Add context with *contextId* and *contextType*.

        Optional *_reload* can be set to False to prevent reload of widget.

        '''

        self._context[contextType].append(contextId)

        if _reload:
            self.reload()

    def clear(self):
        '''Clear list of notifications.'''
        self._list.clearItems()

    def _reload(self):
        session = ftrack.Session()

        cases = []
        events = []

        if self._context['asset']:
            cases.append(
                '(feeds.owner_id in ({asset_ids}) and action is '
                '"asset.published")'.format(
                    asset_ids=','.join(self._context['asset'])
                )
            )

        if self._context['task']:
            cases.append(
                'parent_id in ({task_ids}) and action in '
                '("change.status.shot", "change.status.task"'.format(
                    task_ids=','.join(self._context['task'])
                )
            )

        if cases:
            events = session.query(
                'select id, action, parent_id, parent_type, created_at, data '
                'from Event where {0})'.format(' or '.join(cases))
            ).all()

            events.sort(key=lambda event: event['created_at'], reverse=True)

        return events

    def reload(self):
        '''Reload notifications.'''
        self.loadStarted.emit()
        worker = ftrack_connect.worker.Worker(self._reload)
        worker.start()

        while worker.isRunning():
            app = QtGui.QApplication.instance()
            app.processEvents()

        if worker.error:
            self.loadEnded.emit()
            raise worker.error[1], None, worker.error[2]

        events = worker.result

        self.clear()
        for event in events:
            self.addNotification({
                'type': _typeMapper[event['action']],
                'event': event
            })

        self.loadEnded.emit()
