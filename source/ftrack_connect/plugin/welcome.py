# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import tempfile
import appdirs
import urllib
import logging
import zipfile
import json

from ftrack_connect.qt import QtCore, QtWidgets, QtGui
import qtawesome as qta

from ftrack_connect.ui.application import ConnectWidget


class WelcomePlugin(ConnectWidget):
    '''Welcome plugin widget.'''

    name = "Welcome"

    # local variables for finding and installing plugin manager.
    install_path = appdirs.user_data_dir(
        'ftrack-connect-plugins', 'ftrack'
    )

    json_config_url = os.environ.get(
        'FTRACK_CONNECT_JSON_PLUGINS_URL',
        'https://download.ftrack.com/ftrack-connect/plugins.json'
    )

    def download(self, source_path):
        '''Download provided *plugin* item.'''
        zip_name = os.path.basename(source_path)
        save_path = tempfile.gettempdir()
        temp_path = os.path.join(save_path, zip_name)
        logging.debug('Downloading {} to {}'.format(source_path, temp_path))

        with urllib.request.urlopen(source_path) as dl_file:
            with open(temp_path, 'wb') as out_file:
                out_file.write(dl_file.read())
        return temp_path

    def discover_plugin_manager(self):
        with urllib.request.urlopen(self.json_config_url) as url:
            data = json.loads(url.read().decode())
            manager_url = data.get('manager')
            plugins_url = [plugin_url for plugin_url in data.get('integrations') if 'plugin-manager' in plugin_url]
            url = None

            # TODO: DISABLE ONCE WE DECIDE WHERE TO PUT THE MANAGER TO DOWNLOAD
            if plugins_url:
                url = plugins_url[0]
            elif manager_url:
                url = manager_url
            else:
                self.install_button.setDisabled(True)

            return url

    def install(self):
        '''Install provided *plugin* item.'''
        plugin_path = self.discover_plugin_manager()
        source_path = self.download(plugin_path)
        plugin_name = os.path.basename(source_path).split('.zip')[0]
        destination_path = os.path.join(self.install_path, plugin_name)
        logging.debug('Installing {} to {}'.format(source_path, destination_path))

        with zipfile.ZipFile(source_path, 'r') as zip_ref:
            zip_ref.extractall(destination_path)

    def __init__(self, session, parent=None):
        '''Instantiate the actions widget.'''
        super(WelcomePlugin, self).__init__(session, parent=parent)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(30, 0, 30, 0)
        self.setLayout(layout)
        spacer = QtWidgets.QSpacerItem(0, 70, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout.addItem(spacer)

        icon_label = QtWidgets.QLabel()
        icon = qta.icon("ph.rocket", color='#BF9AC9', rotated=45, scale_factor=0.7)
        icon_label.setPixmap(icon.pixmap(icon.actualSize(QtCore.QSize(180, 180))))
        icon_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

        label_title = QtWidgets.QLabel(
            "<H1>Let's get started!</H1>"
        )
        label_title.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

        label_text = QtWidgets.QLabel(
            'To be able to get use of the connect application, '
            'you will need to install the plugins for the integrations you would like to use.'
            '<br/><br/>'
        )
        self.install_button = QtWidgets.QPushButton(
            'Install the plugin manager to get started.'
        )
        self.install_button.setObjectName('primary')

        label_text.setAlignment(QtCore.Qt.AlignLeft| QtCore.Qt.AlignTop)
        label_text.setWordWrap(True)

        layout.addWidget(label_title, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        layout.addWidget(icon_label, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        layout.addWidget(label_text, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        layout.addWidget(self.install_button)
        spacer = QtWidgets.QSpacerItem(0, 300, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout.addItem(spacer)
        self.install_button.clicked.connect(self.install)
        self.discover_plugin_manager()
