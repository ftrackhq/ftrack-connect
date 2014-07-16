# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import uuid

from PySide import QtGui
from PySide import QtCore
import ftrack_connect.ui.widget.label


class TimeLog(QtGui.QWidget):
    '''Represent a time log.'''

    selected = QtCore.Signal(object)

    def __init__(self, parent=None, link=None):
        '''Initialise widget with *parent* and optional *link*.

        *link* may be a reference to an ftrack entity to represent a time log
        for.

        '''
        super(TimeLog, self).__init__(parent=parent)
        self.setObjectName('time-log')
        self._link = link
        self._path = None

        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        self.labelLayout = QtGui.QVBoxLayout()
        layout.addLayout(self.labelLayout, stretch=1)

        self.titleLabel = ftrack_connect.ui.widget.label.Label()
        self.titleLabel.setObjectName('title')
        self.labelLayout.addWidget(self.titleLabel)

        self.descriptionLabel = ftrack_connect.ui.widget.label.Label()
        self.labelLayout.addWidget(self.descriptionLabel)

        # TODO: Add theme support.
        playIcon = QtGui.QIcon(
            QtGui.QPixmap(':/ftrack/image/light/play')
        )

        self.playButton = QtGui.QPushButton(playIcon, '')
        self.playButton.setFlat(True)
        self.playButton.clicked.connect(self._onPlayButtonClicked)
        layout.addWidget(self.playButton)

        # Set initial values.
        self.setId(self._link.getId())
        self.setTitle(self._link.getName())
        self.setDescription(
            self.path(asString=True)
        )

    def id(self):
        '''Return current id.'''
        return self._id

    def setId(self, taskId):
        '''Set id to *taskId*.'''
        self._id = taskId

    def setTitle(self, title=None):
        '''Set the *path*.'''
        if title is None:
            path = self._link.getName()

        self.titleLabel.setText(title)

    def title(self):
        return self.titleLabel.text()

    def description(self):
        '''Return description.'''
        return self.descriptionLabel.text()

    def setDescription(self, description):
        '''Set *description*.'''
        self.descriptionLabel.setText(description)

    def value(self):
        '''Return dictionary with component data.'''
        return {
            'id': self._link.id(),
            'path': self.getPath(),
            'loggedTime': self.loggedTime()
        }

    def _onPlayButtonClicked(self):
        '''Handle playButton clicks.'''
        self.selected.emit(self)

    def path(self, asString=False):
        '''Return path for entity as a list.

        If *asString* is True a string representation will be returned instead.

        '''
        if self._path is None:
            parents = self._link.getParents()
            parents.reverse()
            self._path = [parent.getName() for parent in parents]

        if asString:
            return '/'.join(self._path)

        return self._path
