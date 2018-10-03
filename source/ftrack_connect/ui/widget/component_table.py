# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import traceback
import logging
from QtExt import QtWidgets, QtCore
import ftrack

from ftrack_connect.worker import Worker
from ftrack_api import symbol
from ftrack_api import exception


class ComponentTableWidget(QtWidgets.QTableWidget):

    '''Display components for asset version and manage importing.'''

    COMPONENT_ROLE = (QtCore.Qt.UserRole + 1)

    importComponentSignal = QtCore.Signal(int)

    def __init__(self, parent=None, connector=None):
        '''Initialise widget.'''
        super(ComponentTableWidget, self).__init__(parent)
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
        self.session = self.connector.session
        self.locations = self.session.query(
            'select name, id from Location'
        ).all()

        self.workers = []
        self.columns = (
            'Component', 'Location', 'Availability', 'Path', 'Action'
        )
        self.build()
        self.postBuild()
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def build(self):
        '''Build widgets and layout.'''
        self.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )

        self.setTextElideMode(QtCore.Qt.ElideLeft)
        self.setWordWrap(False)

        self.setRowCount(0)
        self.verticalHeader().hide()

        self.setColumnCount(len(self.columns))
        self.setHorizontalHeaderLabels(self.columns)

        horizontalHeader = self.horizontalHeader()
        horizontalHeader.setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        horizontalHeader.setResizeMode(
            self.columns.index('Path'),
            QtWidgets.QHeaderView.Stretch
        )
        horizontalHeader.setResizeMode(
            self.columns.index('Action'),
            QtWidgets.QHeaderView.Fixed
        )
        horizontalHeader.resizeSection(
            self.columns.index('Action'),
            100
        )

    def postBuild(self):
        '''Perform post build operations.'''
        self.locationSignalMapper = QtCore.QSignalMapper(self)
        self.locationSignalMapper.mapped[int].connect(
            self.onLocationSelected
        )

        self.actionSignalMapper = QtCore.QSignalMapper(self)
        self.actionSignalMapper.mapped.connect(
            self.onActionButtonClicked
        )

    @QtCore.Slot(str)
    def setAssetVersion(self, assetVersionId):
        '''Update list of components for asset version with *assetVersionId*.'''
        self.clear()

        query = (
            'select id, asset, asset.type, asset.type.short, components'
            ' from AssetVersion where id is "{0}"'.format(assetVersionId)
        )
        asset_version = self.session.query(query).one()

        self.assetType = asset_version['asset']['type']['short']

        asset_version_components = asset_version['components']

        connectorName = self.connector.getConnectorName()
        # Temporary alias
        column = self.columns.index

        for component in asset_version_components:
            componentName = component['name']

            if (
                connectorName == 'nuke' and 'proxy' in componentName
            ):
                pass
            else:
                rowCount = self.rowCount()
                self.insertRow(rowCount)

                componentItem = QtWidgets.QTableWidgetItem(componentName)
                componentItem.setData(self.COMPONENT_ROLE, component['id'])

                self.setItem(
                    rowCount, column('Component'), componentItem
                )

                pathItem = QtWidgets.QTableWidgetItem('')
                self.setItem(rowCount, column('Path'), pathItem)

                availabilityItem = QtWidgets.QTableWidgetItem('')
                self.setItem(
                    rowCount, column('Availability'), availabilityItem
                )

                actionItem = QtWidgets.QPushButton()
                self.setCellWidget(rowCount, column('Action'), actionItem)

                actionItem.clicked.connect(self.actionSignalMapper.map)
                self.actionSignalMapper.setMapping(actionItem, rowCount)

                locationItem = QtWidgets.QComboBox()
                self.setCellWidget(rowCount, column('Location'), locationItem)

                # Map version widget to row number to enable simple lookup
                locationItem.currentIndexChanged[int].connect(
                    self.locationSignalMapper.map
                )
                self.locationSignalMapper.setMapping(
                    locationItem, rowCount
                )

                available_locations = []
                for location in self.locations:
                    accessor = location.accessor
                    # Don't show inaccessible locations
                    if accessor is symbol.NOT_SET:
                        continue
                    name = location['name']
                    location_id = location['id']
                    locationItem.addItem(name, location_id)
                    available_locations.append(location)

                picked_location = self.session.pick_location(component)

                try:
                    location_index = available_locations.index(picked_location)
                except ValueError:
                    location_index = 0

                locationItem.setCurrentIndex(location_index)

    def onLocationSelected(self, row):
        '''Handle location selection.'''
        # Temporary alias
        column = self.columns.index

        self.item(row, column('Availability')).setText('0%')
        self.item(row, column('Path')).setText('No location selected.')

        actionItem = self.cellWidget(row, column('Action'))
        actionItem.setText('Import')
        actionItem.setEnabled(False)
        self._setButtonStyle(actionItem, 'standard')

        componentItem = self.item(row, self.columns.index('Component'))
        component_id = componentItem.data(self.COMPONENT_ROLE)
        ftrack_component = self.session.get('Component', component_id)

        locationItem = self.cellWidget(row, column('Location'))
        if not locationItem.count():
            return

        location_id = locationItem.itemData(locationItem.currentIndex())
        ftrack_location = self.session.get('Location', location_id)

        componentInLocation = ftrack_component

        # Update availability indicator
        availabilityItem = self.item(row, column('Availability'))
        availability = ftrack_location.get_component_availability(
            componentInLocation
        )
        availabilityItem .setText('{0:.0f}%'.format(availability))

        # Update path for location
        pathItem = self.item(row, column('Path'))
        path = None

        try:
            path = ftrack_location.get_filesystem_path(ftrack_component)
        except exception.ComponentNotInLocationError:
            self.logger.debug(
                u'Component {0} not available in Location {1}'.format(
                    ftrack_component['name'], ftrack_location['name']
                )
            )
        except exception.AccessorUnsupportedOperationError:
            self.logger.debug(
                u'Component {0} not accessible from Location {1}'.format(
                    ftrack_component['name'], ftrack_location['name']
                )
            )

        if path is None:
            pathItem.setText('Filesystem path not available.')
        else:
            pathItem.setText(path)
            pathItem.setToolTip(path)

        # Update action button
        if availability == 0:
            actionItem.setText('Transfer')
            actionItem.setEnabled(True)
            self._setButtonStyle(actionItem, 'alert')

        elif path is not None:
            # Access path available

            if availability < 100:
                is_container = isinstance(componentInLocation, (
                    self.session.types['SequenceComponent'],
                    self.session.types['ContainerComponent']
                ))

                if is_container:
                    # Allow import of partial sequence etc
                    actionItem.setEnabled(True)

            elif availability == 100:
                actionItem.setEnabled(True)

    def onActionButtonClicked(self, row):
        '''Handle transfer request.'''
        column = self.columns.index
        actionItem = self.cellWidget(row, column('Action'))

        # TODO: Make more robust test.
        if actionItem.text() == 'Import':
            self.importComponentSignal.emit(row)

        elif actionItem.text() == 'Transfer':
            locationItem = self.cellWidget(row, column('Location'))
            locationItem.setEnabled(False)
            location = locationItem.itemData(locationItem.currentIndex())

            componentItem = self.item(row, column('Component'))
            component_id = componentItem.data(self.COMPONENT_ROLE)
            ftrack_component = self.session.get('Component', component_id)

            # Unfortunately, this will destroy the push button, so have to
            # recreate it afterwards. If Qt adds a takeCellWidget this can be
            # improved.
            transferProgressItem = QtWidgets.QProgressBar()
            transferProgressItem.setTextVisible(False)
            self.setCellWidget(row, self.columns.index('Action'),
                               transferProgressItem)

            transferProgressItem.setRange(0, 0)

            try:
                worker = Worker(
                    self.transfer,
                    [ftrack_component, None, location],
                    parent=self
                )
                worker.start()

                while worker.isRunning():
                    app = QtWidgets.QApplication.instance()
                    app.processEvents()

                if worker.error:
                    raise worker.error[1], None, worker.error[2]

            except Exception as error:
                traceback.print_exc()
                QtWidgets.QMessageBox.critical(
                    None,
                    'Transfer Failed',
                    'Could not transfer to location!'
                    '\n{0}'.format(error)
                )

            finally:
                transferProgressItem.setMaximum(1)
                transferProgressItem.reset()
                locationItem.setEnabled(True)

                # Have to recreate action button
                actionItem = QtWidgets.QPushButton()
                self.setCellWidget(row, column('Action'), actionItem)

                actionItem.clicked.connect(self.actionSignalMapper.map)
                self.actionSignalMapper.setMapping(actionItem, row)

                self.onLocationSelected(row)

    def transfer(self, component, sourceLocation, targetLocation):
        '''Transfer *component* from *sourceLocation* to *targetLocation*.

        If sourceLocation is None, attempt to find a suitable source location
        automatically.

        '''
        if sourceLocation is None:
            # Find a source location if possible.
            locations = self.locations
            accessibleLocations = {}
            for location in locations:
                if location.accessor is not None:
                    accessibleLocations[location['id']] = location

            availability = component.get_availability(
                accessibleLocations.values()
            )

            candidates = []
            for locationId, available in availability.items():
                if available == 100:
                    location = accessibleLocations[locationId]
                    candidates.append((location.priority, location))

            candidates.sort()
            if not candidates:
                raise ftrack.FTrackError('Unable to find a suitable source '
                                         'location to transfer from.')

            sourceLocation = candidates[0][1]

        ftrack_target_location = self.session.query(
            'Location where id is "{0}"'.format(targetLocation)
        ).one()

        ftrack_target_location.add_component(component, sourceLocation, True)

    @QtCore.Slot()
    def clear(self):
        self.clearContents()
        self.setRowCount(0)

    def _setButtonStyle(self, button, style):
        '''Helper method to change button style.

        TODO: Move to separate style sheet and use object name to target.
        '''
        button.setStyleSheet('')

        if style == 'standard':

            gradientStartColor = '#3498DB'
            gradientStopColor = '#2C81BA'
            borderColor = 'rgba(0, 0, 0, 0.1) rgba(0, 0, 0, 0.1) rgba(0, 0, 0, 0.25)'
            textColor = '#ffffff'

        elif style == 'alert':
            borderColor = 'rgba(0, 0, 0, 0.1) rgba(0, 0, 0, 0.1) rgba(0, 0, 0, 0.25)'
            gradientStartColor = '#EE5F5B'
            gradientStopColor = '#BD362F'
            textColor = '#ffffff'

        else:
            return

        button.setStyleSheet('''
            QPushButton {{
                color: {textColor};
                border: 1px solid {borderColor};
                border-radius: 1px;
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {gradientStartColor}, stop: 1 {gradientStopColor}
                );
            }}

            QPushButton:pressed {{
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {gradientStopColor}, stop: 1 {gradientStartColor}
                );
            }}

            QPushButton:disabled {{
                background-color: {gradientStartColor};
            }}
        '''.format(textColor=textColor,
                   borderColor=borderColor,
                   gradientStartColor=gradientStartColor,
                   gradientStopColor=gradientStopColor))
