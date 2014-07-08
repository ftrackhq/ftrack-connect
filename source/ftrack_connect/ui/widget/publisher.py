# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui
from PySide import QtCore
import ftrack


from ftrack_connect.ui.widget import entity_path as _entity_path
from ftrack_connect.ui.widget import asset_type_selector as _asset_type_selector
from ftrack_connect.ui.widget import component_drop_zone as _component_drop_zone
from ftrack_connect.ui.widget import components_list as _components_list
import ftrack_connect.asynchronous
import ftrack_connect.error


class Publisher(QtGui.QWidget):
    '''Publish widget for ftrack connect Publisher.'''
    entityChanged = QtCore.Signal(object)

    publishStarted = QtCore.Signal()
    publishFinished = QtCore.Signal(bool)

    def __init__(self, parent):
        '''Initiate a publish view.'''
        super(Publisher, self).__init__(parent)

        layout = QtGui.QVBoxLayout()

        self.setLayout(layout)

        self.browser = _component_drop_zone.ComponentDropZone()
        layout.addWidget(self.browser)
        self.browser.fileSelected.connect(self._onFileSelected)

        # Create a components list widget.
        self.componentsList = _components_list.ComponentsList()
        self.componentsList.setObjectName('publisher-componentlist')
        self.componentsList.itemsChanged.connect(
            self._onComponentListItemsChanged
        )
        layout.addWidget(
            self.componentsList, stretch=1
        )
        self.componentsList.hide()

        # Create form layout to keep track of publish form items.
        formLayout = QtGui.QFormLayout()
        layout.addLayout(formLayout, stretch=0)

        # Add linked to component and connect to entityChanged signal.
        self.entityPath = _entity_path.EntityPath()
        formLayout.addRow('Linked to', self.entityPath)
        self.entityChanged.connect(self.entityPath.setEntity)

        # Add asset selector.
        self.assetSelector = _asset_type_selector.AssetTypeSelector()
        formLayout.addRow('Asset type', self.assetSelector)

        # Add version description component.
        self.versionDescription = QtGui.QTextEdit()
        formLayout.addRow('Description', self.versionDescription)

        publishButton = QtGui.QPushButton(text='Publish')
        publishButton.setObjectName('primary')
        publishButton.clicked.connect(self.publish)

        layout.addWidget(
            publishButton, alignment=QtCore.Qt.AlignCenter, stretch=0
        )

    def _onComponentListItemsChanged(self):
        '''Callback for component changed signal.'''
        if self.componentsList.count():
            self.componentsList.show()
        else:
            self.componentsList.hide()

    def _onFileSelected(self, filePath):
        '''Callback for Browser file selected signal.'''
        self.componentsList.addItem({
            'resourceIdentifier': filePath
        })

    def clear(self):
        '''Clear the publish view to it's initial state.'''
        self.assetSelector.setCurrentIndex(-1)
        self.versionDescription.clear()
        self.entityPath.clear()
        self.browser.clear()

    def setEntity(self, entity):
        '''Set the *entity* for the view.'''
        self._entity = entity
        self.entityChanged.emit(entity)

    def publish(self):
        '''Gather all data in publisher and publish version with components.'''
        self.publishStarted.emit()

        entity = self._entity
        taskId = None

        assetType = self.assetSelector.itemData(
            self.assetSelector.currentIndex()
        )

        versionDescription = self.versionDescription.toPlainText()

        # ftrack does not support having Tasks as parent for Assets.
        # Therefore get parent shot/sequence etc.
        if entity.getObjectType() == 'Task':
            taskId = entity.getId()
            entity = entity.getParent()

        defaultLocation = ftrack.pickLocation()

        components = []
        for component in self.componentsList.items():
            components.append({
                'locations': [defaultLocation],
                'name': component['componentName'],
                'filePath': component['resourceIdentifier']
            })

        self._publish(
            entity=entity, assetType=assetType,
            versionDescription=versionDescription, taskId=taskId,
            components=components
        )

    @ftrack_connect.asynchronous.asynchronous
    def _publish(
        self, entity=None, assetName=None, assetType=None,
        versionDescription='', taskId=None, components=None
    ):
        '''Get or create an asset of *assetType* on *entity*.

        *taskId*, *versionDescription* and *components* are optional.

        Each component in *components* should be represented by a dictionary
        containing name, filepath and a list of locations.

        '''
        if not assetType:
            self.publishFinished.emit(False)
            raise ftrack_connect.error.ConnectError('No asset type found')

        if not entity:
            self.publishFinished.emit(False)
            raise ftrack_connect.error.ConnectError('No entity found')

        if assetName is None:
            assetName = assetType.getName()

        if components is None:
            components = []

        asset = entity.createAsset(
            assetName, assetType.getShort(), taskId
        )

        version = asset.createVersion(
            versionDescription, taskId
        )

        for componentData in components:
            component = version.createComponent(
                componentData.get('name', None),
                path=componentData.get('filePath'),
                location=None
            )

            for location in componentData.get('locations', []):
                location.addComponent(component)

        version.publish()

        self.publishFinished.emit(True)
