# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import functools

from PySide import QtGui

import ftrack_connect.widget.component
import ftrack_connect.widget.item_list


class ComponentsList(ftrack_connect.widget.item_list.ItemList):
    '''List components.

    The component list is managed using an internal model.

    '''

    def __init__(self, parent=None):
        '''Initialise widget with *parent*.'''
        super(ComponentsList, self).__init__(
            widgetFactory=self._createComponentWidget,
            widgetItem=lambda widget: widget.value(),
            parent=parent
        )
        self.list.setSelectionMode(
            QtGui.QAbstractItemView.NoSelection
        )
        self.list.setShowGrid(False)

        self.label = QtGui.QLabel('Components')
        self.layout().insertWidget(0, self.label)

    def _createComponentWidget(self, item):
        '''Return component widget for *item*.

        *item* should be a mapping of keyword arguments to pass to
        :py:class:`ftrack_connect.widget.component.Component`.

        '''
        if item is None:
            item = {}

        return ftrack_connect.widget.component.Component(**item)

    def addItem(self, item, row=None):
        '''Add *item* at *row*.

        If *row* is not specified, then append item to end of list.

        '''
        if row is None:
            row = self.count()

        super(ComponentsList, self).addItem(item, row=row)
        widget = self.list.widgetAt(row)

        # Connect remove action.
        widget.removeAction.triggered.connect(
            functools.partial(self._removeComponent, widget)
        )

    def _removeComponent(self, widget):
        '''Remove component represented by *widget*.'''
        row = self.list.indexOfWidget(widget)
        self.removeItem(row)
