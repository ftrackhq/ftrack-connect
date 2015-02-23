# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import traceback
import operator
import os

from PySide import QtCore, QtGui
import ftrack

from ftrack_connect.worker import Worker


class ComponentTableWidget(QtGui.QTableWidget):

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
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

    def build(self):
        '''Build widgets and layout.'''
        self.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows
        )

        self.setTextElideMode(QtCore.Qt.ElideLeft)
        self.setWordWrap(False)

        self.setRowCount(0)
        self.verticalHeader().hide()

        self.setColumnCount(len(self.columns))
        self.setHorizontalHeaderLabels(self.columns)

        horizontalHeader = self.horizontalHeader()
        horizontalHeader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        horizontalHeader.setResizeMode(
            self.columns.index('Path'),
            QtGui.QHeaderView.Stretch
        )
        horizontalHeader.setResizeMode(
            self.columns.index('Action'),
            QtGui.QHeaderView.Fixed
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

        assetVersion = ftrack.AssetVersion(assetVersionId)
        self.assetType = assetVersion.getAsset().getType().getShort()

        assetVersionComponents = sorted(
            assetVersion.getComponents(), key=lambda entity: entity.get('name')
        )

        connectorName = self.connector.getConnectorName()

        # Temporary alias
        column = self.columns.index

        locations = ftrack.getLocations()

        for component in assetVersionComponents:
            componentName = component.getName()

            if (
                connectorName == 'nuke' and 'proxy' in componentName
            ):
                pass
            else:
                rowCount = self.rowCount()
                self.insertRow(rowCount)

                componentItem = QtGui.QTableWidgetItem(componentName)
                componentItem.setData(self.COMPONENT_ROLE, component)
                self.setItem(
                    rowCount, column('Component'), componentItem
                )

                pathItem = QtGui.QTableWidgetItem('')
                self.setItem(rowCount, column('Path'), pathItem)

                availabilityItem = QtGui.QTableWidgetItem('')
                self.setItem(
                    rowCount, column('Availability'), availabilityItem
                )

                actionItem = QtGui.QPushButton()
                self.setCellWidget(rowCount, column('Action'), actionItem)

                actionItem.clicked.connect(self.actionSignalMapper.map)
                self.actionSignalMapper.setMapping(actionItem, rowCount)

                locationItem = QtGui.QComboBox()
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
                    accessor = location.getAccessor()
                    if accessor is None:
                        continue

                    name = location.getName()
                    locationItem.addItem(name, location)

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
        component = componentItem.data(self.COMPONENT_ROLE)

        locationItem = self.cellWidget(row, column('Location'))
        if not locationItem.count():
            return

        location = locationItem.itemData(locationItem.currentIndex())

        try:
            componentInLocation = location.getComponent(
                component.getId()
            )
        except ftrack.FTrackError:
            # TODO: Be able to check error type rather than just
            # assume component not in location.
            componentInLocation = component

        # Update availability indicator
        availabilityItem = self.item(row, column('Availability'))
        availability = location.getComponentAvailability(
            componentInLocation.getId()
        )
        availabilityItem .setText('{0:.0f}%'.format(availability))

        # Update path for location
        pathItem = self.item(row, column('Path'))
        path = componentInLocation.getFilesystemPath()
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
            transferProgressItem = QtGui.QProgressBar()
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
                    app = QtGui.QApplication.instance()
                    app.processEvents()

                if worker.error:
                    raise worker.error[1], None, worker.error[2]

            except Exception as error:
                traceback.print_exc()
                QtGui.QMessageBox.critical(
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
                actionItem = QtGui.QPushButton()
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
            locations = ftrack.getLocations()
            accessibleLocations = {}
            for location in locations:
                if location.getAccessor() is not None:
                    accessibleLocations[location.getId()] = location

            availability = component.getAvailability(
                accessibleLocations.keys())
            candidates = []
            for locationId, available in availability.items():
                if available == 100:
                    location = accessibleLocations[locationId]
                    candidates.append((location.getPriority(), location))

            candidates.sort()
            if not candidates:
                raise ftrack.FTrackError('Unable to find a suitable source '
                                         'location to transfer from.')

            sourceLocation = candidates[0][1]

        componentInLocation = sourceLocation.getComponent(component)
        targetLocation.addComponent(componentInLocation)

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

            gradientStartColor = '#1199dd'
            gradientStopColor = '#0066cc'
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
                border-radius: 3px;
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
