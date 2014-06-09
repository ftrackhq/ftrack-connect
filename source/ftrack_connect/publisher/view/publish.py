# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import time

from PySide import QtGui
from PySide import QtCore
import ftrack

from ..component.linked_to import LinkedToComponent
from ..component.asset_type_selector import AssetTypeSelectorComponent
from ..core import asynchronous


class PublishView(QtGui.QWidget):

    entityChanged = QtCore.Signal(object)

    publishStarted = QtCore.Signal()
    publishFinished = QtCore.Signal()
    publishFailed = QtCore.Signal()

    def __init__(self, parent):
        '''Initiate a publish view.'''
        super(PublishView, self).__init__(parent)

        publishLayout = QtGui.QVBoxLayout()

        self.setLayout(publishLayout)

        # Create form layout to keep track of publish form items.
        formLayout = QtGui.QFormLayout()
        publishLayout.addLayout(formLayout)

        # Add linked to component and connect to entityChanged signal.
        linkedTo = LinkedToComponent()
        formLayout.addRow('Linked to', linkedTo)
        self.entityChanged.connect(linkedTo.setEntity)

        # Add asset selector.
        self.assetSelector = AssetTypeSelectorComponent()
        formLayout.addRow('Asset type', self.assetSelector)

        # Add version description component.
        self.versionDescriptionComponent = QtGui.QTextEdit()
        formLayout.addRow('Description', self.versionDescriptionComponent)

        # TODO: Remove this call when it is possible to select or start
        # publisher with an entity.
        self.setEntity(ftrack.Task('d547547a-66de-11e1-bdb8-f23c91df25eb'))

        publishButton = QtGui.QPushButton(text='Publish')
        publishButton.clicked.connect(self.publish)

        publishLayout.addWidget(publishButton)

    def setEntity(self, entity):
        '''Set the *entity* for the view.'''
        self._entity = entity
        self.entityChanged.emit(entity)

    def publish(self):
        '''Gather all data in publisher and publish version with components.'''
        self.publishStarted.emit()

        entity = self._entity

        assetType = self.assetSelector.itemData(
            self.assetSelector.currentIndex()
        )

        versionDescription = self.versionDescriptionComponent.toPlainText()

        # ftrack does not support having Tasks as parent for Assets.
        # Therefore get parent shot/sequence etc.
        if entity.getObjectType() == 'Task':
            taskId = entity.getId()
            entity = entity.getParent()

        defaultLocation = ftrack.pickLocation()

        # TODO: Get components from components widget.
        components = []
        for component in components:
            component['locations'] = [
                defaultLocation
            ]

        self._publish(
            entity, assetType, versionDescription,
            taskId, components=components
        )

    @asynchronous
    def _publish(
        self, entity=None, assetType=None,
        versionDescription='', taskId=None, components=None
    ):
        '''Get or create an asset of *assetType* on *entity*.

        *taskId*, *versionDescription* and *components* are optional.

        Each component in *components* should be represented by a dictionary
        containing name, filepath and a list of locations.

        '''
        if not assetType:
            self.publishFailed.emit()
            raise ConnectError('No asset type found')

        if not entity:
            self.publishFailed.emit()
            raise ConnectError('No entity found')

        if components is None:
            components = []

        asset = entity.createAsset(
            assetType.getName(), assetType.getShort(), taskId
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

        time.sleep(2)
        self.publishFinished.emit()
