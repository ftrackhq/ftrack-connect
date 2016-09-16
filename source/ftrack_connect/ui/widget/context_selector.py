# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import ftrack
from QtExt import QtWidgets
from QtExt import QtCore

import entity_path as entityPath
import entity_browser as entityBrowser
from ftrack_connect.ui.theme import applyTheme


class ContextSelector(QtWidgets.QWidget):
    '''Context browser with entity path field.'''

    entityChanged = QtCore.Signal(object)

    def __init__(self, currentEntity, parent=None):
        '''Initialise with the *currentEntity* and *parent* widget.'''
        super(ContextSelector, self).__init__(parent=parent)
        self._entity = currentEntity
        self.entityBrowser = entityBrowser.EntityBrowser()
        self.entityBrowser.setMinimumWidth(600)
        self.entityPath = entityPath.EntityPath()
        self.entityBrowseButton = QtWidgets.QPushButton('Browse')
        applyTheme(self.entityBrowser, 'integration')
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        layout.addWidget(self.entityPath)
        layout.addWidget(self.entityBrowseButton)

        self.entityBrowseButton.clicked.connect(
            self._onEntityBrowseButtonClicked
        )
        self.entityChanged.connect(self.entityPath.setEntity)
        self.entityBrowser.selectionChanged.connect(
            self._onEntityBrowserSelectionChanged
        )

    def reset(self, entity=None):
        '''Reset browser to the given *entity* or the default one.'''
        currentEntity = entity or self._entity
        self.entityPath.setEntity(currentEntity)
        self.setEntity(currentEntity)

    def setEntity(self, entity):
        '''Set the *entity* for the view.'''
        self._entity = entity
        self.entityChanged.emit(entity)

    def _onEntityBrowseButtonClicked(self):
        '''Handle entity browse button clicked.'''
        # Ensure browser points to parent of currently selected entity.
        if self._entity is not None:
            location = []
            try:
                parents = self._entity.getParents()
            except AttributeError:
                pass
            else:
                for parent in parents:
                    location.append(parent.getId())

            location.reverse()
            self.entityBrowser.setLocation(location)

        # Launch browser.
        if self.entityBrowser.exec_():
            selected = self.entityBrowser.selected()
            if selected:
                self.setEntity(ftrack.Task(selected[0]['id']))
            else:
                self.setEntity(None)

    def _onEntityBrowserSelectionChanged(self, selection):
        '''Handle selection of entity in browser.'''
        self.entityBrowser.acceptButton.setDisabled(True)

        # Only allow single select.
        if len(selection) == 1:
            # Do not allow selection of projects.
            if selection[0].entity_type == 'Project':
                return

            self.entityBrowser.acceptButton.setDisabled(False)
