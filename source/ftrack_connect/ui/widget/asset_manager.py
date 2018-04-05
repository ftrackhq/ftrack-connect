# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import getpass
import logging

from QtExt import QtCore, QtWidgets, QtGui, is_webwidget_supported

import ftrack
import ftrack_api

from ftrack_connect.connector import FTAssetObject, PanelComInstance

has_webwidgets = is_webwidget_supported()

if has_webwidgets:
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
        self.verticalLayout = QtWidgets.QVBoxLayout(AssetManager)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName('verticalLayout')
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName('horizontalLayout')
        self.AssetManagerComboBox = QtWidgets.QComboBox(AssetManager)
        self.AssetManagerComboBox.setMaximumSize(QtCore.QSize(120, 16777215))
        self.AssetManagerComboBox.setObjectName('AssetManagerComboBox')
        self.horizontalLayout.addWidget(self.AssetManagerComboBox)
        self.versionDownButton = QtWidgets.QPushButton(AssetManager)
        self.versionDownButton.setMinimumSize(QtCore.QSize(20, 0))
        self.versionDownButton.setMaximumSize(QtCore.QSize(20, 16777215))
        self.versionDownButton.setObjectName('versionDownButton')
        self.horizontalLayout.addWidget(self.versionDownButton)
        self.versionUpButton = QtWidgets.QPushButton(AssetManager)
        self.versionUpButton.setMinimumSize(QtCore.QSize(20, 0))
        self.versionUpButton.setMaximumSize(QtCore.QSize(20, 16777215))
        self.versionUpButton.setObjectName('versionUpButton')
        self.horizontalLayout.addWidget(self.versionUpButton)
        self.latestButton = QtWidgets.QPushButton(AssetManager)
        self.latestButton.setMinimumSize(QtCore.QSize(60, 0))
        self.latestButton.setMaximumSize(QtCore.QSize(60, 16777215))
        self.latestButton.setObjectName('latestButton')
        self.horizontalLayout.addWidget(self.latestButton)
        self.selectAllButton = QtWidgets.QPushButton(AssetManager)
        self.selectAllButton.setMinimumSize(QtCore.QSize(80, 0))
        self.selectAllButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.selectAllButton.setObjectName('selectAllButton')
        self.horizontalLayout.addWidget(self.selectAllButton)
        self.menuButton = QtWidgets.QPushButton(AssetManager)
        self.menuButton.setMaximumSize(QtCore.QSize(70, 16777215))
        self.menuButton.setObjectName('menuButton')
        self.horizontalLayout.addWidget(self.menuButton)
        self.whiteSpaceLabel = QtWidgets.QLabel(AssetManager)
        self.whiteSpaceLabel.setText('')
        self.whiteSpaceLabel.setObjectName('whiteSpaceLabel')
        self.horizontalLayout.addWidget(self.whiteSpaceLabel)
        self.refreshButton = QtWidgets.QPushButton(AssetManager)
        self.refreshButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.refreshButton.setObjectName('refreshButton')
        self.horizontalLayout.addWidget(self.refreshButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.AssertManagerTableWidget = QtWidgets.QTableWidget(AssetManager)
        self.AssertManagerTableWidget.setFrameShape(QtWidgets.QFrame.Box)
        self.AssertManagerTableWidget.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.AssertManagerTableWidget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        self.AssertManagerTableWidget.setObjectName('AssertManagerTableWidget')
        self.AssertManagerTableWidget.setColumnCount(0)
        self.AssertManagerTableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.AssertManagerTableWidget)

        self.retranslateUi(AssetManager)

        # Connect signals.
        self.refreshButton.clicked.connect(
            AssetManager.refreshAssetManager
        )

        self.AssetManagerComboBox.currentIndexChanged[int].connect(
            AssetManager.filterAssets
        )

        self.versionDownButton.clicked.connect(
            AssetManager.versionDownSelected
        )

        self.versionUpButton.clicked.connect(
            AssetManager.versionUpSelected
        )

        self.latestButton.clicked.connect(
            AssetManager.versionLatestSelected
        )

        self.selectAllButton.clicked.connect(
            AssetManager.selectAll
        )

        QtCore.QMetaObject.connectSlotsByName(AssetManager)

    def retranslateUi(self, AssetManager):
        '''Retranslate ui for *AssetManager*.'''
        AssetManager.setWindowTitle(
            QtWidgets.QApplication.translate(
                'AssetManager', 'Form', None, QtWidgets.QApplication.UnicodeUTF8
            )
        )
        self.versionDownButton.setText(
            QtWidgets.QApplication.translate(
                'AssetManager', '-', None, QtWidgets.QApplication.UnicodeUTF8)
        )
        self.versionUpButton.setText(
            QtWidgets.QApplication.translate(
                'AssetManager', '+', None, QtWidgets.QApplication.UnicodeUTF8)
        )
        self.latestButton.setText(
            QtWidgets.QApplication.translate(
                'AssetManager', 'Latest', None,
                QtWidgets.QApplication.UnicodeUTF8
            )
        )
        self.selectAllButton.setText(
            QtWidgets.QApplication.translate(
                'AssetManager', 'Select All', None,
                QtWidgets.QApplication.UnicodeUTF8
            )
        )
        self.menuButton.setText(
            QtWidgets.QApplication.translate(
                'AssetManager', 'Extra', None,
                QtWidgets.QApplication.UnicodeUTF8
            )
        )
        self.refreshButton.setText(
            QtWidgets.QApplication.translate(
                'AssetManager', 'Refresh', None,
                QtWidgets.QApplication.UnicodeUTF8
            )
        )


class FtrackAssetManagerDialog(QtWidgets.QDialog):
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
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
        )

        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalMainLayout = QtWidgets.QVBoxLayout(self)
        self.verticalMainLayout.setSpacing(6)
        self.horizontalLayout = QtWidgets.QHBoxLayout()

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


class AssetManagerWidget(QtWidgets.QWidget):
    '''Asset manager widget.'''

    notVersionable = dict()
    notVersionable['maya'] = []

    def __init__(self, parent, task=None, connector=None):
        '''Instantiate asset manager with *connector*.'''
        QtWidgets.QWidget.__init__(self, parent)
        
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

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
        self.ui.AssertManagerTableWidget.horizontalHeader(
        ).setDefaultSectionSize(65)
        self.ui.AssertManagerTableWidget.setColumnWidth(0, 20)
        self.ui.AssertManagerTableWidget.setColumnWidth(5, 55)
        self.ui.AssertManagerTableWidget.setColumnWidth(6, 65)
        self.ui.AssertManagerTableWidget.setColumnWidth(9, 20)
        self.ui.AssertManagerTableWidget.setColumnWidth(10, 20)
        self.ui.AssertManagerTableWidget.setColumnWidth(11, 20)
        self.ui.AssertManagerTableWidget.setColumnWidth(15, 20)
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            0, QtWidgets.QHeaderView.Fixed
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            5, QtWidgets.QHeaderView.Fixed
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            6, QtWidgets.QHeaderView.Fixed
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            9, QtWidgets.QHeaderView.Fixed
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            10, QtWidgets.QHeaderView.Fixed
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            11, QtWidgets.QHeaderView.Fixed
        )
        self.ui.AssertManagerTableWidget.horizontalHeader().setResizeMode(
            15, QtWidgets.QHeaderView.Fixed
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

        self.ui.AssetManagerComboBox.setModel(
            self.ui.AssetManagerComboBoxModel
        )

        self.signalMapperSelect = QtCore.QSignalMapper()
        self.signalMapperSelect.mapped[str].connect(self.selectObject)

        self.signalMapperRemove = QtCore.QSignalMapper()
        self.signalMapperRemove.mapped[str].connect(self.removeObject)

        self.signalMapperComment = QtCore.QSignalMapper()
        self.signalMapperComment.mapped[str].connect(self.openComments)

        extraOptionsMenu = QtWidgets.QMenu(self.ui.menuButton)
        extraOptionsMenu.addAction(
            'Get SceneSelection',
            self.getSceneSelection
        )
        extraOptionsMenu.addAction(
            'Set SceneSelection',
            self.setSceneSelection
        )
        self.ui.menuButton.setMenu(extraOptionsMenu)

        self.refreshAssetManager()

    @QtCore.Slot()
    def refreshAssetManager(self):
        '''Refresh assets in asset manager.'''
        assets = self.connector.getAssets()

        self.ui.AssertManagerTableWidget.setSortingEnabled(False)
        self.ui.AssertManagerTableWidget.setRowCount(0)

        self.ui.AssertManagerTableWidget.setRowCount(len(assets))

        component_ids = []

        for component_id, _ in assets:
            if component_id:
                component_ids.append(component_id)

        if component_ids:
            query_string = (
                'select name, version.asset.type.short, version.asset.name, '
                'version.asset.type.name, version.asset.versions.version, '
                'version.id, version.version, version.asset.versions, '
                'version.date, version.comment, version.asset.name, version, '
                'version_id, version.user.first_name, version.user.last_name '
                'from Component where id in ({0})'.format(
                    ','.join(component_ids)
                )
            )
            components = self.connector.session.query(query_string).all()

            asset_ids = set()
            for component in components:
                asset_ids.add(component['version']['asset']['id'])

            if asset_ids:
                # Because of bug in 3.3.X backend we need to divide the query. The
                # memory cache will allow using entities without caring about this.
                preload_string = (
                    'select components.name from AssetVersion where '
                    'asset_id in ({0})'
                ).format(', '.join(list(asset_ids)))
                self.connector.session.query(preload_string).all()

            component_map = dict(
                (component['id'], component)
                for component in components
            )
        else:
            component_map = {}

        for i in range(len(assets)):
            if assets[i][0]:
                component = component_map[assets[i][0]]
                asset_version = component['version']
                componentNameStr = component['name']
                assetVersionNr = asset_version['version']
                asset = asset_version['asset']
    
                asset_versions_with_same_component_name = []

                for related_version in asset['versions']:
                    for other_component in related_version['components']:
                        if other_component['name'] == componentNameStr:
                            asset_versions_with_same_component_name.append(
                                related_version
                            )

                asset_versions_with_same_component_name = sorted(
                    asset_versions_with_same_component_name,
                    key=lambda x: x['version']
                )
                latest_version_number = (
                    asset_versions_with_same_component_name[-1]['version']
                )

                versionIndicatorButton = QtWidgets.QPushButton('')
                if assetVersionNr == latest_version_number:
                    versionIndicatorButton.setStyleSheet('''
                        QPushButton {
                            background-color: #1CBC90;
                            border: none;
                        }
                    ''')
                    self.connector.setNodeColor(
                        applicationObject=assets[i][1], latest=True
                    )
                else:
                    versionIndicatorButton.setStyleSheet('''
                        QPushButton {
                            background-color: #E36316;
                            border: none;
                        }
                    ''')
                    self.connector.setNodeColor(
                        applicationObject=assets[i][1], latest=False
                    )
                self.ui.AssertManagerTableWidget.setCellWidget(
                    i, 0, versionIndicatorButton
                )

                componentName = QtWidgets.QTableWidgetItem(componentNameStr)
                self.ui.AssertManagerTableWidget.setItem(i, 1, componentName)

                componentId = QtWidgets.QTableWidgetItem(component['id'])
                self.ui.AssertManagerTableWidget.setItem(i, 2, componentId)

                assetType = QtWidgets.QTableWidgetItem(asset['type']['short'])
                self.ui.AssertManagerTableWidget.setItem(i, 3, assetType)

                assetTypeLong = QtWidgets.QTableWidgetItem(
                    asset['type']['name']
                )
                self.ui.AssertManagerTableWidget.setItem(i, 4, assetTypeLong)

                versionNumberComboBox = QtWidgets.QComboBox()
                for version in reversed(
                    asset_versions_with_same_component_name
                ):
                    versionNumberComboBox.addItem(str(version['version']))

                conName = self.connector.getConnectorName()
                if conName in self.notVersionable:
                    if componentNameStr in self.notVersionable[conName]:
                        versionNumberComboBox.setEnabled(False)

                result = versionNumberComboBox.findText(str(assetVersionNr))
                versionNumberComboBox.setCurrentIndex(result)

                self.ui.AssertManagerTableWidget.setCellWidget(
                    i, 5, versionNumberComboBox
                )

                versionNumberComboBox.currentIndexChanged.connect(
                    self.changeVersion
                )

                latestVersionNumberWidget = QtWidgets.QTableWidgetItem(
                    str(latest_version_number)
                )
                self.ui.AssertManagerTableWidget.setItem(
                    i, 6, latestVersionNumberWidget
                )

                assetName = QtWidgets.QTableWidgetItem(asset['name'])
                assetName.setToolTip(asset['name'])
                self.ui.AssertManagerTableWidget.setItem(i, 7, assetName)

                assetNameInScene = QtWidgets.QTableWidgetItem(assets[i][1])
                assetNameInScene.setToolTip(assets[i][1])
                self.ui.AssertManagerTableWidget.setItem(
                    i, 8, assetNameInScene
                )

                selectButton = QtWidgets.QPushButton('S')
                selectButton.setToolTip('Select asset in scene')
                self.ui.AssertManagerTableWidget.setCellWidget(
                    i, 9, selectButton
                )
                selectButton.clicked.connect(self.signalMapperSelect.map)

                self.signalMapperSelect.setMapping(selectButton, assets[i][1])

                replaceButton = QtWidgets.QPushButton('R')
                self.ui.AssertManagerTableWidget.setCellWidget(
                    i, 10, replaceButton
                )

                removeButton = QtWidgets.QPushButton()
                removeButton.setToolTip('Remove asset from scene')
                icon = QtGui.QIcon()
                icon.addPixmap(
                    QtGui.QPixmap(':ftrack/image/integration/trash'),
                    QtGui.QIcon.Normal,
                    QtGui.QIcon.Off
                )
                removeButton.setIcon(icon)
                self.ui.AssertManagerTableWidget.setCellWidget(
                    i, 11, removeButton
                )
                removeButton.clicked.connect(self.signalMapperRemove.map)
                self.signalMapperRemove.setMapping(removeButton, assets[i][1])

                assetId = QtWidgets.QTableWidgetItem(str(asset['id']))
                self.ui.AssertManagerTableWidget.setItem(i, 12, assetId)

                assetVersionId = QtWidgets.QTableWidgetItem(
                    str(asset_version['id'])
                )
                self.ui.AssertManagerTableWidget.setItem(i, 13, assetVersionId)

                currentVersionFallback = QtWidgets.QTableWidgetItem(
                    str(assetVersionNr)
                )
                self.ui.AssertManagerTableWidget.setItem(
                    i, 14, currentVersionFallback
                )

                commentButton = QtWidgets.QPushButton()
                commentButton.setText('')
                icon = QtGui.QIcon()
                icon.addPixmap(
                    QtGui.QPixmap(
                        ':ftrack/image/integration/comment'
                    ),
                    QtGui.QIcon.Normal,
                    QtGui.QIcon.Off
                )
                commentButton.setIcon(icon)

                fullUserName = (
                    asset_version['user']['first_name'] + ' ' +
                    asset_version['user']['last_name']
                )
                pubDate = str(asset_version['date'])
                comment = asset_version['comment']
                tooltipText = '\n'.join([fullUserName, pubDate, comment])

                commentButton.setToolTip(tooltipText)
                self.ui.AssertManagerTableWidget.setCellWidget(
                    i, 15, commentButton
                )

                commentButton.clicked.connect(self.signalMapperComment.map)

                self.signalMapperComment.setMapping(
                    commentButton, str(asset_version['id'])
                )

                commentButton.setEnabled(has_webwidgets)

        self.ui.AssertManagerTableWidget.setHorizontalHeaderLabels(
            self.columnHeaders
        )

    def openComments(self, taskId):
        '''Open comments dialog for *taskId*.'''
        self.comment_dialog = FtrackInfoDialog(connector=self.connector)
        self.comment_dialog.show()
        self.comment_dialog.move(
            QtWidgets.QApplication.desktop().screen().rect().center() -
            self.comment_dialog.rect().center()
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
                tableItem = self.ui.AssertManagerTableWidget.item(i, 3)

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
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText('Remove asset.')
        msgBox.setInformativeText('Are you sure you want to remove the asset?')
        msgBox.setStandardButtons(
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
        )
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        ret = msgBox.exec_()
        if ret == QtWidgets.QMessageBox.Ok:
            self.connector.removeObject(applicationObject=objectName)
            foundItem = self.ui.AssertManagerTableWidget.findItems(
                objectName, QtCore.Qt.MatchExactly
            )
            self.ui.AssertManagerTableWidget.removeRow(foundItem[0].row())
            self.refreshAssetManager()

    def getSelectedRows(self):
        '''Return selected rows.'''
        rows = []
        selectionModel = self.ui.AssertManagerTableWidget.selectionModel()
        for idx in selectionModel.selectedRows():
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

    def versionLatestSelected(self):
        '''Version up assets to latest.'''
        rows = self.getSelectedRows()
        for row in rows:
            newIndex = 0
            self.ui.AssertManagerTableWidget.cellWidget(
                row, 5
            ).setCurrentIndex(newIndex)

    def selectAll(self):
        '''Select all assets rows.'''
        rowCount = self.ui.AssertManagerTableWidget.rowCount()
        for row in range(0, rowCount):
            index = self.ui.AssertManagerTableWidget.model().index(row, 0)
            selModel = self.ui.AssertManagerTableWidget.selectionModel()
            selModel.select(
                index,
                QtCore.QItemSelectionModel.Select |
                QtCore.QItemSelectionModel.Rows
            )

    def getSceneSelection(self):
        '''Get selection from scene.'''
        selectedAssets = self.connector.getSelectedAssets()
        self.ui.AssertManagerTableWidget.selectionModel().clearSelection()
        for asset in selectedAssets:
            foundItem = self.ui.AssertManagerTableWidget.findItems(
                asset, QtCore.Qt.MatchExactly
            )
            index = self.ui.AssertManagerTableWidget.indexFromItem(
                foundItem[0]
            )
            selModel = self.ui.AssertManagerTableWidget.selectionModel()
            selModel.select(
                index, QtCore.QItemSelectionModel.Select |
                QtCore.QItemSelectionModel.Rows
            )

    def setSceneSelection(self):
        '''Set scene selection from selected rows.'''
        rows = self.getSelectedRows()
        objectNames = []
        for row in rows:
            objectName = self.ui.AssertManagerTableWidget.item(row, 8).text()
            objectNames.append(objectName)
        self.connector.selectObjects(objectNames)

    @QtCore.Slot(str, int)
    def changeVersion(self, newVersion=None, row=None):
        '''Change version.'''
        if row is None:
            sender = self.sender()
            row = self.ui.AssertManagerTableWidget.indexAt(sender.pos()).row()
            newVersion = sender.itemText(newVersion)

        latestVersion = self.ui.AssertManagerTableWidget.item(row, 6).text()
        objectName = self.ui.AssertManagerTableWidget.item(row, 8).text()
        componentName = self.ui.AssertManagerTableWidget.item(row, 1).text()
        assetId = self.ui.AssertManagerTableWidget.item(row, 12).text()
        currentVersion = self.ui.AssertManagerTableWidget.item(row, 14).text()

        ftrackAsset = ftrack.Asset(assetId)
        assetVersions = ftrackAsset.getVersions()

        newftrackAssetVersion = None

        # Check the next suitable chosen version.
        for version in assetVersions:

            # If there's a matching version , use that one.
            if str(version.getVersion()) == str(newVersion):
                newftrackAssetVersion = version
                break
            else:
                # Otherwise, fall back on the latest available.
                newftrackAssetVersion = assetVersions[-1]

        try:
            newComponent = newftrackAssetVersion.getComponent(componentName)
        except:
            print 'Could not getComponent for main. Trying with sequence'
            componentName = 'sequence'
            newComponent = newftrackAssetVersion.getComponent(componentName)

        # Build a new api component object.
        ftrack_component = self.connector.session.get(
            'Component', newComponent.getId()
        )
        location = self.connector.session.pick_location(
            component=ftrack_component
        )

        if location is None:
            raise ftrack.FTrackError(
                'Cannot load version data as no accessible location '
                'containing the version is available.'
            )

        path = location.get_filesystem_path(ftrack_component)

        importObj = FTAssetObject(
            filePath=path,
            componentName=componentName,
            componentId=newComponent.getId(),
            assetVersionId=newftrackAssetVersion.getId()
        )

        before = set(self.connector.getAssets())

        result = self.connector.changeVersion(
            iAObj=importObj,
            applicationObject=objectName
        )
        after = set(self.connector.getAssets())

        diff = after.difference(before)

        if result:
            cellWidget = self.ui.AssertManagerTableWidget.cellWidget(row, 0)
            if newVersion == latestVersion:
                cellWidget.setStyleSheet('''
                        QPushButton {
                            background-color: #1CBC90;
                            border: none;
                        }
                    ''')
                self.connector.setNodeColor(
                    applicationObject=objectName, latest=True
                )
            else:
                cellWidget.setStyleSheet('''
                        QPushButton {
                            background-color: #E36316;
                            border: none;
                        }
                    ''')
                self.connector.setNodeColor(
                    applicationObject=objectName, latest=False
                )

            self.ui.AssertManagerTableWidget.item(
                row, 14
            ).setText(str(newVersion))
            if diff:
                newName = list(diff)[0][1]
                self.ui.AssertManagerTableWidget.item(row, 8).setText(newName)
            self.updateSignalMapper(row)
        else:
            cellWidget = self.ui.AssertManagerTableWidget.cellWidget(row, 5)
            fallbackIndex = cellWidget.findText(currentVersion)
            cellWidget.setCurrentIndex(fallbackIndex)

    def updateSignalMapper(self, row):
        '''Update signal mapper with updated widgets.'''
        name = self.ui.AssertManagerTableWidget.item(row, 8).text()

        removeWidget = self.ui.AssertManagerTableWidget.cellWidget(row, 11)
        self.signalMapperRemove.setMapping(removeWidget, unicode(name))

        selectWidget = self.ui.AssertManagerTableWidget.cellWidget(row, 9)
        self.signalMapperSelect.setMapping(selectWidget, unicode(name))
