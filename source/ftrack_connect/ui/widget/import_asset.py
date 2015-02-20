from PySide import QtCore, QtGui

from ftrack_connect.connector import PanelComInstance, FTAssetObject
from ftrack_connect.ui.widget.browse_tasks_small import BrowseTasksSmallWidget
from ftrack_connect.ui.widget.list_assets_table import ListAssetsTableWidget
from ftrack_connect.ui.widget.asset_version_details import AssetVersionDetailsWidget
from ftrack_connect.ui.widget.component_table import ComponentTableWidget
from ftrack_connect.ui.widget.import_options import ImportOptionsWidget
from ftrack_connect.ui.widget.header import HeaderWidget

class FtrackImportAssetDialog(QtGui.QDialog):
    importSignal = QtCore.Signal()

    def __init__(self, parent=None, connector=None):

        if not connector:
            raise ValueError('Please provide a connector object for %s' % self.__class__.__name__)

        super(FtrackImportAssetDialog, self).__init__(parent=parent)

        self.connector = connector

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
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.mainWidget = QtGui.QWidget(self)
        self.scrollArea.setWidget(self.mainWidget)

        self.verticalLayout = QtGui.QVBoxLayout()
        self.mainWidget.setLayout(self.verticalLayout)

        self.headerWidget = HeaderWidget(self)
        self.headerWidget.setTitle('Import Asset')
        self.verticalLayout.addWidget(self.headerWidget, stretch=0)

        self.browseTasksWidget = BrowseTasksSmallWidget(parent=self)
        self.verticalLayout.addWidget(self.browseTasksWidget, stretch=0)
        pos = self.headerWidget.rect().bottomRight().y()
        self.browseTasksWidget.setTopPosition(pos)
        self.browseTasksWidget.setLabelText('Import from')

        self.listAssetsTableWidget = ListAssetsTableWidget(self)

        self.verticalLayout.addWidget(self.listAssetsTableWidget, stretch=4)

        # Horizontal line
        self.divider = QtGui.QFrame()
        self.divider.setFrameShape(QtGui.QFrame.HLine)
        self.divider.setFrameShadow(QtGui.QFrame.Sunken)
        self.divider.setLineWidth(2)

        self.verticalLayout.addWidget(self.divider)

        self.assetVersionDetailsWidget = AssetVersionDetailsWidget(self, connector=self.connector)

        self.verticalLayout.addWidget(self.assetVersionDetailsWidget, stretch=0)

        self.componentTableWidget = ComponentTableWidget(self, connector=self.connector)

        self.verticalLayout.addWidget(self.componentTableWidget, stretch=3)
        
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.verticalLayout.addLayout(self.horizontalLayout)
        
        self.importAllButton = QtGui.QPushButton("Import All")
        self.importAllButton.setFixedWidth(120)
        
        self.importSelectedButton = QtGui.QPushButton("Import Selected")
        self.importSelectedButton.setFixedWidth(120)
        
        self.horizontalLayout.addWidget(self.importSelectedButton)
        self.horizontalLayout.addWidget(self.importAllButton)
        
        self.horizontalLayout.setAlignment(QtCore.Qt.AlignRight)

        self.importOptionsWidget = ImportOptionsWidget(parent=self, connector=self.connector)

        self.verticalLayout.addWidget(self.importOptionsWidget, stretch=0)

        self.messageLabel = QtGui.QLabel(self)
        self.messageLabel.setText(' \n ')
        self.verticalLayout.addWidget(self.messageLabel, stretch=0)
        
        self.setObjectName('ftrackImportAsset')
        self.setWindowTitle("ftrackImportAsset")
        
        panelComInstance = PanelComInstance.instance()
        panelComInstance.addSwitchedShotListener(self.browseTasksWidget.updateTask)

        QtCore.QObject.connect(self.browseTasksWidget, QtCore.SIGNAL('clickedIdSignal(QString)'), self.clickedIdSignal)
        
        QtCore.QObject.connect(self.importAllButton, QtCore.SIGNAL('clicked()'), self.importAllComponents)
        QtCore.QObject.connect(self.importSelectedButton, QtCore.SIGNAL('clicked()'), self.importSelectedComponents)

        QtCore.QObject.connect(self.listAssetsTableWidget, QtCore.SIGNAL('assetVersionSelectedSignal(QString)'), self.clickedAssetVSignal)
        QtCore.QObject.connect(self.listAssetsTableWidget, QtCore.SIGNAL('assetTypeSelectedSignal(QString)'), self.importOptionsWidget.setStackedWidget)

        QtCore.QObject.connect(self, QtCore.SIGNAL('importSignal()'), panelComInstance.refreshListeners)

        self.componentTableWidget.importComponentSignal.connect(
            self.onImportComponent
        )
        
        self.browseTasksWidget.update()
        
    def importSelectedComponents(self):
        selectedRows = self.componentTableWidget.selectionModel().selectedRows()
        for r in selectedRows:
            self.onImportComponent(r.row())
        
    def importAllComponents(self):
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
        component = componentItem.data(
            self.componentTableWidget.COMPONENT_ROLE
        )
    
        assetVersion = component.getVersion()
        
        accessPath = self.componentTableWidget.item(
            row,
            self.componentTableWidget.columns.index('Path')
        ).text()
        
        importObj = FTAssetObject(
            componentId=component.getId(),
            filePath=accessPath,
            componentName=component.getName(),
            assetVersionId=assetVersion.getId(),
            options=importOptions
        )
        message = self.connector.importAsset(importObj)

        self.importSignal.emit()
        self.setMessage(message)
        
    def clickedAssetVSignal(self, assetVid):
        self.assetVersionDetailsWidget.setAssetVersion(assetVid)
        self.componentTableWidget.setAssetVersion(assetVid)
        
    def clickedIdSignal(self, ftrackId):
        self.listAssetsTableWidget.initView(ftrackId)

    def setMessage(self, message=''):        
        '''Display a message.'''
        if message is None:
            message = ''
            
        message = 'Notice: \n' + message
        self.messageLabel.setText(message)
