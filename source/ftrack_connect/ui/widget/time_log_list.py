# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from QtExt import QtWidgets
from QtExt import QtCore

import ftrack_connect.ui.widget.item_list
import ftrack_connect.ui.widget.label
import ftrack_connect.ui.widget.time_log


class TimeLogList(ftrack_connect.ui.widget.item_list.ItemList):
    '''List time logs widget.'''

    itemSelected = QtCore.Signal(object)

    def __init__(self, parent=None, title=None, headerWidgets=None):
        '''Instantiate widget with optional *parent* and *title*.

        *headerWidgets* is an optional list of widgets to append to the header
        of the time log widget.

        '''
        super(TimeLogList, self).__init__(
            widgetFactory=self._createWidget,
            widgetItem=lambda widget: widget.value(),
            parent=parent
        )
        self.setObjectName('time-log-list')
        self.list.setShowGrid(False)

        # Disable selection on internal list.
        self.list.setSelectionMode(
            QtWidgets.QAbstractItemView.NoSelection
        )

        headerLayout = QtWidgets.QHBoxLayout()
        self.titleLabel = QtWidgets.QLabel(title)
        self.titleLabel.setProperty('title', True)

        headerLayout.addWidget(self.titleLabel, stretch=1)

        # TODO: Refacor and make use of QToolBar and QAction.
        # Also consider adding 'addAction'/'removeAction'.
        if headerWidgets:
            for widget in headerWidgets:
                headerLayout.addWidget(widget, stretch=0)

        self.layout().insertLayout(0, headerLayout)

    def setTitle(self, title):
        '''Set *title*.'''
        self.titleLabel.setText(title)

    def title(self):
        '''Return current title.'''
        self.titleLabel.text()

    def addItem(self, item, row=None):
        '''Add *item* at *row*.

        If *row* not specified then add to end of list.

        Return row item added at.

        '''
        row = super(TimeLogList, self).addItem(item, row=row)
        widget = self.list.widgetAt(row)

        # Connect the widget's selected signal to the itemSelected signal
        widget.selected.connect(self.itemSelected.emit)

        return row

    def _createWidget(self, item):
        '''Return time log widget for *item*.

        *item* should be a mapping of keyword arguments to pass to
        :py:class:`ftrack_connect.ui.widget.time_log.TimeLog`.

        '''
        if item is None:
            item = {}

        return ftrack_connect.ui.widget.time_log.TimeLog(**item)
