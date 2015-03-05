# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import getpass

from PySide import QtCore, QtGui

import ftrack_legacy as ftrack

from ftrack_connect.connector import FTAssetObject, PanelComInstance
from ftrack_connect.ui.widget.info import FtrackInfoDialog
from ftrack_connect.ui.widget import header
from ftrack_connect.ui.theme import applyTheme
from ftrack_connect.ui import resource


class Ui_AssetManager(object):
    '''Class to generate asset manager ui.'''

    def setupUi(self, AssetManager):
        '''Setup ui for *AssetManager*.'''
        AssetManager.setObjectName('AssetManager')
        AssetManager.resize(549, 419)
        self.verticalLayout = QtGui.QVBoxLayout(AssetManager)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName('verticalLayout')
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName('horizontalLayout')
        self.AssetManagerComboBox = QtGui.QComboBox(AssetManager)
        self.AssetManagerComboBox.setMaximumSize(QtCore.QSize(120, 16777215))
        self.AssetManagerComboBox.setObjectName('AssetManagerComboBox')
        self.horizontalLayout.addWidget(self.AssetManagerComboBox)
        self.versionDownButton = QtGui.QPushButton(AssetManager)
        self.versionDownButton.setMinimumSize(QtCore.QSize(20, 0))
        self.versionDownButton.setMaximumSize(QtCore.QSize(20, 16777215))
        self.versionDownButton.setObjectName('versionDownButton')
        self.horizontalLayout.addWidget(self.versionDownButton)
        self.versionUpButton = QtGui.QPushButton(AssetManager)
        self.versionUpButton.setMinimumSize(QtCore.QSize(20, 0))
        self.versionUpButton.setMaximumSize(QtCore.QSize(20, 16777215))
        self.versionUpButton.setObjectName('versionUpButton')
        self.horizontalLayout.addWidget(self.versionUpButton)
        self.latestButton = QtGui.QPushButton(AssetManager)
        self.latestButton.setMinimumSize(QtCore.QSize(60, 0))
        self.latestButton.setMaximumSize(QtCore.QSize(60, 16777215))
        self.latestButton.setObjectName('latestButton')
        self.horizontalLayout.addWidget(self.latestButton)
        self.selectAllButton = QtGui.QPushButton(AssetManager)
        self.selectAllButton.setMinimumSize(QtCore.QSize(80, 0))
        self.selectAllButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.selectAllButton.setObjectName('selectAllButton')
        self.horizontalLayout.addWidget(self.selectAllButton)
        self.menuButton = QtGui.QPushButton(AssetManager)
        self.menuButton.setMaximumSize(QtCore.QSize(70, 16777215))
        self.menuButton.setObjectName('menuButton')
        self.horizontalLayout.addWidget(self.menuButton)
        self.whiteSpaceLabel = QtGui.QLabel(AssetManager)
        self.whiteSpaceLabel.setText('')
        self.whiteSpaceLabel.setObjectName('whiteSpaceLabel')
        self.horizontalLayout.addWidget(self.whiteSpaceLabel)
        self.refreshButton = QtGui.QPushButton(AssetManager)
        self.refreshButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.refreshButton.setObjectName('refreshButton')
        self.horizontalLayout.addWidget(self.refreshButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.AssertManagerTableWidget = QtGui.QTableWidget(AssetManager)
        self.AssertManagerTableWidget.setFrameShape(QtGui.QFrame.Box)
        self.AssertManagerTableWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.AssertManagerTableWidget.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows
        )
        self.AssertManagerTableWidget.setObjectName('AssertManagerTableWidget')
        self.AssertManagerTableWidget.setColumnCount(0)
        self.AssertManagerTableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.AssertManagerTableWidget)

        self.retranslateUi(AssetManager)
        QtCore.QObject.connect(
            self.refreshButton, QtCore.SIGNAL('clicked()'),
            AssetManager.refreshAssetManager
        )
        QtCore.QObject.connect(
            self.AssetManagerComboBox,
            QtCore.SIGNAL('currentIndexChanged(int)'),
            AssetManager.filterAssets
        )
        QtCore.QObject.connect(
            self.versionDownButton,
            QtCore.SIGNAL('clicked()'),
            AssetManager.versionDownSelected
        )
        QtCore.QObject.connect(
            self.versionUpButton,
            QtCore.SIGNAL('clicked()'),
            AssetManager.versionUpSelected
        )
        QtCore.QObject.connect(
            self.latestButton,
            QtCore.SIGNAL('clicked()'),
            AssetManager.versionLatestSelected
        )
        QtCore.QObject.connect(
            self.selectAllButton,
            QtCore.SIGNAL('clicked()'),
            AssetManager.selectAll
        )
        QtCore.QMetaObject.connectSlotsByName(AssetManager)

    def retranslateUi(self, AssetManager):
        '''Retranslate ui for *AssetManager*.'''
        AssetManager.setWindowTitle(
            QtGui.QApplication.translate(
                'AssetManager', 'Form', None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.versionDownButton.setText(
            QtGui.QApplication.translate(
                'AssetManager', '-', None, QtGui.QApplication.UnicodeUTF8)
        )
        self.versionUpButton.setText(
            QtGui.QApplication.translate(
                'AssetManager', '+', None, QtGui.QApplication.UnicodeUTF8)
        )
        self.latestButton.setText(
            QtGui.QApplication.translate(
                'AssetManager', 'Latest', None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.selectAllButton.setText(
            QtGui.QApplication.translate(
                'AssetManager', 'Select All', None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
        self.menuButton.setText(
            QtGui.QApplication.translate(
                'AssetManager', 'Extra', None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.refreshButton.setText(
            QtGui.QApplication.translate(
                'AssetManager', 'Refresh', None, QtGui.QApplication.UnicodeUTF8
            )
        )


class FtrackAssetManagerDialog(QtGui.QDialog):
    '''Class to represent an asset manager dialog.'''

    def __init__(self, parent=None, connector=None):
        '''Instantiate asset manager dialog with *connector*.'''
        super(FtrackAssetManagerDialog, self).__init__(parent=parent)
        applyTheme(self, 'integration')
        if not connector:
            raise ValueError(
                'Please provide a connector object for {0}'.format(
                    self.__class__.__name__
                )
            )

        self.connector = connector
        self.setMinimumWidth(400)
        self.setSizePolicy(
            QtGui.QSizePolicy(
                QtGui.QSizePolicy.Expanding,
                QtGui.QSizePolicy.Expanding
            )
        )

        self.centralwidget = QtGui.QWidget(self)
        self.verticalMainLayout = QtGui.QVBoxLayout(self)
        self.verticalMainLayout.setSpacing(6)
        self.horizontalLayout = QtGui.QHBoxLayout()

        self.headerWidget = header.Header(getpass.getuser(), self)
        self.verticalMainLayout.addWidget(self.headerWidget)

        self.assetManagerWidget = AssetManagerWidget(
            parent=self.centralwidget,
            connector=self.connector
        )

        self.horizontalLayout.addWidget(self.assetManagerWidget)
        self.verticalMainLayout.addLayout(self.horizontalLayout)

        self.setObjectName('ftrackAssetManager')
        self.setWindowTitle('ftrackAssetManager')

        panelComInstance = PanelComInstance.instance()
        panelComInstance.addRefreshListener(
            self.assetManagerWidget.refreshAssetManager
        )


class AssetManagerWidget(QtGui.QWidget):
    '''Asset manager widget'''

    notVersionable = dict()
    notVersionable['maya'] = ['alembic']

    def __init__(self, parent, task=None, connector=None):
        '''Instantiate asset manager with *connector*.'''
        QtGui.QWidget.__init__(self, parent)

        if not connector:
            raise ValueError(
                'Please provide a connector object for {0}'.format(
                    self.__class__.__name__
                )
            )

        self.connector = connector

        self.ui = Ui_AssetManager()
        self.ui.setupUi(self)
        self.setMinimumWidth(500)
        self.ui.AssertManagerTableWidget.setSortingEnabled(True)
        self.ui.AssertManagerTableWidget.setShowGrid(False)

        self.ui.AssertManagerTableWidget.verticalHeader().hide()
        self.ui.AssertManagerTableWidget.setColumnCount(16)
        self.ui.AssertManagerTableWidget.horizontalHeader().setDefaultSectionSize(65)
        self.ui.AssertManagerTableWidget.setColumnWidth(0, 20)
        self.ui.AssertManagerTableWidget.setColumnWidth(5, 55)
        self.ui.AssertManagerTableWidget.setColumnWidth(6, 65)
        self.ui.AssertManagerTableWidget.setColumnWidth(9, 20)
        self.ui.AssertManagerTableWidget.setColumnWidth(10, 20)
        self.ui.AssertManagerTableWidget.setColumnWidth(11, 20)
        self.ui.AssertManagerTableWidget.setColumnWidth(15, 20)
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            0, QtGui.QHeaderView.Fixed
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            5, QtGui.QHeaderView.Fixed
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            6, QtGui.QHeaderView.Fixed
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            9, QtGui.QHeaderView.Fixed
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            10, QtGui.QHeaderView.Fixed
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            11, QtGui.QHeaderView.Fixed
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            15, QtGui.QHeaderView.Fixed
        )

        self.ui.AssertManagerTableWidget.setColumnHidden(2, True)
        self.ui.AssertManagerTableWidget.setColumnHidden(3, True)
        self.ui.AssertManagerTableWidget.setColumnHidden(6, True)
        self.ui.AssertManagerTableWidget.setColumnHidden(10, True)
        self.ui.AssertManagerTableWidget.setColumnHidden(12, True)
        self.ui.AssertManagerTableWidget.setColumnHidden(13, True)
        self.ui.AssertManagerTableWidget.setColumnHidden(14, True)

        self.columnHeaders = [
            '', 'Component', 'CmpId', 'AssetTypeShort',
            'Type', 'Version', 'LatestV', 'Name',
            'SceneName', '', '', '', 'AssetId',
            'AssetVersionId', 'CurrentVersionFallback', ''
        ]

        self.ui.AssertManagerTableWidget.setHorizontalHeaderLabels(
            self.columnHeaders
        )

        self.ui.AssetManagerComboBoxModel = QtGui.QStandardItemModel()

        assetTypes = ftrack.getAssetTypes()
        assetTypes = sorted(assetTypes, key=lambda a: a.getName().lower())

        assetTypeItem = QtGui.QStandardItem('Show All')
        self.ui.AssetManagerComboBoxModel.appendRow(assetTypeItem)

        for assetType in assetTypes:
            assetTypeItem = QtGui.QStandardItem(assetType.getName())
            assetTypeItem.type = assetType.getShort()
            self.ui.AssetManagerComboBoxModel.appendRow(assetTypeItem)

        self.ui.AssetManagerComboBox.setModel(self.ui.AssetManagerComboBoxModel)

        self.signalMapperSelect = QtCore.QSignalMapper()
        QtCore.QObject.connect(
            self.signalMapperSelect,
            QtCore.SIGNAL('mapped(QString)'),
            self.selectObject
        )

        self.signalMapperRemove = QtCore.QSignalMapper()
        QtCore.QObject.connect(
            self.signalMapperRemove,
            QtCore.SIGNAL('mapped(QString)'),
            self.removeObject
        )

        self.signalMapperComment = QtCore.QSignalMapper()
        QtCore.QObject.connect(
            self.signalMapperComment,
            QtCore.SIGNAL('mapped(QString)'),
            self.openComments
        )

        self.signalMapperChangeVersion = QtCore.QSignalMapper()
        QtCore.QObject.connect(
            self.signalMapperChangeVersion,
            QtCore.SIGNAL('mapped(int)'),
            self.changeVersion
        )

        extraOptionsMenu = QtGui.QMenu(self.ui.menuButton)
        extraOptionsMenu.addAction('Get SceneSelection', self.getSceneSelection)
        extraOptionsMenu.addAction('Set SceneSelection', self.setSceneSelection)
        self.ui.menuButton.setMenu(extraOptionsMenu)

        self.refreshAssetManager()

    @QtCore.Slot()
    def refreshAssetManager(self):
        '''Refresh assets in asset manager.'''
        assets = self.connector.getAssets()

        self.ui.AssertManagerTableWidget.setSortingEnabled(False)
        self.ui.AssertManagerTableWidget.setRowCount(0)

        self.ui.AssertManagerTableWidget.setRowCount(len(assets))

        for i in range(len(assets)):
            if assets[i][0]:
                ftrackComponent = ftrack.Component(assets[i][0])
                assetVersion = ftrackComponent.getVersion()
                componentNameStr = ftrackComponent.getName()
                assetVersionNr = assetVersion.getVersion()
                asset = assetVersion.getAsset()

                assetVersions = asset.getVersions(
                    componentNames=[componentNameStr]
                )
                latestAssetVersion = assetVersions[-1].getVersion()

                versionIndicatorButton = QtGui.QPushButton('')
                if assetVersionNr == latestAssetVersion:
                    versionIndicatorButton.setStyleSheet(
                        'background-color: #1CBC90;'
                    )
                    self.connector.setNodeColor(
                        applicationObject=assets[i][1], latest=True
                    )
                else:
                    versionIndicatorButton.setStyleSheet(
                        'background-color: rgb(227, 99, 22);'
                    )
                    self.connector.setNodeColor(
                        applicationObject=assets[i][1], latest=False
                    )
                self.ui.AssertManagerTableWidget.setCellWidget(
                    i, 0, versionIndicatorButton
                )

                componentName = QtGui.QTableWidgetItem(componentNameStr)
                self.ui.AssertManagerTableWidget.setItem(i, 1, componentName)

                componentId = QtGui.QTableWidgetItem(ftrackComponent.getId())
                self.ui.AssertManagerTableWidget.setItem(i, 2, componentId)

                assetType = QtGui.QTableWidgetItem(asset.getType().getShort())
                self.ui.AssertManagerTableWidget.setItem(i, 3, assetType)

                assetTypeLong = QtGui.QTableWidgetItem(
                    asset.getType().getName()
                )
                self.ui.AssertManagerTableWidget.setItem(i, 4, assetTypeLong)

                versionNumberComboBox = QtGui.QComboBox()
                for version in reversed(assetVersions):
                    versionNumberComboBox.addItem(str(version.getVersion()))

                conName = self.connector.getConnectorName()
                if conName in self.notVersionable:
                    if componentNameStr in self.notVersionable[conName]:
                        versionNumberComboBox.setEnabled(False)

                result = versionNumberComboBox.findText(str(assetVersionNr))
                versionNumberComboBox.setCurrentIndex(result)

                self.ui.AssertManagerTableWidget.setCellWidget(
                    i, 5, versionNumberComboBox
                )
                QtCore.QObject.connect(
                    versionNumberComboBox,
                    QtCore.SIGNAL('currentIndexChanged(QString)'),
                    self.signalMapperChangeVersion, QtCore.SLOT('map()')
                )
                self.signalMapperChangeVersion.setMapping(
                    versionNumberComboBox, -1
                )

                latestVersionNumber = QtGui.QTableWidgetItem(
                    str(latestAssetVersion)
                )
                self.ui.AssertManagerTableWidget.setItem(
                    i, 6, latestVersionNumber
                )

                assetName = QtGui.QTableWidgetItem(str(asset.getName()))
                assetName.setToolTip(asset.getName())
                self.ui.AssertManagerTableWidget.setItem(i, 7, assetName)

                assetNameInScene = QtGui.QTableWidgetItem(assets[i][1])
                assetNameInScene.setToolTip(assets[i][1])
                self.ui.AssertManagerTableWidget.setItem(i, 8, assetNameInScene)

                selectButton = QtGui.QPushButton('S')
                selectButton.setToolTip('Select asset in scene')
                self.ui.AssertManagerTableWidget.setCellWidget(
                    i, 9, selectButton
                )

                QtCore.QObject.connect(
                    selectButton,
                    QtCore.SIGNAL('clicked()'),
                    self.signalMapperSelect,
                    QtCore.SLOT('map()')
                )
                self.signalMapperSelect.setMapping(selectButton, assets[i][1])

                replaceButton = QtGui.QPushButton('R')
                self.ui.AssertManagerTableWidget.setCellWidget(
                    i, 10, replaceButton
                )

                removeButton = QtGui.QPushButton()
                removeButton.setToolTip('Remove asset from scene')
                icon = QtGui.QIcon()
                icon.addPixmap(
                    QtGui.QPixmap(':ftrack/image/studio/trash'),
                    QtGui.QIcon.Normal,
                    QtGui.QIcon.Off
                )
                removeButton.setIcon(icon)
                self.ui.AssertManagerTableWidget.setCellWidget(
                    i, 11, removeButton
                )

                QtCore.QObject.connect(
                    removeButton,
                    QtCore.SIGNAL('clicked()'),
                    self.signalMapperRemove,
                    QtCore.SLOT('map()')
                )
                self.signalMapperRemove.setMapping(removeButton, assets[i][1])

                assetId = QtGui.QTableWidgetItem(str(asset.getId()))
                self.ui.AssertManagerTableWidget.setItem(i, 12, assetId)

                assetVersionId = QtGui.QTableWidgetItem(
                    str(assetVersion.getId())
                )
                self.ui.AssertManagerTableWidget.setItem(i, 13, assetVersionId)

                currentVersionFallback = QtGui.QTableWidgetItem(
                    str(assetVersionNr)
                )
                self.ui.AssertManagerTableWidget.setItem(
                    i, 14, currentVersionFallback
                )

                commentButton = QtGui.QPushButton()
                commentButton.setText('')
                icon = QtGui.QIcon()
                icon.addPixmap(
                    QtGui.QPixmap(':ftrack/image/studio/comment'), QtGui.QIcon.Normal,
                    QtGui.QIcon.Off
                )
                commentButton.setIcon(icon)

                fullUserName = assetVersion.getUser().getName()
                pubDate = str(assetVersion.getDate())
                comment = assetVersion.getComment()
                tooltipText = '\n'.join([fullUserName, pubDate, comment])

                commentButton.setToolTip(tooltipText)
                self.ui.AssertManagerTableWidget.setCellWidget(
                    i, 15, commentButton
                )
                QtCore.QObject.connect(
                    commentButton,
                    QtCore.SIGNAL('clicked()'),
                    self.signalMapperComment,
                    QtCore.SLOT('map()')
                )

                self.signalMapperComment.setMapping(
                    commentButton, str(assetVersion.getId())
                )

        self.ui.AssertManagerTableWidget.setHorizontalHeaderLabels(
            self.columnHeaders
        )

    def openComments(self, taskId):
        '''Open comments dialog for *taskId*.'''
        self.comment_dialog = FtrackInfoDialog(connector=self.connector)
        self.comment_dialog.show()
        self.comment_dialog.move(
            QtGui.QApplication.desktop().screen().rect().center()
            - self.comment_dialog.rect().center()
        )
        panelComInstance = PanelComInstance.instance()
        panelComInstance.infoListeners(taskId)

    @QtCore.Slot(int)
    def filterAssets(self, comboBoxIndex):
        '''Filter asset based on *comboBoxIndex*.'''
        rowCount = self.ui.AssertManagerTableWidget.rowCount()
        if comboBoxIndex:
            comboItem = self.ui.AssetManagerComboBoxModel.item(comboBoxIndex)
            for i in range(rowCount):
                tableItem = self.ui.AssertManagerTableWidget.item(i, 2)

                if comboItem.type != tableItem.text():

                    self.ui.AssertManagerTableWidget.setRowHidden(i, True)
                else:

                    self.ui.AssertManagerTableWidget.setRowHidden(i, False)

        else:
            for i in range(rowCount):
                self.ui.AssertManagerTableWidget.setRowHidden(i, False)

    @QtCore.Slot(str)
    def selectObject(self, objectName):
        '''Select object in scene from *objectName*.'''
        self.connector.selectObject(applicationObject=objectName)

    @QtCore.Slot(str)
    def removeObject(self, objectName):
        '''Remove object with *objectName* from scene.'''
        msgBox = QtGui.QMessageBox()
        msgBox.setText('Remove asset.')
        msgBox.setInformativeText('Are you sure you want to remove the asset?')
        msgBox.setStandardButtons(
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel
        )
        msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
        ret = msgBox.exec_()
        if ret == QtGui.QMessageBox.Ok:
            self.connector.removeObject(applicationObject=objectName)
            foundItem = self.ui.AssertManagerTableWidget.findItems(
                objectName, QtCore.Qt.MatchExactly
            )
            self.ui.AssertManagerTableWidget.removeRow(foundItem[0].row())
            self.refreshAssetManager()

    def getSelectedRows(self):
        '''Return selected rows.'''
        rows = []
        for idx in self.ui.AssertManagerTableWidget.selectionModel().selectedRows():
            rows.append(idx.row())
        return rows

    def versionDownSelected(self):
        '''Version down selected assets.'''
        rows = self.getSelectedRows()
        for row in rows:
            currentComboIndex = self.ui.AssertManagerTableWidget.cellWidget(
                row, 5
            ).currentIndex()
            indexCount = self.ui.AssertManagerTableWidget.cellWidget(
                row, 5
            ).count()
            newIndex = min(currentComboIndex + 1, indexCount - 1)
            self.ui.AssertManagerTableWidget.cellWidget(
                row, 5
            ).setCurrentIndex(newIndex)
            newVersion = self.ui.AssertManagerTableWidget.cellWidget(
                row, 5
            ).currentText()
            self.changeVersion(row, newVersion)

    def versionUpSelected(self):
        '''Version up selected assets.'''
        rows = self.getSelectedRows()
        for row in rows:
            currentComboIndex = self.ui.AssertManagerTableWidget.cellWidget(
                row, 5
            ).currentIndex()
            newIndex = max(currentComboIndex - 1, 0)
            self.ui.AssertManagerTableWidget.cellWidget(
                row, 5
            ).setCurrentIndex(newIndex)
            newVersion = self.ui.AssertManagerTableWidget.cellWidget(
                row, 5
            ).currentText()
            self.changeVersion(row, newVersion)

    def versionLatestSelected(self):
        '''Version up assets to latest.'''
        rows = self.getSelectedRows()
        for row in rows:
            newIndex = 0
            self.ui.AssertManagerTableWidget.cellWidget(
                row, 5
            ).setCurrentIndex(newIndex)
            newVersion = self.ui.AssertManagerTableWidget.cellWidget(
                row, 5
            ).currentText()
            self.changeVersion(row, newVersion)

    def selectAll(self):
        '''Select all assets rows.'''
        rowCount = self.ui.AssertManagerTableWidget.rowCount()
        for row in range(0, rowCount):
            index = self.ui.AssertManagerTableWidget.model().index(row, 0)
            selModel = self.ui.AssertManagerTableWidget.selectionModel()
            selModel.select(
                index,
                QtGui.QItemSelectionModel.Select |
                QtGui.QItemSelectionModel.Rows
            )

    def getSceneSelection(self):
        '''Get selection from scene.'''
        selectedAssets = self.connector.getSelectedAssets()
        self.ui.AssertManagerTableWidget.selectionModel().clearSelection()
        for asset in selectedAssets:
            foundItem = self.ui.AssertManagerTableWidget.findItems(
                asset, QtCore.Qt.MatchExactly
            )
            index = self.ui.AssertManagerTableWidget.indexFromItem(foundItem[0])
            selModel = self.ui.AssertManagerTableWidget.selectionModel()
            selModel.select(
                index, QtGui.QItemSelectionModel.Select |
                QtGui.QItemSelectionModel.Rows
            )

    def setSceneSelection(self):
        '''Set scene selection from selected rows.'''
        rows = self.getSelectedRows()
        objectNames = []
        for row in rows:
            objectName = self.ui.AssertManagerTableWidget.item(row, 8).text()
            objectNames.append(objectName)
        self.connector.selectObjects(objectNames)

    def getCurrenRow(self):
        '''Return current row.'''
        fw = QtGui.QApplication.focusWidget()
        modelindexComboBox = self.ui.AssertManagerTableWidget.indexAt(fw.pos())
        row = modelindexComboBox.row()
        return row

    @QtCore.Slot(int, str)
    def changeVersion(self, row, newVersion=None):
        '''Change version of asset at *row* to *newVersion*.'''
        if row == -1:
            row = self.getCurrenRow()

        if not newVersion:
            newVersion = self.ui.AssertManagerTableWidget.cellWidget(
                row, 5
            ).currentText()

        latestVersion = self.ui.AssertManagerTableWidget.item(row, 6).text()
        objectName = self.ui.AssertManagerTableWidget.item(row, 8).text()
        componentName = self.ui.AssertManagerTableWidget.item(row, 1).text()
        assetId = self.ui.AssertManagerTableWidget.item(row, 12).text()
        currentVersion = self.ui.AssertManagerTableWidget.item(row, 14).text()

        ftrackAsset = ftrack.Asset(assetId)
        assetVersions = ftrackAsset.getVersions()
        newftrackAssetVersion = assetVersions[int(newVersion) - 1]
        try:
            newComponent = newftrackAssetVersion.getComponent(componentName)
        except:
            print 'Could not getComponent for main. Trying with sequence'
            componentName = 'sequence'
            newComponent = newftrackAssetVersion.getComponent(componentName)

        location = ftrack.pickLocation(newComponent.getId())
        if location is None:
            raise ftrack.FTrackError(
                'Cannot load version data as no accessible location '
                'containing the version is available.'
            )

        newComponent = location.getComponent(newComponent.getId())

        path = newComponent.getFilesystemPath()
        importObj = FTAssetObject(
            filePath=path,
            componentName=componentName,
            componentId=newComponent.getId(),
            assetVersionId=newftrackAssetVersion.getId()
        )

        result = self.connector.changeVersion(
            iAObj=importObj,
            applicationObject=objectName
        )

        if result:
            cellWidget = self.ui.AssertManagerTableWidget.cellWidget(row, 0)
            if newVersion == latestVersion:
                cellWidget.setStyleSheet('background-color: rgb(20, 161, 74);')
                self.connector.setNodeColor(
                    applicationObject=objectName, latest=True
                )
            else:
                cellWidget.setStyleSheet('background-color: rgb(227, 99, 22);')
                self.connector.setNodeColor(
                    applicationObject=objectName, latest=False
                )

            self.ui.AssertManagerTableWidget.item(
                row, 14
            ).setText(str(newVersion))
        else:
            cellWidget = self.ui.AssertManagerTableWidget.cellWidget(row, 5)
            fallbackIndex = cellWidget.findText(currentVersion)
            cellWidget.setCurrentIndex(fallbackIndex)
