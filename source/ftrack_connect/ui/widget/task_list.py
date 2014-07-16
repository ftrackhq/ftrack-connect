# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import uuid

from PySide import QtGui
from PySide import QtCore

import ftrack_connect.ui.widget.item_list
import ftrack_connect.ui.widget.label
import ftrack_connect.ui.widget.task


class TaskList(ftrack_connect.ui.widget.item_list.ItemList):
    '''List tasks widget.'''

    taskSelected = QtCore.Signal(object)

    def __init__(self, parent=None, title=''):
        super(TaskList, self).__init__(
            widgetFactory=self._createTaskWidget,
            widgetItem=lambda widget: widget.value(),
            parent=parent
        )
        self.setObjectName('tasklist')
        self.list.setShowGrid(False)

        # Disbale selection on internal list.
        self.list.setSelectionMode(
            QtGui.QAbstractItemView.NoSelection
        )

        self.titleLabel = QtGui.QLabel(title)
        self.titleLabel.setObjectName('title')
        self.layout().insertWidget(0, self.titleLabel)

    def setTitle(self, title):
        '''Set *title*.'''
        self.titleLabel.setText(title)

    def getTitle(self):
        '''Return currect title.'''
        self.titleLabel.text()

    def addItem(self, item, row=None):
        '''Add *item* at *row*.

        If *row* is not specified, then append item to end of list.

        '''
        if row is None:
            row = self.count()

        super(TaskList, self).addItem(item, row=row)
        widget = self.list.widgetAt(row)

        # Connect the widget's selected signal to the taskSelected signal
        widget.selected.connect(self.taskSelected.emit)

    def _createTaskWidget(self, item):
        '''Return timer task widget for *item*.

        *item* should be a mapping of keyword arguments to pass to
        :py:class:`ftrack_connect.ui.widget.task.Task`.

        '''
        if item is None:
            item = {}

        return ftrack_connect.ui.widget.task.Task(**item)
