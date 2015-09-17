# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack
import sys
import logging

from PySide import QtGui
from PySide import QtCore
import ftrack


from ftrack_connect.ui.widget import data_drop_zone as _data_drop_zone
from ftrack_connect.ui.widget import components_list as _components_list
from ftrack_connect.ui.widget import item_selector as _item_selector
from ftrack_connect.ui.widget import thumbnail_drop_zone as _thumbnail_drop_zone
from ftrack_connect.ui.widget import asset_options as _asset_options
from ftrack_connect.ui.widget import entity_selector

import ftrack_connect.asynchronous
import ftrack_connect.error


class EntitySelector(entity_selector.EntitySelector):
    '''Local representation of EntitySelector to support custom behaviour.'''

    def isValidBrowseSelection(self, entity):
        '''Overriden method to validate the selected *entity*.'''
        # Prevent selecting projects.
        return entity.entity_type != 'Project'


class Publisher(QtGui.QWidget):
    '''Publish widget for ftrack connect Publisher.'''
    publishStarted = QtCore.Signal()
    publishFinished = QtCore.Signal(bool)

    #: Signal to emit when an asset is created.
    assetCreated = QtCore.Signal(object)

    def __init__(self, parent=None):
        '''Initiate a publish view.'''
        super(Publisher, self).__init__(parent)

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._entity = None
        self._manageData = False

        layout = QtGui.QVBoxLayout()

        self.setLayout(layout)

        self.browser = _data_drop_zone.DataDropZone()
        layout.addWidget(self.browser)
        self.browser.dataSelected.connect(self._onDataSelected)

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

        # Add entity selector.
        self.entitySelector = EntitySelector()
        formLayout.addRow('Linked to', self.entitySelector)

        # Add asset options.
        self.assetOptions = _asset_options.AssetOptions()
        self.entitySelector.entityChanged.connect(self.assetOptions.setEntity)
        self.assetCreated.connect(self.assetOptions.setAsset)
        formLayout.addRow('Asset', self.assetOptions.radioButtonFrame)
        formLayout.addRow('Existing asset', self.assetOptions.existingAssetSelector)
        formLayout.addRow('Type', self.assetOptions.assetTypeSelector)
        formLayout.addRow('Name', self.assetOptions.assetNameLineEdit)
        self.assetOptions.initializeFieldLabels(formLayout)

        # Add preview selector.
        self.previewSelector = _item_selector.ItemSelector(
            labelField='componentName',
            defaultLabel='Unnamed component',
            emptyLabel='Select component to use'
        )
        formLayout.addRow('Web playable', self.previewSelector)

        self.thumbnailDropZone = _thumbnail_drop_zone.ThumbnailDropZone()
        formLayout.addRow('Thumbnail', self.thumbnailDropZone)

        # Add version description component.
        self.versionDescription = QtGui.QTextEdit()
        formLayout.addRow('Description', self.versionDescription)

        publishButton = QtGui.QPushButton(text='Publish')
        publishButton.setObjectName('primary')
        publishButton.clicked.connect(self.publish)

        layout.addWidget(
            publishButton, alignment=QtCore.Qt.AlignCenter, stretch=0
        )

    def setEntity(self, entity):
        '''Set current entity.'''
        self.entitySelector.setEntity(entity)

    def _onComponentListItemsChanged(self):
        '''Callback for component changed signal.'''
        self.previewSelector.setItems(self.componentsList.items())
        if self.componentsList.count():
            self.componentsList.show()
        else:
            self.componentsList.hide()

    def _onDataSelected(self, filePath):
        '''Callback for Browser file selected signal.'''
        self.componentsList.addItem({
            'resourceIdentifier': filePath
        })

    def _pickLocation(self, manageData=False):
        '''Return a location based on *manageData*.'''
        location = None
        locations = ftrack.getLocations(excludeInaccessible=True)
        try:
            location = next(
                candidateLocation for candidateLocation in locations
                if (
                    manageData == False
                    or not isinstance(candidateLocation, ftrack.UnmanagedLocation)
                )
            )

        except StopIteration:
            pass

        self.logger.debug('Picked location {0}.'.format(location))

        return location

    def clear(self):
        '''Clear the publish view to it's initial state.'''
        self._manageData = False
        self.assetOptions.clear()
        self.versionDescription.clear()
        self.componentsList.clearItems()
        self.thumbnailDropZone.clear()
        self.entitySelector.setEntity(None)

    def setManageData(self, manageData):
        '''Set *manageData*.'''
        self._manageData = manageData

    def publish(self):
        '''Gather all data in publisher and publish version with components.'''
        # TODO: Proper validation.
        entity = self.entitySelector.getEntity()
        if entity is None:
            raise ftrack_connect.error.ConnectError(
                'No linked entity selected to publish against!'
            )

        taskId = None

        asset = self.assetOptions.getAsset()
        assetType = self.assetOptions.getAssetType()
        assetName = self.assetOptions.getAssetName()

        versionDescription = self.versionDescription.toPlainText()

        previewPath = None
        previewComponent = self.previewSelector.currentItem()
        if previewComponent:
            previewPath = previewComponent['resourceIdentifier']

        # ftrack does not support having Tasks as parent for Assets.
        # Therefore get parent shot/sequence etc.
        if entity.getObjectType() == 'Task':
            taskId = entity.getId()
            entity = entity.getParent()

        componentLocation = self._pickLocation(self._manageData)

        components = []
        for component in self.componentsList.items():
            components.append({
                'locations': [componentLocation],
                'name': component['componentName'],
                'filePath': component['resourceIdentifier']
            })

        thumbnailFilePath = self.thumbnailDropZone.getFilePath()

        self._publish(
            entity=entity,
            asset=asset,
            assetName=assetName,
            assetType=assetType,
            versionDescription=versionDescription,
            taskId=taskId,
            components=components,
            previewPath=previewPath,
            thumbnailFilePath=thumbnailFilePath
        )

    def _cleanupFailedPublish(self, version=None):
        '''Clean up after a failed publish.'''
        try:
            version.delete()
        except ftrack.FTrackError:
            self.logger.exception(
                'Failed to delete version, probably due to a permission error.'
            )
        except Exception:
            self.logger.exception(
                'Failed to clean up version after failed publish'
            )

    @ftrack_connect.asynchronous.asynchronous
    def _publish(
        self, entity=None, assetName=None, assetType=None,
        versionDescription='', taskId=None, components=None,
        previewPath=None, thumbnailFilePath=None, asset=None
    ):
        '''If *asset* is specified, publish a new version of it. Otherwise, get
        or create an asset of *assetType* on *entity*.

        *taskId*, *versionDescription*, *components*, *previewPath* and
        *thumbnailFilePath* are optional.

        Each component in *components* should be represented by a dictionary
        containing name, filepath and a list of locations.

        '''
        version = None

        self.publishStarted.emit()

        try:
            if not (asset or assetType):
                self.publishFinished.emit(False)
                raise ftrack_connect.error.ConnectError('No asset type selected.')

            if not entity:
                self.publishFinished.emit(False)
                raise ftrack_connect.error.ConnectError('No entity found')

            if components is None:
                components = []

            if not asset:
                if assetName is None:
                    assetName = assetType.getName()

                asset = entity.createAsset(
                    assetName, assetType.getShort(), taskId
                )
                self.assetCreated.emit(asset)

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

            if previewPath:
                ftrack.EVENT_HUB.publish(
                    ftrack.Event(
                        'ftrack.connect.publish.make-web-playable',
                        data=dict(
                            versionId=version.getId(),
                            path=previewPath
                        )
                    ),
                    synchronous=True
                )

            if thumbnailFilePath:
                version.createThumbnail(thumbnailFilePath)

            version.publish()

            self.publishFinished.emit(True)

        # Catch any errors, emit *publishFinished*, clean up and re-raise.
        except Exception as error:
            self.logger.exception('Failed to publish')
            self.publishFinished.emit(False)
            self._cleanupFailedPublish(version=version)

            raise
