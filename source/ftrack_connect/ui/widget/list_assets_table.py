import sys

from PySide import QtCore, QtGui
import ftrack

from ftrack_connect.connector import FTAssetHandlerInstance

class Ui_AssetVersionDetails(object):
    def setupUi(self, AssetVersionDetails):
        AssetVersionDetails.setObjectName("AssetVersionDetails")
        AssetVersionDetails.resize(180, 424)
        AssetVersionDetails.setMinimumSize(QtCore.QSize(180, 0))
        AssetVersionDetails.setMaximumSize(QtCore.QSize(180, 16777215))
        self.horizontalLayout = QtGui.QHBoxLayout(AssetVersionDetails)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtGui.QSpacerItem(20, 75, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.AssetVersionImageLabel = QtGui.QLabel(AssetVersionDetails)
        self.AssetVersionImageLabel.setMinimumSize(QtCore.QSize(180, 120))
        self.AssetVersionImageLabel.setMaximumSize(QtCore.QSize(180, 120))
        self.AssetVersionImageLabel.setText("")
        self.AssetVersionImageLabel.setObjectName("AssetVersionImageLabel")
        self.verticalLayout.addWidget(self.AssetVersionImageLabel)
        self.AssetVersionDetailsLabel = QtGui.QLabel(AssetVersionDetails)
        self.AssetVersionDetailsLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.AssetVersionDetailsLabel.setWordWrap(True)
        self.AssetVersionDetailsLabel.setObjectName("AssetVersionDetailsLabel")
        self.verticalLayout.addWidget(self.AssetVersionDetailsLabel)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(AssetVersionDetails)
        QtCore.QMetaObject.connectSlotsByName(AssetVersionDetails)

    def retranslateUi(self, AssetVersionDetails):
        AssetVersionDetails.setWindowTitle(QtGui.QApplication.translate("AssetVersionDetails", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.AssetVersionDetailsLabel.setText(QtGui.QApplication.translate("AssetVersionDetails", "No asset selected", None, QtGui.QApplication.UnicodeUTF8))


class ListAssetsTableWidget(QtGui.QWidget):
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
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        self.optionsLayout = QtGui.QHBoxLayout()
        self.assetTypeSelector = QtGui.QComboBox()
        self.optionsLayout.addWidget(self.assetTypeSelector)
        
        self.refreshButton = QtGui.QPushButton(self.tr('Refresh'))
        self.optionsLayout.addWidget(self.refreshButton)
        self.optionsLayout.addStretch(1)
        
        self.layout().addLayout(self.optionsLayout)
        
        self.assetTable = QtGui.QTableWidget()
        self.assetTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.assetTable.setSelectionMode(
            QtGui.QAbstractItemView.SingleSelection
        )
        self.assetTable.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows
        )
        
        self.assetTable.setColumnCount(len(self.assetTableColumns))
        self.assetTable.setRowCount(0)
        self.assetTable.verticalHeader().hide()
        
        self.assetTable.setHorizontalHeaderLabels(self.assetTableColumns)
        
        horizontalHeader = self.assetTable.horizontalHeader()
        horizontalHeader.setResizeMode(QtGui.QHeaderView.Fixed)

        self.assetTable.horizontalHeader().setDefaultSectionSize(100)
        self.assetTable.setColumnWidth(1, 63)
        self.assetTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)

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
        selectedRows = self.assetTable.selectionModel().selectedRows()
        try:
            selRow = selectedRows[0].row()
        except:
            selRow = 0
        '''Refresh view using latest FTrack id.'''
        self.updateView(self.latestFtrackId)
        
        self.onVersionSelected(selRow)

    @QtCore.Slot(str)
    def initView(self, ftrackId=None):
        self.updateView(ftrackId)
        if self.assetTable.rowCount()>0:
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
                    item = QtGui.QTableWidgetItem(assetName)
                    item.id = assets[i].getId()
                    item.setToolTip(assetName)

                    j = i - blankRows
                    self.assetTable.setItem(j, column('Asset'), item)

                    self.assetTable.setItem(
                        j, column('Author'), QtGui.QTableWidgetItem('')
                    )

                    self.assetTable.setItem(
                        j, column('Date'), QtGui.QTableWidgetItem('')
                    )
                    
                    assetType = assets[i].getType()
                    itemType = QtGui.QTableWidgetItem(assetType.getShort())
                    self.assetTable.setItem(j, column('Asset Type Code'),
                                            itemType)

                    itemTypeLong = QtGui.QTableWidgetItem(assetType.getName())
                    self.assetTable.setItem(j, column('Asset Type'),
                                            itemTypeLong)
                    
                    assetVersions = assets[i].getVersions()
                    versionComboBox = QtGui.QComboBox()
                    self.assetTable.setCellWidget(j, column('Version'),
                                                  versionComboBox)
                    
                    # Populate version list
                    for version in reversed(assetVersions):
                        versionComboBox.addItem(
                            str(version.getVersion()),
                            version
                        )
                    
                    author = QtGui.QTableWidgetItem(assetVersions[-1].getUser().getName())
                    self.assetTable.setItem(j, column('Author'), author)
                    
                    author = QtGui.QTableWidgetItem(assetVersions[-1].getDate().strftime('%Y-%m-%d %H:%M'))
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
            import traceback
            traceback.print_exc(file=sys.stdout)

    @QtCore.Slot(int)
    def onVersionSelected(self, row):
        '''Handle change of version.'''
        versionComboBox = self.assetTable.cellWidget(
            row, self.assetTableColumns.index('Version')
        )
        version = versionComboBox.itemData(versionComboBox.currentIndex())
        
        self.assetVersionSelectedSignal.emit(version.getId())
        self.emitAssetType(row)
        
        self.assetTable.selectionModel().clearSelection()
        index = self.assetTable.model().index(row, 0)
        self.assetTable.selectionModel().select(
            index,
            QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows
        )

        # Temporary alias
        column = self.assetTableColumns.index
        
        # Update version specific fields
        authorItem = self.assetTable.item(row, column('Author'))
        authorItem.setText(version.getUser().getName())
        
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
