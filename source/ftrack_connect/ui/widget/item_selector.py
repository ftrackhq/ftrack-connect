# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from Qt import QtWidgets, QtCore, QtGui


class ItemSelector(QtWidgets.QComboBox):
    '''Item selector widget.'''

    @property
    def session(self):
        '''Return current session.'''
        return self._session

    def __init__(
        self, session=None, idField='id', labelField='label', defaultLabel='Unnamed Item',
        emptyLabel='Select an item', *args, **kwargs
    ):
        '''Initialise item selector widget.

        *idField* and *labelField* are the keys used to get the unique
        identifier and label for each item. *defaultLabel* is used if
        *labelField* is not found in an item and *emptyLabel* is used as
        the placholder label.

        '''
        super(ItemSelector, self).__init__(*args, **kwargs)
        self.itemDelegate = QtWidgets.QStyledItemDelegate()

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setEditable(True)
        self.completer = QtWidgets.QCompleter(self)
        self.completer.setFilterMode(QtCore.Qt.MatchContains)
        self._session = session

        self.completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
        self.pFilterModel = QtCore.QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.completer.setPopup(self.view())
        self.completer.popup().setObjectName("completerPopup")

        self.setCompleter(self.completer)
        self.lineEdit().textEdited[str].connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.setTextIfCompleterIsClicked)

        self._idField = idField
        self._labelField = labelField
        self._defaultLabel = defaultLabel
        self._emptyLabel = emptyLabel

        self.currentIndexChanged.connect(self._onCurrentIndexChanged)
        self.model = QtGui.QStandardItemModel()

        self.setModel(self.model)
        # Set style delegate to allow styling of combobox menu via Qt Stylesheet
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
        # self.lineEdit().setPlaceholderText(self._emptyLabel)
        self.addItem(str(self._emptyLabel), None)

        for item in items:
            label = item.get(self._labelField) or self._defaultLabel
            self.addItem(str(label), item[self._idField])

        # Re-select previously selected item
        self.selectItem(currentItem)

    def setDelegate(self):
        self.setItemDelegate(self.itemDelegate)
        self.completer.popup().setItemDelegate(self.itemDelegate)

    def setModel(self, model):
        super(ItemSelector, self).setModel( model )
        self.pFilterModel.setSourceModel( model )
        self.completer.setModel(self.pFilterModel)
        self.setDelegate()

    def setModelColumn(self, column):
        self.completer.setCompletionColumn( column )
        self.pFilterModel.setFilterKeyColumn( column )
        super(ItemSelector, self).setModelColumn( column )

    def view(self):
        return self.completer.popup()

    def index(self):
        return self.currentIndex()

    def setTextIfCompleterIsClicked(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
