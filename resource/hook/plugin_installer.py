# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack
import os
import re
import ftrack_api
import logging
import shutil
import zipfile
import tempfile
import urllib
from urllib.request import urlopen
import json

from Qt import QtWidgets, QtCore, QtGui
import qtawesome as qta
from distutils.version import LooseVersion
from ftrack_connect.ui.widget.overlay import BlockingOverlay, BusyOverlay


import ftrack_connect.ui.application
logger = logging.getLogger('ftrack_connect.plugin.plugin_installer')

# fetch available plugins from remote json
response = urlopen(
    'https://s3-eu-west-1.amazonaws.com/ftrack-deployment/ftrack-connect/plugins/plugins.json'
)
response_json = json.loads(response.read())
download_plugins = response_json['integrations']


class InstallerBlockingOverlay(
    BlockingOverlay
):
    '''Custom blocking overlay for publisher.'''

    def __init__(self, parent, message=''):
        super(InstallerBlockingOverlay, self).__init__(parent, message=message)
        self.confirmButton = QtWidgets.QPushButton('Ok')
        self.contentLayout.insertWidget(
            3, self.confirmButton, alignment=QtCore.Qt.AlignCenter, stretch=0
        )
        self.confirmButton.hide()
        self.confirmButton.clicked.connect(self.hide)
        self.content.setMinimumWidth(350)


class STATUSES(object):
    INSTALLED = 0
    NEW = 1
    UPDATE = 2
    REMOVE = 3
    DOWNLOAD = 4


class ROLES(object):
    PLUGIN_STATUS = QtCore.Qt.UserRole + 1
    PLUGIN_NAME = PLUGIN_STATUS + 1
    PLUGIN_VERSION = PLUGIN_NAME + 1
    PLUGIN_SOURCE_PATH = PLUGIN_VERSION + 1
    PLUGIN_INSTALL_PATH = PLUGIN_SOURCE_PATH + 1
    PLUGIN_ID = PLUGIN_INSTALL_PATH + 1


STATUS_ICONS = {
    STATUSES.INSTALLED: QtGui.QIcon(qta.icon('mdi6.harddisk')),
    STATUSES.NEW:  QtGui.QIcon(qta.icon('mdi6.new-box')),
    STATUSES.UPDATE:  QtGui.QIcon(qta.icon('mdi6.update')),
    STATUSES.DOWNLOAD: QtGui.QIcon(qta.icon('mdi6.download')),

}


class PluginProcessor(QtCore.QObject):

    def __init__(self):
        super(PluginProcessor, self).__init__()

        self.process_mapping = {
            STATUSES.NEW: self.install,
            STATUSES.UPDATE: self.update,
            STATUSES.REMOVE: self.remove,
            STATUSES.DOWNLOAD: self.install
        }

    def download(self, plugin):
        source_path = plugin.data(ROLES.PLUGIN_SOURCE_PATH)
        zip_name = os.path.basename(source_path)
        save_path = tempfile.gettempdir()
        temp_path = os.path.join(save_path, zip_name)
        logging.debug('Downloading {} to {}'.format(source_path, temp_path))

        with urllib.request.urlopen(source_path) as dl_file:
            with open(temp_path, 'wb') as out_file:
                out_file.write(dl_file.read())
        return temp_path

    def process(self, plugin):
        status = plugin.data(ROLES.PLUGIN_STATUS)
        plugin_fn = self.process_mapping.get(status)

        if not plugin_fn:
            return

        plugin_fn(plugin)

    def update(self, plugin):
        self.remove(plugin)
        self.install(plugin)

    def install(self, plugin):
        source_path = plugin.data(ROLES.PLUGIN_SOURCE_PATH)
        status = plugin.data(ROLES.PLUGIN_STATUS)
        if source_path.startswith('http'):
            source_path = self.download(plugin)

        plugin_name = os.path.basename(source_path).split('.zip')[0]

        install_path = os.path.dirname(plugin.data(ROLES.PLUGIN_INSTALL_PATH))
        destination_path = os.path.join(install_path, plugin_name)
        logging.debug('Installing {} to {}'.format(source_path, destination_path))

        with zipfile.ZipFile(source_path, 'r') as zip_ref:
            zip_ref.extractall(destination_path)

    def remove(self, plugin):
        install_path = plugin.data(ROLES.PLUGIN_INSTALL_PATH)
        logging.debug('Removing {}'.format(install_path))
        if os.path.exists(install_path) and os.path.isdir(install_path):
            shutil.rmtree(install_path, ignore_errors=False, onerror=None)


class PluginInstaller(ftrack_connect.ui.application.ConnectWidget):
    '''Base widget for ftrack connect actions plugin.'''

    plugin_re = re.compile(
        '(?P<name>(([A-Za-z-3-4]+)))-(?P<version>(\w.+))'
    )
    name = 'User Plugin Manager'
    # icon = qta.icon('mdi6.puzzle')

    # default methods
    def __init__(self, session, parent=None):
        '''Instantiate the actions widget.'''
        super(PluginInstaller, self).__init__(session, parent=parent)
        self.plugin_processor = PluginProcessor()
        self._main_ftrack_connect_plugin_path = None
        self.setAcceptDrops(True)
        self.setProperty('ftrackDropZone', True)
        self.setObjectName('ftrack-connect-publisher-browse-button')

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.plugin_list = QtWidgets.QListView()
        self.plugin_model = QtGui.QStandardItemModel(self)
        self.plugin_list.setModel(self.plugin_model)
        button_layout = QtWidgets.QHBoxLayout()
        self.apply_button = QtWidgets.QPushButton('Apply changes')
        button_layout.addWidget(self.apply_button)

        layout.addWidget(self.plugin_list)
        layout.addLayout(button_layout)

        # wire connections
        self.apply_button.clicked.connect(self._on_apply_changes)

        # overlays
        self.blockingOverlay = InstallerBlockingOverlay(self)
        self.blockingOverlay.hide()
        self.blockingOverlay.confirmButton.clicked.connect(self.refresh)

        # refresh
        self.refresh()

    def refresh(self):
        self.populate_installed_plugins()
        self.populate_download_plugins()

    def show_message(self):
        self.blockingOverlay.setMessage(
            'Installation finished!\n \n'
            'Please restart connect to pick up the changes.'
        )
        self.blockingOverlay.confirmButton.show()
        self.blockingOverlay.show()

    def _on_apply_changes(self, event):
        num_items = self.plugin_model.rowCount()
        for i in range(num_items):
            item = self.plugin_model.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                self.plugin_processor.process(item)

        self.show_message()

    def _processMimeData(self, mimeData):
        '''Return a list of valid filepaths.'''
        validPaths = []

        if not mimeData.hasUrls():
            QtWidgets.QMessageBox.warning(
                self,
                'Invalid file',
                'Invalid file: the dropped item is not a valid file.'
            )
            return validPaths

        for path in mimeData.urls():
            localPath = path.toLocalFile()
            if os.path.isfile(localPath):
                if localPath.endswith('.zip'):
                    validPaths.append(localPath)
            else:
                message = u'Invalid file: "{0}" is not a valid file.'.format(
                    localPath
                )
                if os.path.isdir(localPath):
                    message = (
                        'Folders not supported.\n\nIn the current version, '
                        'folders are not supported. This will be enabled in a '
                        'later release of ftrack connect.'
                    )
                QtWidgets.QMessageBox.warning(
                    self, 'Invalid file', message
                )

        return validPaths

    def dragEnterEvent(self, event):
        '''Override dragEnterEvent and accept all events.'''
        event.setDropAction(QtCore.Qt.CopyAction)
        event.accept()
        self._setDropZoneState('active')

    def dropEvent(self, event):
        '''Handle dropped file event.'''
        self._setDropZoneState()

        paths = self._processMimeData(
            event.mimeData()
        )

        for path in paths:
            self.addPlugin(path, STATUSES.NEW)

        event.accept()

    # custom methods
    def addPlugin(self, file_path, status=STATUSES.NEW):
        data = self._is_plugin_valid(file_path)

        if not data:
            return

        # create new plugin item and populate it with data
        plugin_id = str(hash(data['name']))
        data['id'] = plugin_id

        plugin_item = QtGui.QStandardItem()

        plugin_item.setCheckable(True)
        plugin_item.setEditable(False)
        plugin_item.setSelectable(False)

        plugin_item.setText('{} | {}'.format(data['name'], data['version']))
        plugin_item.setData(status, ROLES.PLUGIN_STATUS)
        plugin_item.setData(str(data['name']), ROLES.PLUGIN_NAME)
        new_plugin_version = LooseVersion(data['version'])
        plugin_item.setData(new_plugin_version, ROLES.PLUGIN_VERSION)
        plugin_item.setData(plugin_id, ROLES.PLUGIN_ID)
        plugin_item.setIcon(STATUS_ICONS[status])

        # check if is a new plugin.....
        stored_item = self.plugin_is_available(data)

        if not stored_item:
            # add new plugin
            if status == STATUSES.INSTALLED:
                plugin_item.setData(
                    file_path, ROLES.PLUGIN_INSTALL_PATH
                )
                plugin_item.setCheckable(False)

            elif status in [STATUSES.NEW, STATUSES.DOWNLOAD]:
                destination_path = os.path.join(
                    self._main_ftrack_connect_plugin_path,
                    os.path.basename(file_path)
                )

                plugin_item.setData(
                    destination_path, ROLES.PLUGIN_INSTALL_PATH
                )

                plugin_item.setData(
                    file_path, ROLES.PLUGIN_SOURCE_PATH
                )

            self.plugin_model.appendRow(plugin_item)
            return

        # update/remove plugin
        stored_status = stored_item.data(ROLES.PLUGIN_STATUS)
        if stored_status in [STATUSES.INSTALLED, STATUSES.DOWNLOAD] and status in [STATUSES.NEW, STATUSES.DOWNLOAD]:
            stored_plugin_version = stored_item.data(ROLES.PLUGIN_VERSION)
            should_update = stored_plugin_version < new_plugin_version
            if not should_update:
                return
            print('item {} should update with {}'.format(stored_item.text(), file_path))
            # update stored item.
            stored_item.setText('{} > {}'.format(stored_item.text(), new_plugin_version))
            stored_item.setData(STATUSES.UPDATE, ROLES.PLUGIN_STATUS)
            stored_item.setIcon(STATUS_ICONS[STATUSES.UPDATE])
            stored_item.setData(file_path, ROLES.PLUGIN_SOURCE_PATH)
            stored_item.setData(new_plugin_version, ROLES.PLUGIN_VERSION)
            # enable it by default if we are updating
            stored_item.setCheckable(True)
            stored_item.setCheckState(QtCore.Qt.Checked)

    def plugin_is_available(self, plugin_data):
        num_items = self.plugin_model.rowCount()
        for i in range(num_items):
            item = self.plugin_model.item(i)
            item_id = item.data(ROLES.PLUGIN_ID)
            if item_id == plugin_data['id']:
                return item
        return None

    def _is_plugin_valid(self, plugin_path):
        plugin_name = os.path.basename(plugin_path)
        match = self.plugin_re.match(plugin_name)
        if match:
            data = match.groupdict()
        else:
            return False

        if data['version'].endswith('.zip'):
            # pop zip extension from the version.
            # TODO: refine regex to catch extension
            data['version'] = data['version'][:-4]
        return data

    def populate_installed_plugins(self):
        self.plugin_model.clear()
        plugin_data = self._fetch_installed_plugins()
        for path, plugins in plugin_data.items():
            if path != self._main_ftrack_connect_plugin_path:
                continue
            for plugin in plugins:
                self.addPlugin(os.path.join(path, plugin), STATUSES.INSTALLED)

    def _fetch_installed_plugins(self):
        plugin_paths = os.environ.get('FTRACK_CONNECT_PLUGIN_PATH', '').split(os.pathsep)

        self._main_ftrack_connect_plugin_path = plugin_paths[0]
        if len(plugin_paths) > 1:
            logging.warning(
                'More than one FTRACK_CONNECT_PLUGIN_PATH found.\n'
                'Using {}.'.format(
                    self._main_ftrack_connect_plugin_path
                )
            )

        plugins_per_path = {
            self._main_ftrack_connect_plugin_path: os.listdir(
                self._main_ftrack_connect_plugin_path
            )
        }
        return plugins_per_path

    def populate_download_plugins(self):
        for link in download_plugins:
            self.addPlugin(link, STATUSES.DOWNLOAD)

    def _setDropZoneState(self, state='default'):
        '''Set drop zone state to *state*.

        *state* should be 'default', 'active' or 'invalid'.

        '''
        self.setProperty('ftrackDropZoneState', state)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


def register(session, **kw):
    '''Register plugin. Called when used as an plugin.'''
    # Validate that session is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an old or incompatible API and
    # return without doing anything.
    if not isinstance(session, ftrack_api.session.Session):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack_api.Session instance.'.format(session)
        )
        return

    #  Uncomment to register plugin
    plugin = ftrack_connect.ui.application.ConnectWidgetPlugin(PluginInstaller)
    plugin.register(session, priority=30)