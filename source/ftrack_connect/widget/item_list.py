# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui

import ftrack_connect.widget.list


class ItemList(QtGui.QFrame):
    '''Manage a list of items represented by widgets.'''

    def __init__(self, widgetFactory, widgetItem, parent=None):
        '''Initialise widget with *parent*.

        *widgetFactory* should be a callable that accepts an item and returns
        an appropriate widget.

        *widgetItem* should be a callable that accepts a widget and returns
        the appropriate item from the widget.

        '''
        self.widgetFactory = widgetFactory
        self.widgetItem = widgetItem

        super(ItemList, self).__init__(parent=parent)

        self.setLayout(QtGui.QVBoxLayout())
        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.NoFrame)

        # List
        self.list = ftrack_connect.widget.list.List()
        self.layout().addWidget(self.list, stretch=1)

        self.layout().setContentsMargins(5, 5, 5, 5)

        # Allow growing with container.
        self.setSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding,
            QtGui.QSizePolicy.MinimumExpanding
        )

    def count(self):
        '''Return count of items in list.'''
        return self.list.count()

    def addItem(self, item, row=None):
        '''Add *item* at *row*.'''
        if row is None:
            row = self.count()

        widget = self.widgetFactory(item)
        self.list.addWidget(widget, row)

    def removeItem(self, row):
        '''Remove item at *row*.'''
        self.list.removeWidget(row)

    def indexOfItem(self, item):
        '''Return row of *item* in list or None if not present.'''
        index = None

        for row in range(self.count()):
            widget = self.list.widgetAt(row)
            if self.widgetItem(widget) == item:
                index = row
                break

        return index

    def items(self):
        '''Return list of items.'''
        items = []
        for row in range(self.count()):
            widget = self.list.widgetAt(row)
            items.append(self.widgetItem(widget))

        return items

    def itemAt(self, row):
        '''Return item at *row*.'''
        widget = self.list.widgetAt(row)
        return self.widgetItem(widget)
