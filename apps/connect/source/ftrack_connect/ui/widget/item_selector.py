# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from ftrack_connect.qt import QtWidgets


class ItemSelector(QtWidgets.QComboBox):
    '''Item selector widget.'''

    @property
    def session(self):
        '''Return current session.'''
        return self._session

    def __init__(
        self,
        session=None,
        idField='id',
        labelField='label',
        defaultLabel='Unnamed Item',
        emptyLabel='Select an item',
        *args,
        **kwargs
    ):
        '''Initialise item selector widget.

        *idField* and *labelField* are the keys used to get the unique
        identifier and label for each item. *defaultLabel* is used if
        *labelField* is not found in an item and *emptyLabel* is used as
        the placholder label.

        '''
        super(ItemSelector, self).__init__(*args, **kwargs)
        self._session = session
        # Set style delegate to allow styling of combobox menu via Qt Stylesheet
        itemDelegate = QtWidgets.QStyledItemDelegate()
        self.setItemDelegate(itemDelegate)

        self._idField = idField
        self._labelField = labelField
        self._defaultLabel = defaultLabel
        self._emptyLabel = emptyLabel

        self.currentIndexChanged.connect(self._onCurrentIndexChanged)
        self.setItems()

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

    def findData(self, itemId):
        '''Return index of item with id equal to *itemId*

        If a matching item is not found, Return -1.

        '''
        foundIndex = -1
        for index in range(1, self.count()):
            item = self.itemData(index)
            if item == itemId:
                foundIndex = index
                break

        return foundIndex

    def selectItem(self, item):
        '''Select item with the same id as *item*.

        If a matching item is not found, selects the first item

        '''
        index = 0
        if item is not None:
            index = self.findData(item)
            if index == -1:
                index = 0

        self.setCurrentIndex(index)

    def items(self):
        '''Return current items.'''
        items = []
        for index in range(1, self.count()):
            items.append(self.itemData(index))

        return items

    def setItems(self, items=None):
        '''Set items to *items*, keeping current selection.

        *items* should be a list of mappings. Each mapping should contain keys
        matching those set for idField and labelField.

        '''
        if items is None:
            items = []

        currentItem = self.currentItem()
        self.clear()

        # Add default empty item
        self.addItem(str(self._emptyLabel), None)

        for item in items:
            label = item.get(self._labelField) or self._defaultLabel
            self.addItem(str(label), item[self._idField])

        # Re-select previously selected item
        self.selectItem(currentItem)
