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
        self._list = ftrack_connect.widget.list.List()
        self.layout().addWidget(self._list, stretch=1)

        # Footer (item list controls)
        self._footer = QtGui.QFrame()
        self._footer.setLayout(QtGui.QHBoxLayout())
        self._footer.layout().addStretch(1)

        self._addButton = QtGui.QPushButton('Add')
        self._addButton.setToolTip('Add a new item to the list.')
        plusIcon = QtGui.QPixmap(':icon_add')
        self._addButton.setIcon(plusIcon)
        self._addButton.setIconSize(plusIcon.size())
        self._footer.layout().addWidget(self._addButton)

        self._removeButton = QtGui.QPushButton('Remove')
        self._removeButton.setToolTip('Remove selected items from list.')
        minusIcon = QtGui.QPixmap(':icon_remove')
        self._removeButton.setIcon(minusIcon)
        self._removeButton.setIconSize(minusIcon.size())
        self._footer.layout().addWidget(self._removeButton)

        self._footer.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._footer)

        self.layout().setContentsMargins(5, 5, 5, 5)

        # Allow growing with container.
        self.setSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding,
            QtGui.QSizePolicy.MinimumExpanding
        )

        self._removeButton.setDisabled(True)

        # Connect signals
        self._addButton.clicked.connect(self.onAddButtonClick)
        self._removeButton.clicked.connect(self.onRemoveButtonClick)

        selectionModel = self._list.selectionModel()
        selectionModel.selectionChanged.connect(self.onSelectionChanged)

    def onSelectionChanged(self, selected, deselected):
        '''Handle change in selection.'''
        rows = self._list.selected()
        if rows:
            self._removeButton.setEnabled(True)
        else:
            self._removeButton.setEnabled(False)

    def onAddButtonClick(self):
        '''Handle add button click.'''
        row = self._list.count()
        self.addItem(None, row)

    def onRemoveButtonClick(self):
        '''Handle remove button click.'''
        rows = self._list.selected()

        # Remove in reverse order to avoid incorrect index.
        rows = sorted(rows, reverse=True)
        for row in rows:
            self.removeItem(row)

    def addItem(self, item, row=None):
        '''Add *item* at *row*.'''
        widget = self.widgetFactory(item)
        self._list.addWidget(widget, row)

    def removeItem(self, row):
        '''Remove item at *row*.'''
        self._list.removeWidget(row)

    def indexOfItem(self, item):
        '''Return row of *item* in list or None if not present.'''
        index = None

        for row in range(self.count()):
            widget = self._list.widgetAt(row)
            if self.widgetItem(widget) == item:
                index = row
                break

        return index

    def items(self):
        '''Return list of items.'''
        items = []
        for row in range(self.count()):
            widget = self._list.widgetAt(row)
            items.append(self.widgetItem(widget))

        return items

    def itemAt(self, row):
        '''Return item at *row*.'''
        widget = self._list.widgetAt(row)
        return self.widgetItem(widget)
