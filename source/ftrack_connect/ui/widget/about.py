# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import json

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
        self.messageLabel.setAlignment(QtCore.Qt.AlignLeft)
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

    def setInformation(self, versionData, user, server):
        '''Set displayed *versionData*, *user*, *server*.'''
        core = [plugin for plugin in versionData if plugin.get('core')]
        plugins = [
            plugin for plugin in versionData if plugin.get('core') is not True
        ]

        coreTemplate = '''
        <h4>Version:</h4>
        <p>{core_versions}</p>
        <h4>Server and user:</h4>
        <p>{server}<br>
        {user}<br></p>
        '''

        itemTemplate = '{name}: {version}<br>'

        coreVersions = ''
        for _core in core:
            coreVersions += itemTemplate.format(
                name=_core['name'],
                version=_core['version']
            )

        content = coreTemplate.format(
            core_versions=coreVersions,
            server=server,
            user=user
        )

        if plugins:
            pluginVersions = ''
            for _plugin in plugins:
                pluginVersions += itemTemplate.format(
                    name=_plugin['name'],
                    version=_plugin['version']
                )

            content += '<h4>Plugins:</h4>{0}'.format(pluginVersions)

        self.messageLabel.setText(content)
        self.debugTextEdit.insertPlainText(
            json.dumps(versionData, indent=4, sort_keys=True)
        )
