# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack
import os
import re
import ftrack_api
import logging
from Qt import QtWidgets, QtCore, QtGui
import qtawesome as qta
from distutils.version import LooseVersion

import ftrack_connect.ui.application
logger = logging.getLogger('ftrack_connect.plugin.plugin_installer')


class STATUSES(object):
    INSTALLED = 0
    NEW = 1
    UPDATE = 2


class ROLES(object):
    PLUGIN_STATUS = QtCore.Qt.UserRole + 1
    PLUGIN_NAME = PLUGIN_STATUS + 1
    PLUGIN_VERSION = PLUGIN_NAME + 1
    PLUGIN_PATH = PLUGIN_VERSION + 1


STATUS_ICONS = {
    STATUSES.INSTALLED: QtGui.QIcon(qta.icon('mdi6.harddisk')),
    STATUSES.NEW:  QtGui.QIcon(qta.icon('mdi6.new-box')),
    STATUSES.UPDATE:  QtGui.QIcon(qta.icon('mdi6.update')),
}


class PluginInstaller(ftrack_connect.ui.application.ConnectWidget):
    '''Base widget for ftrack connect actions plugin.'''

    plugin_re = re.compile(
        '(?P<name>(([A-Za-z-]+)))-(?P<version>(\w.+))'
    )
    name = 'User Plugin Manager'

    # default methods
    def __init__(self, session, parent=None):
        '''Instantiate the actions widget.'''
        super(PluginInstaller, self).__init__(session, parent=parent)
        self.setAcceptDrops(True)
        self.setProperty('ftrackDropZone', True)
        self.setObjectName('ftrack-connect-publisher-browse-button')

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.plugin_list = QtWidgets.QListView()
        self.plugin_model = QtGui.QStandardItemModel(self)
        self.plugin_list.setModel(self.plugin_model)
        button_layout = QtWidgets.QHBoxLayout()
        apply_button = QtWidgets.QPushButton('Apply changes')
        button_layout.addWidget(apply_button)

        layout.addWidget(self.plugin_list)
        layout.addLayout(button_layout)
        self.populuate_installed_plugins()

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

        # TODO: Allow hook into the dropEvent.

        paths = self._processMimeData(
            event.mimeData()
        )

        for path in paths:
            self.addPlugin(path, STATUSES.NEW)

        event.accept()

    # custom methods
    def addPlugin(self, file_path, status=STATUSES.NEW):
        data = self._is_plugin_valid(os.path.basename(file_path))

        if not data:
            return

        # create new plugin item and populate it with data
        plugin_item = QtGui.QStandardItem('{}\t\r{}'.format(data['name'], data['version']))
        plugin_item.setData(status, ROLES.PLUGIN_STATUS)
        plugin_item.setData(data['name'], ROLES.PLUGIN_NAME)
        plugin_item.setData(os.path.abspath(file_path), ROLES.PLUGIN_PATH)
        new_plugin_version = LooseVersion(data['version'])
        plugin_item.setData(new_plugin_version, ROLES.PLUGIN_VERSION)
        plugin_item.setIcon(STATUS_ICONS[status])

        # check if is a new plugin.....
        stored_item = self.plugin_is_available(data)
        if not stored_item:
            # add new plugin
            # logger.info('Adding new {}'.format(data))
            self.plugin_model.appendRow(plugin_item)
            return

        # plugin already exist.... let's check what we need to do....
        stored_status = stored_item.data(ROLES.PLUGIN_STATUS)

        if stored_status == STATUSES.INSTALLED and status == STATUSES.NEW:
            stored_plugin_version = stored_item.data(ROLES.PLUGIN_VERSION)
            should_update = stored_plugin_version < new_plugin_version
            if not should_update:
                return

            logger.info('updating : {} to version {} from {}'.format(data['name'], new_plugin_version, stored_plugin_version))
            stored_item.setText('{} > {}'.format(stored_item.text(), new_plugin_version))
            stored_item.setData(STATUSES.UPDATE, ROLES.PLUGIN_STATUS)
            stored_item.setIcon(STATUS_ICONS[STATUSES.UPDATE])

    def plugin_is_available(self, plugin_data):

        found = self.plugin_model.match(
            self.plugin_model.index(0, 0),
            ROLES.PLUGIN_NAME,
            plugin_data['name']
        )

        if not found:
            return
        result = self.plugin_model.item(found[0].row())
        return result

    def _is_plugin_valid(self, plugin):
        match = self.plugin_re.match(plugin)
        if match:
            data = match.groupdict()
        else:
            return False
        if data['version'].endswith('.zip'):
            data['version'] = data['version'][:-4]
        return data

    def populuate_installed_plugins(self):
        plugin_data = self._fetch_installed_plugins()
        for path, plugins in plugin_data.items():
            for plugin in plugins:
                self.addPlugin(os.path.join(path, plugin), STATUSES.INSTALLED)

    def _fetch_installed_plugins(self):
        plugin_paths = os.environ.get('FTRACK_CONNECT_PLUGIN_PATH', '').split(os.pathsep)
        plugins_per_path = {}
        for plugin_path in plugin_paths:
            if not plugin_path:
                continue
            plugins_per_path.setdefault(plugin_path, [])
            plugins_per_path[plugin_path] = os.listdir(plugin_path)

        return plugins_per_path

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