# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from QtExt import QtWidgets, QtCore, QtGui
import ftrack

from ftrack_connect.ui.widget import entity_path as _entity_path
from ftrack_connect.ui.widget import entity_browser as _entity_browser


class EntitySelector(QtWidgets.QStackedWidget):
    '''Entity selector widget.'''

    entityChanged = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        '''Instantiate the entity selector widget.'''
        super(EntitySelector, self).__init__(*args, **kwargs)
        self._entity = None

        # Create widget used to select an entity.
        selectionWidget = QtWidgets.QFrame()
        selectionWidget.setLayout(QtWidgets.QHBoxLayout())
        selectionWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.insertWidget(0, selectionWidget)

        self.entityBrowser = _entity_browser.EntityBrowser(parent=self)
        self.entityBrowser.setMinimumSize(600, 400)
        self.entityBrowser.selectionChanged.connect(
            self._onEntityBrowserSelectionChanged
        )

        self.entityBrowseButton = QtWidgets.QPushButton('Browse')

        # TODO: Once the link is available through the API change this to a
        # combo with assigned tasks.
        self.assignedContextSelector = QtWidgets.QLineEdit()
        self.assignedContextSelector.setReadOnly(True)

        selectionWidget.layout().addWidget(self.assignedContextSelector)
        selectionWidget.layout().addWidget(self.entityBrowseButton)

        # Create widget used to present current selection.
        presentationWidget = QtWidgets.QFrame()
        presentationWidget.setLayout(QtWidgets.QHBoxLayout())
        presentationWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.insertWidget(1, presentationWidget)

        self.entityPath = _entity_path.EntityPath()
        presentationWidget.layout().addWidget(self.entityPath)

        self.discardEntityButton = QtWidgets.QPushButton()
        removeIcon = QtGui.QIcon(
            QtGui.QPixmap(':/ftrack/image/light/remove')
        )
        self.discardEntityButton.setIconSize(QtCore.QSize(20, 20))
        self.discardEntityButton.setIcon(removeIcon)
        self.discardEntityButton.setFixedWidth(20)
        self.discardEntityButton.clicked.connect(
            self._onDiscardEntityButtonClicked
        )

        presentationWidget.layout().addWidget(self.discardEntityButton)

        self.entityChanged.connect(self.entityPath.setEntity)
        self.entityChanged.connect(self._updateIndex)
        self.entityBrowseButton.clicked.connect(
            self._onEntityBrowseButtonClicked
        )

    def _updateIndex(self, entity):
        '''Update the widget when entity changes.'''
        if entity:
            self.setCurrentIndex(1)
        else:
            self.setCurrentIndex(0)

    def _onDiscardEntityButtonClicked(self):
        '''Handle discard entity button clicked.'''
        self.setEntity(None)

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
                # Translate new api entity to instance of ftrack.Task
                # TODO: this should not be necessary once connect has been
                # updated to use the new api.
                if selected[0].entity_type == 'Project':
                    entity = ftrack.Project(selected[0]['id'])
                else:
                    entity = ftrack.Task(selected[0]['id'])

                self.setEntity(entity)
            else:
                self.setEntity(None)

    def _onEntityBrowserSelectionChanged(self, selection):
        '''Handle selection of entity in browser.'''
        self.entityBrowser.acceptButton.setDisabled(True)
        if len(selection) == 1:
            entity = selection[0]

            if self.isValidBrowseSelection(entity):
                self.entityBrowser.acceptButton.setDisabled(False)

    def setEntity(self, entity):
        '''Set the *entity* for the view.'''
        self._entity = entity
        self.entityChanged.emit(entity)

    def getEntity(self):
        '''Return current entity.'''
        return self._entity

    def isValidBrowseSelection(self, entity):
        '''Return True if selected *entity* is valid.'''
        return True