# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import os
import json

from QtExt import QtCore, QtWidgets, QtGui


from ftrack_connect.config import get_log_directory
import ftrack_connect.util


class AboutDialog(QtWidgets.QDialog):
    '''About widget.'''

    def __init__(
        self, parent,
        icon=':ftrack/image/default/ftrackLogoColor'
    ):
        super(AboutDialog, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(layout)

        self.icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(icon)
        self.icon.setPixmap(
            pixmap.scaledToHeight(36, mode=QtCore.Qt.SmoothTransformation)
        )
        self.icon.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.icon)

        self.messageLabel = QtWidgets.QLabel()
        self.messageLabel.setWordWrap(True)
        self.messageLabel.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.messageLabel)

        layout.addSpacing(25)

        self.debugButton = QtWidgets.QPushButton('More info')
        self.debugButton.clicked.connect(self._onDebugButtonClicked)

        layout.addWidget(self.debugButton)

        self.loggingButton = QtWidgets.QPushButton('Open log directory')
        self.loggingButton.clicked.connect(self._onLoggingButtonClicked)

        layout.addWidget(self.loggingButton)

        self.debugTextEdit = QtWidgets.QTextEdit()
        self.debugTextEdit.setReadOnly(True)
        self.debugTextEdit.setFontPointSize(10)
        self.debugTextEdit.hide()
        layout.addWidget(self.debugTextEdit)

    def _onDebugButtonClicked(self):
        '''Handle debug button clicked.'''
        self.debugButton.hide()
        self.debugTextEdit.show()
        self.adjustSize()

    def _onLoggingButtonClicked(self):
        '''Handle logging button clicked.'''
        directory = get_log_directory()

        if not os.path.exists(directory):
            # Create directory if not existing.
            try:
                os.makedirs(directory)
            except OSError:
                messageBox = QtWidgets.QMessageBox(parent=self)
                messageBox.setIcon(QtWidgets.QMessageBox.Warning)
                messageBox.setText(
                    u'Could not open or create logging '
                    u'directory: {0}.'.format(directory)
                )
                messageBox.exec_()
                return

        ftrack_connect.util.open_directory(directory)

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
