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

    def currentItem(self):
        '''Return the currently selected index.'''
        currentIndex = self.currentIndex()
        return self.itemData(currentIndex)

    def _findItemWithId(self, itemId):
        '''Return index of item with id equal to *itemId*

        If a matching item is not found, Return 0.

        '''
        foundIndex = 0
        for index in xrange(self.count()):
            item = self.itemData(index)

            if item is None:
                continue

            if item.get(self._idField) == itemId:
                foundIndex = index
                break

        return foundIndex
     
    def _selectItem(self, item):
        '''Select item with the same id as *item*.

        If a matching item is not found, selects the first item

        '''
        index = 0
        if item is not None:
            itemId = item.get(self._idField)
            index = self._findItemWithId(itemId)

        self.setCurrentIndex(index)

    def updateItems(self, items=None):
        '''Update list of items to *items*, keeping current selection.'''
        if items is None:
            items = []

        currentItem = self.currentItem()
        self.clear()

        # Add default empty item
        self.addItem(self._emptyLabel, None)

        for item in items:
            label = item.get(self._labelField) or self._defaultLabel
            self.addItem(label, item)

        # Re-select previously selected item
        self._selectItem(currentItem)
