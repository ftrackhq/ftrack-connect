# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack
#             Copyright (c) 2014 Martin Pengelly-Phillips
# :notice: Derived from Riffle (https://github.com/4degrees/riffle)

from PySide import QtGui, QtCore

import ftrack_connect.ui.model.entity_tree
import ftrack_connect.ui.widget.overlay


class EntityBrowser(QtGui.QFrame):
    '''Entity browser.'''

    def __init__(self, root=None, parent=None):
        '''Initialise browser with *root* entity.

        Use an empty *root* to start with list of projects.

        *parent* is the optional owner of this UI element.

        '''
        super(EntityBrowser, self).__init__(parent=parent)
        self._root = root
        self._selected = []
        self._updatingNavigationBar = False

        self._construct()
        self._postConstruction()

    def _construct(self):
        '''Construct widget.'''
        self.setLayout(QtGui.QVBoxLayout())

        self.headerLayout = QtGui.QHBoxLayout()

        self.navigationBar = QtGui.QTabBar()
        self.navigationBar.setExpanding(False)
        self.navigationBar.setDrawBase(False)
        self.headerLayout.addWidget(self.navigationBar, stretch=1)

        self.navigateUpButton = QtGui.QToolButton()
        self.navigateUpButton.setIcon(
            QtGui.QIcon(':ftrack/image/light/upArrow')
        )
        self.headerLayout.addWidget(self.navigateUpButton)

        self.layout().addLayout(self.headerLayout)

        self.contentSplitter = QtGui.QSplitter()

        self.bookmarksList = QtGui.QListView()
        self.contentSplitter.addWidget(self.bookmarksList)

        self.view = QtGui.QTableView()
        self.view.setSelectionBehavior(self.view.SelectRows)
        self.view.setSelectionMode(self.view.SingleSelection)
        self.view.verticalHeader().hide()

        self.contentSplitter.addWidget(self.view)

        proxy = ftrack_connect.ui.model.entity_tree.EntityTreeProxyModel(self)
        model = ftrack_connect.ui.model.entity_tree.EntityTreeModel(
            root=self._root, parent=self
        )
        proxy.setSourceModel(model)
        proxy.setDynamicSortFilter(True)

        self.view.setModel(proxy)
        self.view.setSortingEnabled(True)

        self.contentSplitter.setStretchFactor(1, 1)
        self.layout().addWidget(self.contentSplitter)

        self.footerLayout = QtGui.QHBoxLayout()
        self.footerLayout.addStretch(1)

        self.cancelButton = QtGui.QPushButton('Cancel')
        self.footerLayout.addWidget(self.cancelButton)

        self.acceptButton = QtGui.QPushButton('Choose')
        self.footerLayout.addWidget(self.acceptButton)

        self.layout().addLayout(self.footerLayout)

        self.overlay = ftrack_connect.ui.widget.overlay.BusyOverlay(
            self.view, message='Loading'
        )

    def _postConstruction(self):
        '''Perform post-construction operations.'''
        self.setWindowTitle('ftrack browser')
        self.view.sortByColumn(0, QtCore.Qt.AscendingOrder)

        # TODO: Remove once bookmarks widget implemented.
        self.bookmarksList.hide()

        self.acceptButton.setDefault(True)
        self.acceptButton.setDisabled(True)

        self.model.sourceModel().loadStarted.connect(self.overlay.show)
        self.model.sourceModel().loadEnded.connect(self.overlay.hide)

        self.view.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents
        )
        self.view.horizontalHeader().setResizeMode(
            0, QtGui.QHeaderView.Stretch
        )

        self.navigationBar.currentChanged.connect(
            self._onSelectNavigationBarItem
        )
        self.navigateUpButton.clicked.connect(self._onNavigateUpButtonClicked)
        self.view.activated.connect(self._onActivateItem)

        selectionModel = self.view.selectionModel()
        selectionModel.currentRowChanged.connect(self._onSelectItem)

        self._updateNavigationBar()

    @property
    def model(self):
        '''Return current model.'''
        return self.view.model()

    def selected(self):
        '''Return selected entities.'''
        return self._selected[:]

    def setLocationFromIndex(self, index):
        '''Set location to *index*.'''
        if index is None:
            index = QtCore.QModelIndex()

        self.view.setRootIndex(index)
        self._updateNavigationBar()

    def _updateNavigationBar(self):
        '''Update navigation bar.'''
        if self._updatingNavigationBar:
            return

        self._updatingNavigationBar = True

        # Clear all existing entries.
        for index in range(self.navigationBar.count(), -1, -1):
            self.navigationBar.removeTab(index)

        # Compute new entries.
        entries = []
        index = self.view.rootIndex()
        while index.isValid():
            item = self.model.item(index)
            entries.append(
                dict(icon=item.icon, label=item.name, index=index)
            )
            index = self.model.parent(index)

        item = self.model.root
        entries.append(
            dict(icon=item.icon, label=item.name, index=None)
        )

        entries.reverse()
        for entry in entries:
            tabIndex = self.navigationBar.addTab(entry['icon'], entry['label'])
            self.navigationBar.setTabData(tabIndex, entry['index'])
            self.navigationBar.setCurrentIndex(tabIndex)

        self._updatingNavigationBar = False

    def _onSelectNavigationBarItem(self, index):
        '''Handle selection of navigation bar item.'''
        if index < 0:
            return

        if self._updatingNavigationBar:
            return

        modelIndex = self.navigationBar.tabData(index)
        self.setLocationFromIndex(modelIndex)

    def _onActivateItem(self, index):
        '''Handle activation of item in listing.'''
        if self.model.hasChildren(index):
            self.acceptButton.setDisabled(True)
            self.setLocationFromIndex(index)

    def _onSelectItem(self, selection, previousSelection):
        '''Handle selection of item in listing.'''
        self.acceptButton.setEnabled(True)
        del self._selected[:]
        item = self.model.item(selection)
        self._selected.append(item.entity)

    def _onNavigateUpButtonClicked(self):
        '''Navigate up on button click.'''
        currentRootIndex = self.view.rootIndex()
        parent = self.model.parent(currentRootIndex)
        self.setLocationFromIndex(parent)
