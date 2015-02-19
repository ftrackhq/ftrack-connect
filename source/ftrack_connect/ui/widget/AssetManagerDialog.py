from PySide import QtGui
from ftrack_connect.connector import PanelComInstance
from ftrack_connect.ui.widget import AssetManagerWidget
from ftrack_connect.ui.widget import HeaderWidget


class FtrackAssetManagerDialog(QtGui.QDialog):
    def __init__(self, parent=None):

        super(FtrackAssetManagerDialog, self).__init__(parent=parent)

        self.setMinimumWidth(400)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        self.centralwidget = QtGui.QWidget(self)
        self.verticalMainLayout = QtGui.QVBoxLayout(self)
        self.verticalMainLayout.setSpacing(6)
        self.horizontalLayout = QtGui.QHBoxLayout()

        self.headerWidget = HeaderWidget(self)
        self.headerWidget.setTitle('Asset Manager')
        self.verticalMainLayout.addWidget(self.headerWidget)

        self.assetManagerWidget = AssetManagerWidget(self.centralwidget)

        self.horizontalLayout.addWidget(self.assetManagerWidget)
        self.verticalMainLayout.addLayout(self.horizontalLayout)

        self.setObjectName('ftrackAssetManager')
        self.setWindowTitle("ftrackAssetManager")

        panelComInstance = PanelComInstance.instance()
        panelComInstance.addRefreshListener(self.assetManagerWidget.refreshAssetManager)
