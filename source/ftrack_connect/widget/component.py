# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore
import harmony.ui.filesystem_browser


class Component(QtGui.QWidget):
    '''Represent a component.'''

    def __init__(self, componentName=None, resourceIdentifier=None,
                 browser=None, parent=None):
        '''Initialise widget with initial component *value* and *parent*.'''
        super(Component, self).__init__(parent=parent)

        self.setLayout(QtGui.QVBoxLayout())
        labelWidth = 60

        self.componentNameLayout = QtGui.QHBoxLayout()

        self.componentNameLabel = QtGui.QLabel('Name')
        self.componentNameLabel.setFixedWidth(labelWidth)
        self.componentNameLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self.componentNameLayout.addWidget(self.componentNameLabel, stretch=0)

        self.componentNameEdit = QtGui.QLineEdit()
        self.componentNameEdit.setPlaceholderText('Enter component name')
        self.componentNameLayout.addWidget(self.componentNameEdit)
        self.layout().addLayout(self.componentNameLayout)

        self.resourceIdentifierLayout = QtGui.QHBoxLayout()

        self.resourceIdentifierLabel = QtGui.QLabel('Path')
        self.resourceIdentifierLabel.setFixedWidth(labelWidth)
        self.resourceIdentifierLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self.resourceIdentifierLayout.addWidget(
            self.resourceIdentifierLabel, stretch=0
        )

        self.resourceIdentifierEdit = QtGui.QLineEdit()
        self.resourceIdentifierEdit.setPlaceholderText(
            'Enter component resource identifier'
        )
        self.resourceIdentifierLayout.addWidget(self.resourceIdentifierEdit)

        self.browseButton = QtGui.QPushButton('Browse')
        self.browseButton.setToolTip('Browse for path.')
        self.resourceIdentifierLayout.addWidget(self.browseButton, stretch=0)

        self.layout().addLayout(self.resourceIdentifierLayout)

        self.browseButton.clicked.connect(self.browse)

        if browser:
            self.browser = browser
        else:
            self.browser = harmony.ui.filesystem_browser.FilesystemBrowser(
                parent=self
            )
            self.browser.setMinimumSize(900, 500)

        # Set initial values.
        self.setComponentName(componentName)
        self.setResourceIdentifier(resourceIdentifier)

    def browse(self):
        '''Show browse dialog and populate value with result.'''
        currentResourceIdentifier = self.resourceIdentifier()
        if currentResourceIdentifier:
            self.browser.setLocation(currentResourceIdentifier)

        if self.browser.exec_():
            selected = self.browser.selected()
            if selected:
                resourceIdentifier = selected[0]

                self.resourceIdentifierEdit.setText(resourceIdentifier)
                if not self.componentName():
                    self.setComponentName(resourceIdentifier)

    def componentName(self):
        '''Return current component name.'''
        return self.componentNameEdit.text()

    def setComponentName(self, componentName):
        '''Set *componentName*.'''
        self.componentNameEdit.setText(componentName)

    def resourceIdentifier(self):
        '''Return current resource identifier.'''
        return self.resourceIdentifierEdit.text()

    def setResourceIdentifier(self, resourceIdentifier):
        '''Set *resourceIdentifier*.'''
        self.resourceIdentifierEdit.setText(resourceIdentifier)
