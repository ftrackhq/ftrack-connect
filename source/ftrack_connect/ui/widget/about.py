# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack


from PySide import QtGui, QtCore


class AboutDialog(QtGui.QDialog):
    '''About widget.'''

    def __init__(
        self, parent,
        icon=':ftrack/image/default/ftrackLogoColor'
    ):
        super(AboutDialog, self).__init__(parent)

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.setLayout(layout)

        self.icon = QtGui.QLabel()
        pixmap = QtGui.QPixmap(icon)
        self.icon.setPixmap(
            pixmap.scaledToHeight(36, mode=QtCore.Qt.SmoothTransformation)
        )
        self.icon.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.icon)

        self.messageLabel = QtGui.QLabel()
        self.messageLabel.setWordWrap(True)
        self.messageLabel.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.messageLabel)

        layout.addSpacing(25)

        self.debugButton = QtGui.QPushButton('More info')
        self.debugButton.clicked.connect(self._onDebugButtonClicked)

        layout.addWidget(self.debugButton)

        self.debugTextEdit = QtGui.QTextEdit()
        self.debugTextEdit.setReadOnly(True)
        self.debugTextEdit.setFontPointSize(10)
        self.debugTextEdit.hide()
        layout.addWidget(self.debugTextEdit)

    def _onDebugButtonClicked(self):
        '''Handle debug button clicked.'''
        self.debugButton.hide()
        self.debugTextEdit.show()
        self.adjustSize()

    def setInformation(self, version, user, server, debugData=None):
        '''Set displayed *version*, *user*, *server* and any *debugData*.

        *debugData* is optional and should be a dictionary containing key/value
        pairs.

        '''

        self.messageLabel.setText(
            '<h3>ftrack connect</h3>'
            '<p>Version {0}</p>'
            '<p><b>Server:</b> {1} <br>'
            '<b>User:</b> {2}</p>'.format(version, server, user)
        )

        if not debugData:
            debugData = dict()

        debugData['VERSION'] = version
        debugData['USER'] = user
        debugData['SERVER'] = server

        debugInformation = ''
        for key in sorted(debugData.keys(), reverse=True):
            debugInformation = '{1}: {2}\n{0}'.format(
                debugInformation, key, debugData[key]
            )

        self.debugTextEdit.insertPlainText(debugInformation)
