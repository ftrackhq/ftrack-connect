# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

from PySide import QtGui

import ftrack_connect.widget.line_edit
import ftrack_connect.widget.label


class Component(QtGui.QWidget):
    '''Represent a component.'''

    def __init__(self, componentName=None, resourceIdentifier=None,
                 parent=None):
        '''Initialise widget with initial component *value* and *parent*.'''
        super(Component, self).__init__(parent=parent)
        self.setLayout(QtGui.QVBoxLayout())

        self.componentNameEdit = ftrack_connect.widget.line_edit.LineEdit()
        self.componentNameEdit.setPlaceholderText('Enter component name')

        self.layout().addWidget(self.componentNameEdit)

        # TODO: Add theme support.
        removeIcon = QtGui.QIcon(
            QtGui.QPixmap(':/image/light/trash')
        )

        self.removeAction = QtGui.QAction(
            QtGui.QIcon(removeIcon), 'Remove', self.componentNameEdit
        )
        self.removeAction.setStatusTip('Remove component.')
        self.componentNameEdit.addAction(
            self.removeAction
        )

        self.resourceInformation = ftrack_connect.widget.label.Label()
        self.layout().addWidget(self.resourceInformation)

        # Set initial values.
        self.setComponentName(componentName)
        self.setResourceIdentifier(resourceIdentifier)

    def value(self):
        '''Return dictionary with component data.'''
        return {
            'componentName': self.componentName(),
            'resourceIdentifier': self.resourceIdentifier()
        }

    def computeComponentName(self, resourceIdentifier):
        '''Return a relevant component name using *resourceIdentifier*.'''
        name = os.path.basename(resourceIdentifier)
        if not name:
            name = resourceIdentifier
        else:
            name = name.split('.')[0]

        return name

    def componentName(self):
        '''Return current component name.'''
        return self.componentNameEdit.text()

    def setComponentName(self, componentName):
        '''Set *componentName*.'''
        self.componentNameEdit.setText(componentName)

    def resourceIdentifier(self):
        '''Return current resource identifier.'''
        return self.resourceInformation.text()

    def setResourceIdentifier(self, resourceIdentifier):
        '''Set *resourceIdentifier*.'''
        self.resourceInformation.setText(resourceIdentifier)

        if not self.componentName():
            self.setComponentName(
                self.computeComponentName(resourceIdentifier)
            )
