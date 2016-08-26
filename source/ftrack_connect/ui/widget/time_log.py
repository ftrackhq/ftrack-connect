# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from QtExt import QtWidgets
from QtExt import QtCore
from QtExt import QtGui

import ftrack_connect.ui.widget.label


class TimeLog(QtWidgets.QWidget):
    '''Represent a time log.'''

    selected = QtCore.Signal(object)

    def __init__(self, title=None, description=None, data=None, parent=None):
        '''Initialise time log.

        *title* should be the title entry to display for the time log whilst
        *description* can provide an optional longer description.

        *data* is optional data that can be stored for future reference (for
        example a link to an ftrack task that the time log represents).

        *parent* should be the optional parent of this widget.

        '''
        super(TimeLog, self).__init__(parent=parent)
        self.setObjectName('time-log')
        self._data = None

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.labelLayout = QtWidgets.QVBoxLayout()
        layout.addLayout(self.labelLayout, stretch=1)

        self.titleLabel = ftrack_connect.ui.widget.label.Label()
        self.titleLabel.setProperty('title', True)
        self.labelLayout.addWidget(self.titleLabel)

        self.descriptionLabel = ftrack_connect.ui.widget.label.Label()
        self.labelLayout.addWidget(self.descriptionLabel)

        # TODO: Add theme support.
        playIcon = QtGui.QIcon(
            QtGui.QPixmap(':/ftrack/image/light/play')
        )

        self.playButton = QtWidgets.QPushButton(playIcon, '')
        self.playButton.setFlat(True)
        self.playButton.clicked.connect(self._onPlayButtonClicked)
        layout.addWidget(self.playButton)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )

        # Set initial values.
        self.setValue({
            'title': title,
            'description': description,
            'data': data
        })

    def title(self):
        '''Return title.'''
        return self.titleLabel.text()

    def setTitle(self, title):
        '''Set *title*.'''
        self.titleLabel.setText(title)

    def description(self):
        '''Return description.'''
        return self.descriptionLabel.text()

    def setDescription(self, description):
        '''Set *description*.'''
        self.descriptionLabel.setText(description)

    def data(self):
        '''Return associated data.'''
        return self._data

    def setData(self, data):
        '''Set associated *data*.'''
        self._data = data

    def value(self):
        '''Return dictionary of current settings.'''
        return {
            'title': self.title(),
            'description': self.description(),
            'data': self.data()
        }

    def setValue(self, value):
        '''Set all attributes from *value*.'''
        self.setTitle(value.get('title', None))
        self.setDescription(value.get('description', None))
        self.setData(value.get('data', None))

    def _onPlayButtonClicked(self):
        '''Handle playButton clicks.'''
        self.selected.emit(self)
