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

        self._componentNameLayout = QtGui.QHBoxLayout()

        self._componentNameLabel = QtGui.QLabel('Name')
        self._componentNameLabel.setFixedWidth(labelWidth)
        self._componentNameLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self._componentNameLayout.addWidget(self._componentNameLabel, stretch=0)

        self._componentNameEdit = QtGui.QLineEdit()
        self._componentNameEdit.setPlaceholderText('Enter component name')
        self._componentNameLayout.addWidget(self._componentNameEdit)
        self.layout().addLayout(self._componentNameLayout)

        self._resourceIdentifierLayout = QtGui.QHBoxLayout()

        self._resourceIdentifierLabel = QtGui.QLabel('Path')
        self._resourceIdentifierLabel.setFixedWidth(labelWidth)
        self._resourceIdentifierLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self._resourceIdentifierLayout.addWidget(
            self._resourceIdentifierLabel, stretch=0
        )

        self._resourceIdentifierEdit = QtGui.QLineEdit()
        self._resourceIdentifierEdit.setPlaceholderText(
            'Enter component resource identifier'
        )
        self._resourceIdentifierLayout.addWidget(self._resourceIdentifierEdit)

        self._browseButton = QtGui.QPushButton('Browse')
        self._browseButton.setToolTip('Browse for path.')
        self._resourceIdentifierLayout.addWidget(self._browseButton, stretch=0)

        self.layout().addLayout(self._resourceIdentifierLayout)

        self._browseButton.clicked.connect(self.browse)

        if browser:
            self._browser = browser
        else:
            self._browser = harmony.ui.filesystem_browser.FilesystemBrowser(
                parent=self
            )
            self._browser.setMinimumSize(900, 500)

        # Set initial values.
        self.setComponentName(componentName)
        self.setResourceIdentifier(resourceIdentifier)

    def browse(self):
        '''Show browse dialog and populate value with result.'''
        currentResourceIdentifier = self.resourceIdentifier()
        if currentResourceIdentifier:
            self._browser.setLocation(currentResourceIdentifier)

        if self._browser.exec_():
            selected = self._browser.selected()
            if selected:
                resourceIdentifier = selected[0]

                self._resourceIdentifierEdit.setText(resourceIdentifier)
                if not self.componentName():
                    self.setComponentName(resourceIdentifier)

    def componentName(self):
        '''Return current component name.'''
        return self._componentNameEdit.text()

    def setComponentName(self, componentName):
        '''Set *componentName*.'''
        self._componentNameEdit.setText(componentName)

    def resourceIdentifier(self):
        '''Return current resource identifier.'''
        return self._resourceIdentifierEdit.text()

    def setResourceIdentifier(self, resourceIdentifier):
        '''Set *resourceIdentifier*.'''
        self._resourceIdentifierEdit.setText(resourceIdentifier)
