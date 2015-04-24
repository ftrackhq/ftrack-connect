# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import os
import getpass
import ftrack
from PySide import QtCore, QtGui

from ftrack_connect.connector import PanelComInstance, FTAssetObject
from ftrack_connect.ui.widget.browse_tasks_small import BrowseTasksSmallWidget
from ftrack_connect.ui.widget.list_assets_table import ListAssetsTableWidget
from ftrack_connect.ui.widget.asset_version_details import AssetVersionDetailsWidget
from ftrack_connect.ui.widget.component_table import ComponentTableWidget
from ftrack_connect.ui.widget.import_options import ImportOptionsWidget
from ftrack_connect.ui.widget import header
from ftrack_connect.ui.theme import applyTheme
from ftrack_connect.ui.widget.context_selector import ContextSelector
from ftrack_connect.ui import resource


class FtrackImportAssetDialog(QtGui.QDialog):
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
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding
        )

        self.setMinimumWidth(600)

        self.mainLayout = QtGui.QVBoxLayout(self)
        self.setLayout(self.mainLayout)

        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self.scrollArea = QtGui.QScrollArea(self)
        self.mainLayout.addWidget(self.scrollArea)

        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )

        self.mainWidget = QtGui.QWidget(self)
        self.scrollArea.setWidget(self.mainWidget)

        self.verticalLayout = QtGui.QVBoxLayout()
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
        self.divider = QtGui.QFrame()
        self.divider.setFrameShape(QtGui.QFrame.HLine)
        self.divider.setFrameShadow(QtGui.QFrame.Sunken)
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

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.importAllButton = QtGui.QPushButton("Import All")
        self.importAllButton.setFixedWidth(120)
        self.importAllButton.setObjectName('ftrack-import-btn')

        self.importSelectedButton = QtGui.QPushButton("Import Selected")
        self.importSelectedButton.setFixedWidth(120)
        self.importAllButton.setObjectName('ftrack-import-btn')

        self.horizontalLayout.addWidget(self.importSelectedButton)
        self.horizontalLayout.addWidget(self.importAllButton)

        self.horizontalLayout.setAlignment(QtCore.Qt.AlignRight)

        self.importOptionsWidget = ImportOptionsWidget(
            parent=self, connector=self.connector
        )

        self.verticalLayout.addWidget(self.importOptionsWidget, stretch=0)

        self.messageLabel = QtGui.QLabel(self)
        self.messageLabel.setText(' \n ')
        self.verticalLayout.addWidget(self.messageLabel, stretch=0)

        self.setObjectName('ftrackImportAsset')
        self.setWindowTitle("ftrackImportAsset")

        panelComInstance = PanelComInstance.instance()
        panelComInstance.addSwitchedShotListener(
            self.browseTasksWidget.reset
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
        # TODO: Add methods to panels to ease retrieval of this data
        componentItem = self.componentTableWidget.item(
            row,
            self.componentTableWidget.columns.index('Component')
        )
        component = componentItem.data(
            self.componentTableWidget.COMPONENT_ROLE
        )

        assetVersion = component.getVersion()

        self.importSignal.emit()
        asset_name = component.getParents()[0].getAsset().getName()
        self.headerWidget.setMessage(
            'Imported %s.%s:v%s' % (
                asset_name, component.getName(), assetVersion
                )
        )

    def clickedAssetVSignal(self, assetVid):
        '''Set asset version to *assetVid*.'''
        self.assetVersionDetailsWidget.setAssetVersion(assetVid)
        self.componentTableWidget.setAssetVersion(assetVid)

    def clickedIdSignal(self, ftrackId):
        '''Handle click signal.'''
        self.listAssetsTableWidget.initView(ftrackId)

