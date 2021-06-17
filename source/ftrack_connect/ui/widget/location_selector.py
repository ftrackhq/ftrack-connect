from Qt import QtCore, QtWidgets, QtGui


class LocationSelector(QtWidgets.QWidget):

    excluded_locations = ['ftrack.origin', 'ftrack.review']

    def _update_description(self, index):
        # current_location_index = self.locationSelector.currentIndex()
        location = self.locationSelector.itemData(index)
        self.description.setText(location.get('description', 'No Description Provided'))

    def reset(self):
        current_location_index = self.locationSelector.findText(self.session.pick_location()['name'])
        self.locationSelector.setCurrentIndex(current_location_index)

    @property
    def selected_location(self):
        return self.locationSelector.itemData(
            self.locationSelector.currentIndex()
        )

    @property
    def session(self):
        return self._session

    def __init__(self, parent=None, session=None):
        super(LocationSelector, self).__init__(parent=parent)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.description = QtWidgets.QLabel()
        self.description.setWordWrap(True)
        # self.description.setDisabled(True)

        self.layout().addWidget(self.description)
        self._session = session

        # add location selector
        self.locationSelector = QtWidgets.QComboBox()
        self.all_locations = self.session.query('Location').all()
        self.locationSelector.currentIndexChanged.connect(self._update_description)
        for index, location in enumerate(self.all_locations):
            if (
                (location.accessor and location.structure) and
                location['name'] not in self.excluded_locations
            ):

                self.locationSelector.insertItem(index, location['name'], location)
                self.description.setText(location['description'])

        self.reset()
        self.main_layout.addWidget(self.locationSelector)

