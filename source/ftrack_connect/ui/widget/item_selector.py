# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui


class ItemSelector(QtGui.QComboBox):
    '''Item selector widget.'''

    def __init__(
        self, idField='id', labelField='label', defaultLabel='Unnamed Item',
        emptyLabel='Select an item', *args, **kwargs
    ):
        '''Initialise item selector widget.'''
        super(ItemSelector, self).__init__(*args, **kwargs)

        itemDelegate = QtGui.QStyledItemDelegate()
        self.setItemDelegate(itemDelegate)

        self._idField = idField
        self._labelField = labelField
        self._defaultLabel = defaultLabel
        self._emptyLabel = emptyLabel

        self.currentIndexChanged.connect(self._onCurrentIndexChanged)
        self.updateItems()

    def _onCurrentIndexChanged(self):
        '''Update style property when current index changes.'''
        currentIndexIsDefault = self.currentIndex() == 0
        self.setProperty('ftrackCurrentIndexIsDefault', currentIndexIsDefault)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _currentItemId(self):
        '''Return id for the currently selected index.'''
        currentIndex = self.currentIndex()
        return self.itemData(currentIndex)

    def _selectItemWithId(self, itemId):
        '''Select item with *itemId*.

        If *itemId* is not found, select the first item.

        '''
        index = self.findData(itemId)
        if index == -1:
            index = 0
        self.setCurrentIndex(index)

    def updateItems(self, items=None):
        '''Update list of items to *items*, keeping current selection.'''
        if items is None:
            items = []

        currentItemId = self._currentItemId()
        self.clear()

        # Add default empty item
        self.addItem(self._emptyLabel, None)

        for item in items:
            itemId = item.get(self._idField)
            label = item.get(self._labelField) or self._defaultLabel
            self.addItem(label, itemId)

        # Re-select previously selected item
        self._selectItemWithId(currentItemId)
