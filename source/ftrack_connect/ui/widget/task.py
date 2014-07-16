# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import uuid

from PySide import QtGui
from PySide import QtCore
import ftrack_connect.ui.widget.label


class Task(QtGui.QWidget):

    selected = QtCore.Signal(object)

    def __init__(self, parent=None, task=None):
        '''Initialise widget with *parent* and reference to ftrack *task*.'''
        super(Task, self).__init__(parent=parent)
        self.setObjectName('task')
        self._task = task
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
        self.setId(task.getId())
        self.setTitle(self._task.getName())
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
            path = self._task.getName()

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
            'id': self._task.id(),
            'path': self.getPath(),
            'loggedTime': self.loggedTime()
        }

    def _onPlayButtonClicked(self):
        '''Handle playButton clicks.'''
        self.selected.emit(self)

    def path(self, asString=False):
        '''Return path for task as a list.

        If *asString* is True a string representation will be returned instead.

        '''
        if self._path is None:
            parents = self._task.getParents()
            parents.reverse()
            self._path = [parent.getName() for parent in parents]

        if asString:
            return '/'.join(self._path)

        return self._path
