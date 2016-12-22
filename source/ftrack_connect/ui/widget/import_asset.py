# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import os
import getpass
import ftrack
from QtExt import QtCore, QtWidgets

from ftrack_connect.connector import PanelComInstance, FTAssetObject
from ftrack_connect.ui.widget.list_assets_table import ListAssetsTableWidget
from ftrack_connect.ui.widget.asset_version_details import AssetVersionDetailsWidget
from ftrack_connect.ui.widget.component_table import ComponentTableWidget
from ftrack_connect.ui.widget.import_options import ImportOptionsWidget
from ftrack_connect.ui.widget import header
from ftrack_connect.ui.theme import applyTheme
from ftrack_connect.ui.widget.context_selector import ContextSelector
from ftrack_connect.ui import resource


class FtrackImportAssetDialog(QtWidgets.QDialog):
    '''Import asset dialog widget.'''

    importSignal = QtCore.Signal()

    def __init__(self, parent=None, connector=None):
        '''Instantiate widget with *connector*.'''
        if not connector:
            raise ValueError(
                'Please provide a connector object for {0}'.format(
                    self.__class__.__name__
                )
            )

        super(FtrackImportAssetDialog, self).__init__(parent=parent)
        applyTheme(self, 'integration')
        self.connector = connector
        self.currentEntity = ftrack.Task(
            os.getenv('FTRACK_TASKID',
                os.getenv('FTRACK_SHOTID')
            )
        )

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

        self.setMinimumWidth(600)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.mainLayout)

        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self.scrollArea = QtWidgets.QScrollArea(self)
        self.mainLayout.addWidget(self.scrollArea)

        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )

        self.mainWidget = QtWidgets.QWidget(self)
        self.scrollArea.setWidget(self.mainWidget)

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.mainWidget.setLayout(self.verticalLayout)

        self.headerWidget = header.Header(getpass.getuser(), self)
        self.verticalLayout.addWidget(self.headerWidget, stretch=0)

        self.browseTasksWidget = ContextSelector(
            currentEntity=self.currentEntity, parent=self
        )

        self.verticalLayout.addWidget(self.browseTasksWidget, stretch=0)

        self.listAssetsTableWidget = ListAssetsTableWidget(self)

        self.verticalLayout.addWidget(self.listAssetsTableWidget, stretch=4)

        # Horizontal line
        self.divider = QtWidgets.QFrame()
        self.divider.setFrameShape(QtWidgets.QFrame.HLine)
        self.divider.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.divider.setLineWidth(2)

        self.verticalLayout.addWidget(self.divider)

        self.assetVersionDetailsWidget = AssetVersionDetailsWidget(
            self, connector=self.connector
        )

        self.verticalLayout.addWidget(
            self.assetVersionDetailsWidget, stretch=0
        )

        self.componentTableWidget = ComponentTableWidget(
            self, connector=self.connector
        )

        self.verticalLayout.addWidget(self.componentTableWidget, stretch=3)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.importAllButton = QtWidgets.QPushButton("Import All")
        self.importAllButton.setFixedWidth(120)
        self.importAllButton.setObjectName('ftrack-import-btn')

        self.importSelectedButton = QtWidgets.QPushButton("Import Selected")
        self.importSelectedButton.setFixedWidth(120)
        self.importAllButton.setObjectName('ftrack-import-btn')

        self.horizontalLayout.addWidget(self.importSelectedButton)
        self.horizontalLayout.addWidget(self.importAllButton)

        self.horizontalLayout.setAlignment(QtCore.Qt.AlignRight)

        self.importOptionsWidget = ImportOptionsWidget(
            parent=self, connector=self.connector
        )

        self.verticalLayout.addWidget(self.importOptionsWidget, stretch=0)

        self.messageLabel = QtWidgets.QLabel(self)
        self.messageLabel.setText(' \n ')
        self.verticalLayout.addWidget(self.messageLabel, stretch=0)

        self.setObjectName('ftrackImportAsset')
        self.setWindowTitle("ftrackImportAsset")

        panelComInstance = PanelComInstance.instance()
        panelComInstance.addSwitchedShotListener(
            self.reset_context_browser
        )

        self.browseTasksWidget.entityChanged.connect(self.clickedIdSignal)

        self.importAllButton.clicked.connect(self.importAllComponents)
        self.importSelectedButton.clicked.connect(
            self.importSelectedComponents
        )
        self.listAssetsTableWidget.assetVersionSelectedSignal[str].connect(
            self.clickedAssetVSignal
        )
        self.listAssetsTableWidget.assetTypeSelectedSignal[str].connect(
            self.importOptionsWidget.setStackedWidget
        )
        self.importSignal.connect(panelComInstance.refreshListeners)

        self.componentTableWidget.importComponentSignal.connect(
            self.onImportComponent
        )

        self.browseTasksWidget.reset()

    def reset_context_browser(self):
        '''Reset task browser to the value stored in the environments'''
        entity_id = os.getenv('FTRACK_TASKID', os.getenv('FTRACK_SHOTID'))
        entity = ftrack.Task(entity_id)
        self.browseTasksWidget.reset(entity)

    def importSelectedComponents(self):
        '''Import selected components.'''
        selectedRows = self.componentTableWidget.selectionModel(
        ).selectedRows()
        for r in selectedRows:
            self.onImportComponent(r.row())

    def importAllComponents(self):
        '''Import all components.'''
        rowCount = self.componentTableWidget.rowCount()
        for i in range(rowCount):
            self.onImportComponent(i)

    def onImportComponent(self, row):
        '''Handle importing component.'''
        importOptions = self.importOptionsWidget.getOptions()

        # TODO: Add methods to panels to ease retrieval of this data
        componentItem = self.componentTableWidget.item(
            row,
            self.componentTableWidget.columns.index('Component')
        )
        component_id = componentItem.data(
            self.componentTableWidget.COMPONENT_ROLE
        )

        ftrack_component = self.connector.session.query(
            'select name, version.asset.type.short, version.asset.name, '
            'version.asset.type.name, version.asset.versions.version, '
            'version.id, version.version, version.asset.versions, '
            'version.date, version.comment, version.asset.name, version, '
            'version_id, version.user.first_name, version.user.last_name '
            ' from Component where id is {0}'.format(component_id)
        ).one()

        assetVersion = ftrack_component['version']['id']

        self.importSignal.emit()
        asset_name = ftrack_component['version']['asset']['name']

        accessPath = self.componentTableWidget.item(
            row,
            self.componentTableWidget.columns.index('Path')
        ).text()

        importObj = FTAssetObject(
            componentId=ftrack_component['id'],
            filePath=accessPath,
            componentName=ftrack_component['name'],
            assetVersionId=assetVersion,
            options=importOptions
        )
        try:
            self.connector.importAsset(importObj)
        except Exception, error:
            self.headerWidget.setMessage(
                str(error.message), 'error'
            )
            return

        self.headerWidget.setMessage(
            u'Imported {0}.{1}:v{2}'.format(
                asset_name, ftrack_component['name'], ftrack_component['version']['version']
            )
        )

    def clickedAssetVSignal(self, assetVid):
        '''Set asset version to *assetVid*.'''
        self.assetVersionDetailsWidget.setAssetVersion(assetVid)
        self.componentTableWidget.setAssetVersion(assetVid)

    def clickedIdSignal(self, ftrackId):
        '''Handle click signal.'''
        self.listAssetsTableWidget.initView(ftrackId)
