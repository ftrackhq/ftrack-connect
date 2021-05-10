# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging

from Qt import QtWidgets
from Qt import QtCore
import clique

from ftrack_api import exception
from ftrack_api import event


from ftrack_connect.ui.widget import data_drop_zone as _data_drop_zone
from ftrack_connect.ui.widget import components_list as _components_list
from ftrack_connect.ui.widget import entity_selector

import ftrack_connect.asynchronous
import ftrack_connect.error


class EntitySelector(entity_selector.EntitySelector):
    '''Local representation of EntitySelector to support custom behaviour.'''

    def isValidBrowseSelection(self, entity):
        '''Overriden method to validate the selected *entity*.'''
        # Prevent selecting projects.
        return entity.entity_type != 'Project'


class AssetsPublisher(QtWidgets.QWidget):
    '''Publish widget for ftrack connect Publisher.'''

    publishStarted = QtCore.Signal()
    publishFinished = QtCore.Signal(bool)

    #: Signal to emit when an asset is created.
    assetCreated = QtCore.Signal(object)

    @property
    def session(self):
        '''Return current session.'''
        return self._session

    def __init__(self, session, parent=None):
        '''Initiate a publish view.'''
        super(AssetsPublisher, self).__init__(parent)

        self._session = session
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._entity = None

        layout = QtWidgets.QVBoxLayout()

        self.setLayout(layout)

        self.entitySelector = EntitySelector(self.session)
        self.entitySelector.setFixedHeight(50)
        self.context_label = QtWidgets.QLabel('Select task context')
        self.context_label.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(self.context_label)
        layout.addWidget(self.entitySelector)


        self.browser = _data_drop_zone.DataDropZone()
        layout.addWidget(self.browser,  stretch=1)
        self.browser.dataSelected.connect(self._onDataSelected)

        self.reset_button = QtWidgets.QPushButton('Clear list')
        layout.addWidget(self.reset_button)
        self.reset_button.hide()

        # Create a components list widget.
        # Now used as asset versions
        self.componentsList = _components_list.ComponentsList()
        self.componentsList.label.text = 'Assets'
        self.componentsList.setObjectName('publisher-componentlist')
        self.componentsList.itemsChanged.connect(
            self._onComponentListItemsChanged
        )
        layout.addWidget(
            self.componentsList, stretch=3
        )

        self.componentsList.hide()

        # # Create form layout to keep track of publish form items.
        # formLayout = QtWidgets.QFormLayout()
        # layout.addLayout(formLayout, stretch=0)
        #
        # # Add entity selector.
        # self.entitySelector = EntitySelector(self.session)
        # formLayout.addRow('Select task context', self.entitySelector)

        # # Add version description component.
        # self.versionDescription = QtWidgets.QTextEdit()
        # formLayout.addRow('Description', self.versionDescription)

        publishButton = QtWidgets.QPushButton(text='Publish')
        publishButton.setObjectName('primary')
        publishButton.clicked.connect(self.publish)

        layout.addWidget(
            publishButton, alignment=QtCore.Qt.AlignCenter, stretch=0
        )

        # Connect reset button
        self.reset_button.clicked.connect(self.clear)

    def setEntity(self, entity):
        '''Set current entity.'''
        self.entitySelector.setEntity(entity)

    def _onComponentListItemsChanged(self):
        '''Callback for component changed signal.'''
        # self.previewSelector.setItems(self.componentsList.items())
        if self.componentsList.count():
            self.componentsList.show()
            self.reset_button.show()
        else:
            self.componentsList.hide()
            self.reset_button.hide()

    def _onDataSelected(self, filePath):
        '''Callback for Browser file selected signal.'''
        self.componentsList.addItem({
            'resourceIdentifier': filePath
        })

    def clear(self):
        '''Clear the publish view to it's initial state.'''
        # self.assetOptions.clear()
        # self.versionDescription.clear()
        self.componentsList.clearItems()
        # self.thumbnailDropZone.clear()
        # self.entitySelector.setEntity(None)

    def get_assets(self, entity):
        assets = []
        try:
            if entity.entity_type == 'Task':
                entity = entity['parent']

            assets = entity['assets']
        except AttributeError:
            self.logger.warning(
                'Unable to fetch assets for entity: {0}'.format(entity)
            )
        return assets

    def publish(self):
        '''Gather all data in publisher and publish version with components.'''
        # TODO: Proper validation.

        entity = self.entitySelector.getEntity()
        if entity is None:
            raise ftrack_connect.error.ConnectError(
                'No linked entity selected to publish against!'
            )

        task_id = None

        # ftrack does not support having Tasks as parent for Assets.
        # Therefore get parent shot/sequence etc.
        if entity.entity_type == 'Task':
            task_id = entity['id']

        self.publish_asset(entity, task_id)

    @ftrack_connect.asynchronous.asynchronous
    def publish_asset(self, entity, task_id):

        self.publishStarted.emit()
        for asset_item in self.componentsList.items():
            server_assets = self.get_assets(entity)

            asset_name = asset_item['componentName']
            asset_path = asset_item['resourceIdentifier']
            asset_id = None
            asset_type = None

            for server_asset in server_assets:
                server_asset_name = server_asset['name']
                if server_asset_name == asset_name:
                    asset_id = server_asset['id']
                    asset_type = server_asset['type']
                    break

            if not asset_id:
                asset_type = self.session.query(
                    'AssetType where name is "Upload"'
                ).one()

            component_location = self.session.pick_location()

            components = [{
                'locations': [component_location],
                'name': asset_name,
                'filePath': asset_path
            }]
            preview_path = asset_path

            thumbnail_file_path = asset_path
            if asset_path.endswith(']'):
                preview_path = None
                try:
                    collection = clique.parse(asset_path)
                    path = list(collection)[0]
                    thumbnail_file_path =path
                except:
                    thumbnail_file_path = None

            if thumbnail_file_path:
                if thumbnail_file_path.split('.')[-1] not in [
                    'bmp', 'gif', 'jpg', 'jpeg', 'png', 'tif', 'tiff'
                ]:
                    thumbnail_file_path = None


            self._publish(
                entity=entity,
                asset_id=asset_id,
                asset_name=asset_name,
                asset_type=asset_type,
                version_description='',
                task_id=task_id,
                components=components,
                preview_path=preview_path,
                thumbnail_file_path=thumbnail_file_path
            )

    def _publish(
            self, entity=None, asset_id=None, asset_name=None,
            asset_type='', version_description=None, task_id=None,
            components=None, preview_path=None, thumbnail_file_path=None
    ):
        asset_version = None

        # self.publishStarted.emit()

        try:
            if not asset_type:
                self.publishFinished.emit(False)
                raise ftrack_connect.error.ConnectError(
                    'No asset type selected.'
                )
            if not asset_name:
                self.publishFinished.emit(False)
                raise ftrack_connect.error.ConnectError(
                    'No asset name selected.'
                )
            if not entity:
                self.publishFinished.emit(False)
                raise ftrack_connect.error.ConnectError('No entity found')

            if components is None:
                components = []

            asset_parent = entity['parent']

            if not asset_id:

                asset = self.session.create(
                    'Asset',
                    {
                        'name': asset_name,
                        'type': asset_type,
                        'parent': asset_parent
                    }
                )

                self.session.commit()
                self.assetCreated.emit(asset)
            else:
                asset = self.session.get('Asset', asset_id)

            asset_version = self.session.create(
                'AssetVersion',
                {
                    'asset': asset,
                    'task': entity,
                }
            )
            self.session.commit()

            origin_location = self.session.query(
                'Location where name is "ftrack.origin"'
            )

            for component_data in components:
                component = asset_version.create_component(
                    component_data.get('filePath'),
                    {'name': component_data.get('name', None)},
                    location=None
                )
                for location in component_data.get('locations', []):
                    new_location = self.session.get(
                        'Location', location['id']
                    )
                    new_location.add_component(
                        component, source=origin_location
                    )
                    self.logger.info(
                        u'Publish {0!r} to location: {1!r}.'.format(
                            component, new_location['name']
                        )
                    )

            if preview_path:
                # TODO in case of error simply use this one
                # asset_version.encode_media(preview_path)
                self.session.event_hub.publish(
                    event.base.Event(
                        'ftrack.connect.publish.make-web-playable',
                        data=dict(
                            versionId=asset_version['id'],
                            path=preview_path
                        )
                    ),
                    synchronous=True
                )

            if thumbnail_file_path:
                asset_version.create_thumbnail(thumbnail_file_path)

            self.session.commit()
            self.publishFinished.emit(True)

        # Catch any errors, emit *publishFinished*, clean up and re-raise.
        except Exception as error:
            self.logger.exception(u'Failed to publish: {0}'.format(error))
            self.publishFinished.emit(False)
            self._cleanupFailedPublish(version=asset_version)

            raise

    def _cleanupFailedPublish(self, version=None):
        '''Clean up after a failed publish.'''
        try:
            if version:
                self.session.delete(version)

        except exception.OperationError:
            self.logger.exception(
                'Failed to delete version, probably due to a permission error.'
            )
        except Exception:
            self.logger.exception(
                'Failed to clean up version after failed publish'
            )
