# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import sys
import traceback

from QtExt import QtCore, QtWidgets, QtGui
import ftrack

from ftrack_connect.connector import FTAssetHandlerInstance


class ListAssetsTableWidget(QtWidgets.QWidget):
    '''View assets as a table.'''

    assetTypeSelectedSignal = QtCore.Signal(str)
    assetVersionSelectedSignal = QtCore.Signal(str)

    def __init__(self, parent=None):
        '''Initialise widget.'''
        super(ListAssetsTableWidget, self).__init__(parent)
        self.currentAssetType = None
        self.latestFtrackId = None
        self.assetTableColumns = (
            'Asset', 'Version', 'Date', 'Asset Type', 'Author',
            'Asset Type Code'
        )
        self.build()
        self.postBuild()

    def build(self):
        '''Build widgets and layout.'''
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.optionsLayout = QtWidgets.QHBoxLayout()
        self.assetTypeSelector = QtWidgets.QComboBox()
        self.optionsLayout.addWidget(self.assetTypeSelector)

        self.refreshButton = QtWidgets.QPushButton(self.tr('Refresh'))
        self.optionsLayout.addWidget(self.refreshButton)
        self.optionsLayout.addStretch(1)

        self.layout().addLayout(self.optionsLayout)

        self.assetTable = QtWidgets.QTableWidget()
        self.assetTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.assetTable.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )
        self.assetTable.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )

        self.assetTable.setColumnCount(len(self.assetTableColumns))
        self.assetTable.setRowCount(0)
        self.assetTable.verticalHeader().hide()

        self.assetTable.setHorizontalHeaderLabels(self.assetTableColumns)

        horizontalHeader = self.assetTable.horizontalHeader()
        horizontalHeader.setResizeMode(QtWidgets.QHeaderView.Fixed)

        self.assetTable.horizontalHeader().setDefaultSectionSize(100)
        self.assetTable.setColumnWidth(1, 63)
        self.assetTable.horizontalHeader().setResizeMode(
            0, QtWidgets.QHeaderView.Stretch
        )

        self.layout().addWidget(self.assetTable)

    def postBuild(self):
        '''Perform post build operations.'''
        self.assetTableSignalMapper = QtCore.QSignalMapper(self)
        self.assetTableSignalMapper.mapped[int].connect(self.onVersionSelected)

        self.assetTable.horizontalHeader().hideSection(
            self.assetTableColumns.index('Asset Type Code')
        )

        self.assetTypeSelectorModel = QtGui.QStandardItemModel()
        self.assetTypeSelector.setModel(self.assetTypeSelectorModel)

        self.assetTable.clicked.connect(self.rowSelectedEmitSignal)
        self.assetTypeSelector.currentIndexChanged.connect(self.filterAssets)
        self.refreshButton.clicked.connect(self.refreshView)

        self.updateAssetTypeOptions()

    def updateAssetTypeOptions(self):
        '''Update list of asset types to filter by.'''
        self.assetTypeSelectorModel.clear()

        assetTypes = ftrack.getAssetTypes()
        assetTypes = sorted(
            assetTypes,
            key=lambda assetType: assetType.getName().lower()
        )

        assetTypeItem = QtGui.QStandardItem('Show All')
        self.assetTypeSelectorModel.appendRow(assetTypeItem)

        assetHandler = FTAssetHandlerInstance.instance()
        assetTypesStr = sorted(assetHandler.getAssetTypes())

        for assetTypeStr in assetTypesStr:
            try:
                assetType = ftrack.AssetType(assetTypeStr)
            except:
                print assetTypeStr + ' not available in ftrack'
                continue

            assetTypeItem = QtGui.QStandardItem(assetType.getName())
            assetTypeItem.type = assetType.getShort()
            self.assetTypeSelectorModel.appendRow(assetTypeItem)

    @QtCore.Slot()
    def refreshView(self):
        '''Refresh view using latest id.'''
        selectedRows = self.assetTable.selectionModel().selectedRows()
        try:
            selRow = selectedRows[0].row()
        except:
            selRow = 0
        self.updateView(self.latestFtrackId)

        self.onVersionSelected(selRow)

    @QtCore.Slot(str)
    def initView(self, ftrackId=None):
        '''Initiate view with *ftrackId*.'''
        self.updateView(ftrackId)
        if self.assetTable.rowCount() > 0:
            self.onVersionSelected(0)

    @QtCore.Slot(str)
    def updateView(self, ftrackId=None):
        '''Update to view entity identified by *ftrackId*.'''
        self.latestFtrackId = ftrackId

        try:
            assetHandler = FTAssetHandlerInstance.instance()
            task = ftrack.Task(ftrackId)
            assets = task.getAssets(assetTypes=assetHandler.getAssetTypes())
            assets = sorted(assets, key=lambda a: a.getName().lower())
            self.assetTable.clearContents()
            self.assetTable.setRowCount(len(assets))
            blankRows = 0
            for i in range(len(assets)):
                assetName = assets[i].getName()
                assetVersions = assets[i].getVersions()

                # Temporary alias
                column = self.assetTableColumns.index

                if assetName != '' and assetVersions:
                    item = QtWidgets.QTableWidgetItem(assetName)
                    item.id = assets[i].getId()
                    item.setToolTip(assetName)

                    j = i - blankRows
                    self.assetTable.setItem(j, column('Asset'), item)

                    self.assetTable.setItem(
                        j, column('Author'), QtWidgets.QTableWidgetItem('')
                    )

                    self.assetTable.setItem(
                        j, column('Date'), QtWidgets.QTableWidgetItem('')
                    )

                    assetType = assets[i].getType()
                    itemType = QtWidgets.QTableWidgetItem(assetType.getShort())
                    self.assetTable.setItem(
                        j, column('Asset Type Code'), itemType
                    )

                    itemTypeLong = QtWidgets.QTableWidgetItem(assetType.getName())
                    self.assetTable.setItem(
                        j, column('Asset Type'), itemTypeLong
                    )

                    assetVersions = assets[i].getVersions()
                    versionComboBox = QtWidgets.QComboBox()
                    self.assetTable.setCellWidget(
                        j, column('Version'), versionComboBox
                    )

                    # Populate version list
                    for version in reversed(assetVersions):
                        versionComboBox.addItem(
                            str(version.getVersion()),
                            version
                        )

                    try:
                        authorName = assetVersions[-1].getUser().getName()
                    except ftrack.ftrackerror.FTrackError:
                        # This error can happen if a version does not have an user,
                        # for example if the user has been deleted after publishing
                        # the version.
                        authorName = 'No User Found'

                    author = QtWidgets.QTableWidgetItem(authorName)
                    self.assetTable.setItem(j, column('Author'), author)

                    author = QtWidgets.QTableWidgetItem(
                        assetVersions[-1].getDate().strftime('%Y-%m-%d %H:%M')
                    )
                    self.assetTable.setItem(j, column('Date'), author)

                    # Map version widget to row number to enable simple lookup
                    versionComboBox.currentIndexChanged[int].connect(
                        self.assetTableSignalMapper.map
                    )

                    self.assetTableSignalMapper.setMapping(versionComboBox, j)

                else:
                    blankRows += 1

            self.assetTable.setRowCount(len(assets) - blankRows)

        except:
            traceback.print_exc(file=sys.stdout)

    @QtCore.Slot(int)
    def onVersionSelected(self, row):
        '''Handle change of version.'''
        versionComboBox = self.assetTable.cellWidget(
            row, self.assetTableColumns.index('Version')
        )
        if not versionComboBox:
            return

        version = versionComboBox.itemData(versionComboBox.currentIndex())

        self.assetVersionSelectedSignal.emit(version.getId())
        self.emitAssetType(row)

        self.assetTable.selectionModel().clearSelection()
        index = self.assetTable.model().index(row, 0)
        self.assetTable.selectionModel().select(
            index,
            QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows
        )

        # Temporary alias
        column = self.assetTableColumns.index

        # Update version specific fields
        authorItem = self.assetTable.item(row, column('Author'))

        try:
            authorName = version.getUser().getName()
        except ftrack.ftrackerror.FTrackError:
            # This error can happen if a version does not have an user,
            # for example if the user has been deleted after publishing
            # the version.
            authorName = 'No User Found'

        authorItem.setText(authorName)

        dateItem = self.assetTable.item(row, column('Date'))
        dateItem.setText(version.getDate().strftime('%Y-%m-%d %H:%M'))

    @QtCore.Slot(QtCore.QModelIndex)
    def rowSelectedEmitSignal(self, modelindex):
        '''Handle asset selection.'''
        row = modelindex.row()
        versionComboBox = self.assetTable.cellWidget(
            row, self.assetTableColumns.index('Version')
        )
        version = versionComboBox.itemData(versionComboBox.currentIndex())
        self.assetVersionSelectedSignal.emit(version.getId())
        self.emitAssetType(row)

    @QtCore.Slot(int)
    def filterAssets(self, comboBoxIndex):
        '''Filter assets displayed by currently selected asset type.'''
        rowCount = self.assetTable.rowCount()
        if comboBoxIndex:
            comboItem = self.assetTypeSelectorModel.item(comboBoxIndex)
            self.currentAssetType = comboItem.type
            self.assetTypeSelectedSignal.emit(self.currentAssetType)
            for i in range(rowCount):
                tableItem = self.assetTable.item(
                    i,
                    self.assetTableColumns.index('Asset Type Code')
                )
                if comboItem.type != tableItem.text():
                    self.assetTable.setRowHidden(i, True)
                else:
                    self.assetTable.setRowHidden(i, False)
        else:
            for i in range(rowCount):
                self.assetTable.setRowHidden(i, False)

        return True

    def emitAssetType(self, row):
        '''Emit currently selected asset type.'''
        self.currentAssetType = self.assetTable.item(
            row,
            self.assetTableColumns.index('Asset Type Code')
        ).text()
        self.assetTypeSelectedSignal.emit(self.currentAssetType)

    def getAssetType(self):
        '''Return currently selected asset type.'''
        return self.currentAssetType
