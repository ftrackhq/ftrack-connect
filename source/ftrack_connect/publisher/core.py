# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import threading
import uuid

from PySide import QtGui, QtCore
import ftrack
from ftrack_connect.core import ConnectError


def asynchronous(f):
    '''Decorator to make a method asynchronous using its own thread.'''
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=f, args=args, kwargs=kwargs)
        thread.start()
    return wrapper


def register(connect):
    '''Register publish plugin to ftrack connect.'''
    publisher = Publisher()
    connect.add(publisher, publisher.getName())


class Publisher(QtGui.QWidget):
    '''Base widget for ftrack connect publisher plugin.'''

    # Add signal for when the entity is changed.
    entityChanged = QtCore.Signal(object)

    publishStarted = QtCore.Signal(str)
    publishFinished = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        '''Instantiate the publisher widget.'''
        super(Publisher, self).__init__(*args, **kwargs)

        self.publishLayout = QtGui.QVBoxLayout()
        self.setLayout(
            self.publishLayout
        )

        # Create form layout to keep track of publish form items.
        layout = QtGui.QFormLayout()
        self.layout().addLayout(layout)

        # Local import to avoid circular.
        from component.linked_to import LinkedToComponent
        from component.asset_type_selector import AssetTypeSelectorComponent

        # Add linked to component and connect to entityChanged signal.
        linkedTo = LinkedToComponent()
        layout.addRow('Linked to', linkedTo)
        self.entityChanged.connect(linkedTo.setEntity)

        # Add asset selector.
        self.assetSelector = AssetTypeSelectorComponent()
        layout.addRow('Asset type', self.assetSelector)

        # Add version description component.
        self.versionDescriptionComponent = QtGui.QTextEdit()
        layout.addRow('Description', self.versionDescriptionComponent)

        # TODO: Remove this call when it is possible to select or start
        # publisher with an entity.
        self.setEntity(ftrack.Task('d547547a-66de-11e1-bdb8-f23c91df25eb'))

        publishButton = QtGui.QPushButton(text='Publish')
        publishButton.clicked.connect(self.publish)

        self.addWidget(publishButton)

    def getName(self):
        '''Return name of widget.'''
        return 'Publish'

    def addWidget(self, widget):
        '''Add *widget* to internal layout.'''
        layout = self.layout()
        layout.addWidget(widget)

    def setEntity(self, entity):
        '''Set the *entity* for the publisher.'''
        self._entity = entity
        self.entityChanged.emit(entity)

    def publish(self):
        '''Gather all data in publisher and publish version with components.'''
        entity = self._entity

        assetType = self.assetSelector.itemData(
            self.assetSelector.currentIndex()
        )

        versionDescription = self.versionDescriptionComponent.toPlainText()

        if entity.getObjectType() == 'Task':
            taskId = entity.getId()
            entity = entity.getParent()

        self._publish(
            entity, assetType, versionDescription, taskId, components=[]
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
            raise ConnectError('No asset type found')

        if not entity:
            raise ConnectError('No entity found')

        publishId = uuid.uuid1()
        self.publishStarted.emit(publishId)

        if components is None:
            components = []

        asset = entity.createAsset(
            assetType.getName(), assetType.getShort(), taskId
        )

        version = asset.createVersion(
            versionDescription, taskId
        )

        for component in components:
            component = version.createComponent(path=filePath, location=None)
            for location in component.get('locations', []):
                location.addComponent(component)

        version.publish()

        self.publishFinished.emit(publishId)
