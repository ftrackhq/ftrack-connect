# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import traceback

from QtExt import QtWidgets, QtCore
import ftrack

from ftrack_connect.worker import Worker
from ftrack_connect import session as fsession
from ftrack_api import symbol


class ComponentTableWidget(QtWidgets.QTableWidget):

    '''Display components for asset version and manage importing.'''

    COMPONENT_ROLE = (QtCore.Qt.UserRole + 1)

    importComponentSignal = QtCore.Signal(int)

    def __init__(self, parent=None, connector=None):
        '''Initialise widget.'''
        super(ComponentTableWidget, self).__init__(parent)

        if not connector:
            raise ValueError(
                'Please provide a connector object for {0}'.format(
                    self.__class__.__name__
                )
            )

        self.connector = connector
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
        session = fsession.get_shared_session()

        query = (
            'select id, asset, asset.type, asset.type.short, components'
            ' from AssetVersion where id is "{0}"'.format(assetVersionId)
        )
        asset_version = session.query(query).one()

        self.assetType = asset_version['asset']['type']['short']

        asset_version_components = asset_version['components']

        connectorName = self.connector.getConnectorName()
        # Temporary alias
        column = self.columns.index

        locations = session.query('Location').all()
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

                for location in locations:
                    # Don't show inaccessible locations
                    accessor = location.accessor
                    print 'Looking at', location['name'], accessor
                    if accessor is symbol.NOT_SET:
                        continue
                    name = location['name']
                    location_id = location['id']
                    print 'Adding:', location['name']
                    locationItem.addItem(name, location_id)

    def onLocationSelected(self, row):
        '''Handle location selection.'''
        # Temporary alias
        column = self.columns.index
        session = fsession.get_shared_session()

        self.item(row, column('Availability')).setText('0%')
        self.item(row, column('Path')).setText('No location selected.')

        actionItem = self.cellWidget(row, column('Action'))
        actionItem.setText('Import')
        actionItem.setEnabled(False)
        self._setButtonStyle(actionItem, 'standard')

        componentItem = self.item(row, self.columns.index('Component'))
        component_id = componentItem.data(self.COMPONENT_ROLE)
        ftrack_component = session.get('Component', component_id)

        print 'COMPONENT', ftrack_component

        locationItem = self.cellWidget(row, column('Location'))
        if not locationItem.count():
            return

        location_id = locationItem.itemData(locationItem.currentIndex())
        ftrack_location = session.get('Location', location_id)
        print 'LOCATION', ftrack_location

        try:
            componentInLocation = ftrack_location.get(ftrack_component['id'])
        except Exception:
            # TODO: Be able to check error type rather than just
            # assume component not in location.
            componentInLocation = ftrack_component

        print 'onLocationSelected.componentInLocation', componentInLocation, ftrack_location

        # Update availability indicator
        availabilityItem = self.item(row, column('Availability'))
        availability = ftrack_location.get_component_availability(
            componentInLocation
        )
        availabilityItem .setText('{0:.0f}%'.format(availability))

        # Update path for location
        pathItem = self.item(row, column('Path'))
        path = componentInLocation.getFilesystemPath()
        print 'component path:', path

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
                if componentInLocation.isContainer():
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
            component = componentItem.data(self.COMPONENT_ROLE)

            # Unfortunately, this will destroy the push button, so have to
            # recreate it afterwards. If Qt adds a takeCellWidget this can be
            # improved.
            transferProgressItem = QtWidgets.QProgressBar()
            transferProgressItem.setTextVisible(False)
            self.setCellWidget(row, self.columns.index('Action'),
                               transferProgressItem)

            transferProgressItem.setRange(0, 0)

            try:
                worker = Worker(self.transfer,
                                [component, None, location],
                                parent=self)
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
            locations = ftrack_shared_session.query('Location').all()
            accessibleLocations = {}
            for location in locations:
                if location.accessor is not None:
                    accessibleLocations[location['id']] = location

            availability = component.get_availability(
                accessibleLocations.keys()
            )

            candidates = []
            for locationId, available in availability.items():
                if available == 100:
                    location = accessibleLocations[locationId]
                    candidates.append((location['priority'], location))

            candidates.sort()
            if not candidates:
                raise ftrack.FTrackError('Unable to find a suitable source '
                                         'location to transfer from.')

            sourceLocation = candidates[0][1]

        componentInLocation = sourceLocation.get_component(component)
        targetLocation.add_component(componentInLocation)

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
