# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import copy

from PySide import QtGui, QtCore

import ftrack_connect.ui.widget.item_list
import ftrack_connect.ui.widget.user
import ftrack_connect.ui.widget.label


class GroupHeader(QtGui.QLabel):
    '''Group header widget.'''
    def __init__(self, parent=None):
        super(GroupHeader, self).__init__(parent)
        self.setObjectName('header')

    def value(self):
        '''Return value for group header.'''
        return self.text()


class UserList(ftrack_connect.ui.widget.item_list.ItemList):
    '''User list widget.'''

    #: Signal to handle click events.
    itemClicked = QtCore.Signal(object)

    def __init__(self, groups=None, parent=None):
        '''Initialise widget with *groups*.'''
        if groups is None:
            groups = []

        super(UserList, self).__init__(
            widgetFactory=self._createWidget,
            widgetItem=lambda widget: widget.value(),
            parent=parent
        )
        self.setObjectName('presence-list')
        self.list.setSelectionMode(
            QtGui.QAbstractItemView.NoSelection
        )
        self.list.setShowGrid(False)

        for group in groups:
            self.addItem(group)

    def _createWidget(self, item):
        '''Return user widget for *item*.'''
        if item is None:
            item = {}

        if isinstance(item, basestring):
            return GroupHeader(item)

        widget = ftrack_connect.ui.widget.user.User(**item)
        widget.itemClicked.connect(
            self.itemClicked.emit
        )
        widget.setStyleSheet(
            '''
                QWidget#user {
                    background-color: transparent;
                }

            '''
        )

        return widget

    def addSession(self, userId, sessionId, timestamp, application):
        '''Add session for *userId* with *sessionId*.'''
        for row in range(self.count()):
            widget = self.list.widgetAt(row)
            value = self.widgetItem(widget)

            if isinstance(value, dict) and value.get('user_id') == userId:
                application = copy.deepcopy(application)
                application['timestamp'] = timestamp
                value['applications'][sessionId] = application

                widget.setValue(value)

                return

        raise ValueError('User with id {0} could not be found.'.format(userId))

    def updateSession(self, sessionId, timestamp, activity):
        '''Update a session with *sessionId*.'''
        for row in range(self.count()):
            widget = self.list.widgetAt(row)
            value = self.widgetItem(widget)
            if isinstance(value, dict) and sessionId in value['applications']:
                value['applications'][sessionId]['timestamp'] = timestamp
                value['applications'][sessionId]['activity'] = activity

                widget.setValue(value)
                return

        raise ValueError(
            'Session with id {0} could not be found.'.format(sessionId)
        )

    def removeSession(self, sessionId):
        '''Remove session with *sessionId*.'''
        for row in range(self.count()):
            widget = self.list.widgetAt(row)
            value = self.widgetItem(widget)
            if isinstance(value, dict) and sessionId in value['applications']:
                del value['applications'][sessionId]

                widget.setValue(value)
                return

        raise ValueError(
            'Session with id {0} could not be found.'.format(sessionId)
        )

    def userExists(self, userId):
        '''Return true if *userId* exists.'''
        for value in self.items():
            if isinstance(value, dict) and value['user_id'] == userId:
                return True

        return False

    def addItem(self, item, row=None):
        '''Add *item* at *row*.

        If *row* is not specified, then append item to end of list.

        '''
        if not isinstance(item, basestring):
            group = item.get('group')
            row = self.indexOfItem(group)

            if row is None:
                raise ValueError('group {0} not recognized'.format(group))

            row += 1

        return super(UserList, self).addItem(item, row=row)
