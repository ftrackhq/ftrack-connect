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

        # Footer (item list controls)
        self.footer = QtGui.QFrame()
        self.footer.setLayout(QtGui.QHBoxLayout())
        self.footer.layout().addStretch(1)

        self.addButton = QtGui.QPushButton('Add')
        self.addButton.setToolTip('Add a new item to the list.')
        plusIcon = QtGui.QPixmap(':icon_add')
        self.addButton.setIcon(plusIcon)
        self.addButton.setIconSize(plusIcon.size())
        self.footer.layout().addWidget(self.addButton)

        self.removeButton = QtGui.QPushButton('Remove')
        self.removeButton.setToolTip('Remove selected items from list.')
        minusIcon = QtGui.QPixmap(':icon_remove')
        self.removeButton.setIcon(minusIcon)
        self.removeButton.setIconSize(minusIcon.size())
        self.footer.layout().addWidget(self.removeButton)

        self.footer.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.footer)

        self.layout().setContentsMargins(5, 5, 5, 5)

        # Allow growing with container.
        self.setSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding,
            QtGui.QSizePolicy.MinimumExpanding
        )

        self.removeButton.setDisabled(True)

        # Connect signals
        self.addButton.clicked.connect(self.onAddButtonClick)
        self.removeButton.clicked.connect(self.onRemoveButtonClick)

        selectionModel = self.list.selectionModel()
        selectionModel.selectionChanged.connect(self.onSelectionChanged)

    def onSelectionChanged(self, selected, deselected):
        '''Handle change in selection.'''
        rows = self.list.selected()
        if rows:
            self.removeButton.setEnabled(True)
        else:
            self.removeButton.setEnabled(False)

    def onAddButtonClick(self):
        '''Handle add button click.'''
        row = self.list.count()
        self.addItem(None, row)

    def onRemoveButtonClick(self):
        '''Handle remove button click.'''
        rows = self.list.selected()

        # Remove in reverse order to avoid incorrect index.
        rows = sorted(rows, reverse=True)
        for row in rows:
            self.removeItem(row)

    def addItem(self, item, row=None):
        '''Add *item* at *row*.'''
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
