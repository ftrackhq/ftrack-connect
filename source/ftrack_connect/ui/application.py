# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import platform
import sys
import requests
import requests.exceptions
import uuid
import logging
import weakref
from operator import itemgetter
import appdirs
import time
import urllib
import zipfile
import json
import tempfile
from ftrack_connect.qt import QtCore, QtWidgets, QtGui

import qtawesome as qta
from ftrack_connect import load_icons

import ftrack_api
import ftrack_api._centralized_storage_scenario
import ftrack_api.event.base
import ftrack_connect.usage
import ftrack_connect
import ftrack_connect.event_hub_thread as _event_hub_thread
import ftrack_connect.error
import ftrack_connect.util
import ftrack_connect.ui.theme
import ftrack_connect.ui.widget.overlay
from ftrack_connect.ui.widget import uncaught_error as _uncaught_error
from ftrack_connect.ui.widget import tab_widget as _tab_widget
from ftrack_connect.ui.widget import login as _login
from ftrack_connect.ui.widget import about as _about
from ftrack_connect.ui import login_tools as _login_tools
from ftrack_connect.ui.widget import configure_scenario as _scenario_widget
from ftrack_connect import usage
import ftrack_connect.ui.config
from ftrack_connect.asynchronous import asynchronous


class ConnectWidgetPlugin(object):
    topic = 'ftrack.connect.plugin.connect-widget'

    def __init__(self, connect_widget):
        '''Initialise class with non initialised connect_widget.'''
        if not isinstance(connect_widget, type):
            raise Exception(
                'Widget class {} should be non initialised'.format(
                    connect_widget
                )
            )

        self._connect_widget = connect_widget

    def _return_widget(self, event):
        '''Return stored widget class.'''
        return self._connect_widget

    def register(self, session, priority):
        '''register a new connect widget with given **priority**.'''
        session.event_hub.subscribe(
            'topic={0} '
            'and source.user.username={1}'.format(
                self.topic, session.api_user
            ),
            self._return_widget,
            priority=priority,
        )


class ConnectWidget(QtWidgets.QWidget):
    '''Base widget for ftrack connect application plugin.'''

    icon = None
    name = None

    #: Signal to emit to request focus of this plugin in application.
    requestApplicationFocus = QtCore.Signal(object)

    #: Signal to emit to request closing application.
    requestApplicationClose = QtCore.Signal(object)

    #: Signal to emit to request connect to restart.
    requestConnectRestart = QtCore.Signal()

    #: Signal to emit to request an icon update.
    requestIconUpdate = QtCore.Signal(object)

    @property
    def session(self):
        '''Return current session.'''
        return self._session

    def __init__(self, session, parent=None):
        '''Initialise class with ftrack *session* and *parent* widget.'''
        super(ConnectWidget, self).__init__(parent=parent)
        self._session = session

    def getName(self):
        '''Return name of widget.'''
        return self.name or self.__class__.__name__

    def getIdentifier(self):
        '''Return identifier for widget.'''
        return self.getName().lower().replace(' ', '.')


class WelcomePlugin(ConnectWidget):
    '''Welcome plugin widget.'''

    name = "Welcome"

    manager_installed = QtCore.Signal()
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
        '''Provide url where to download the plugin manager from.'''
        with urllib.request.urlopen(self.json_config_url) as url:
            data = json.loads(url.read().decode())
            plugins_url = [plugin_url for plugin_url in data.get('integrations') if 'plugin-manager' in plugin_url]
            url = None

            if plugins_url:
                url = plugins_url[0]
            else:
                self.install_button.setVisible(False)

            return url

    @asynchronous
    def install(self):
        '''Install provided *plugin* item.'''
        plugin_path = self.discover_plugin_manager()
        source_path = self.download(plugin_path)
        plugin_name = os.path.basename(source_path).split('.zip')[0]
        destination_path = os.path.join(self.install_path, plugin_name)
        logging.debug('Installing {} to {}'.format(source_path, destination_path))

        with zipfile.ZipFile(source_path, 'r') as zip_ref:
            zip_ref.extractall(destination_path)

        self.manager_installed.emit()

    def _on_manager_installed(self):
        self.install_button.setVisible(False)
        self.restart_button.setVisible(True)

    def __init__(self, session, parent=None):
        '''Instantiate the actions widget.'''
        super(WelcomePlugin, self).__init__(session, parent=parent)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(30, 0, 30, 0)
        self.setLayout(layout)
        spacer = QtWidgets.QSpacerItem(0, 70, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout.addItem(spacer)

        icon_label = QtWidgets.QLabel()
        icon = qta.icon("ph.rocket", color='#FFDD86', rotated=45, scale_factor=0.7)
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

        self.restart_button = QtWidgets.QPushButton(
            'Restart Now'
        )

        self.restart_button.setObjectName('primary')
        self.restart_button.setVisible(False)

        label_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        label_text.setWordWrap(True)

        layout.addWidget(label_title, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        layout.addWidget(icon_label, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        layout.addWidget(label_text, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        layout.addWidget(self.install_button)
        layout.addWidget(self.restart_button)

        spacer = QtWidgets.QSpacerItem(0, 300, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout.addItem(spacer)
        self.install_button.clicked.connect(self.install)
        self.discover_plugin_manager()
        self.manager_installed.connect(self._on_manager_installed)
        self.restart_button.clicked.connect(self.requestConnectRestart.emit)


class Application(QtWidgets.QMainWindow):
    '''Main application window for ftrack connect.'''

    #: Signal when login fails.
    loginError = QtCore.Signal(object)

    #: Signal when event received via ftrack's event hub.
    eventHubSignal = QtCore.Signal(object)

    # Login signal.
    loginSignal = QtCore.Signal(object, object, object)
    loginSuccessSignal = QtCore.Signal()

    def restart(self):
        '''restart connect application'''
        self.logger.info('Connect restarting....')
        QtWidgets.QApplication.quit()
        self._instance.__del__()

        # Give enough time to ensure the lockfile has been removed
        while os.path.exists(self._instance.lockfile):
            time.sleep(0.1)
        process = QtCore.QProcess()

        path = QtCore.QCoreApplication.applicationFilePath()
        args = QtCore.QCoreApplication.arguments()

        # Check if Connect is frozen (cx_freeze) and act accordingly.
        if not hasattr(sys, 'frozen'):
            path = sys.executable
        else:
            args.pop(0)

        status = -1

        self.logger.debug(
            f'Connect restarting with :: path: {path} argv: {args}'
        )
        try:
            status = process.startDetached(path, args)
        except Exception as error:
            self.logger.exception(str(error))

        self.logger.debug(f'Connect restarted with status {status}')

        return status

    def ftrack_title_icon(self, theme=None):
        logo_path = ':ftrack/titlebar/logo'
        return logo_path

    def ftrack_tray_icon(self, theme=None):
        logo_path = ':ftrack/logo/{}'

        theme = theme or self.system_theme()
        if platform.system() == 'Darwin':
            result_logo = logo_path.format('darwin/{}'.format(theme))
        else:
            result_logo = self.ftrack_title_icon(theme)

        return result_logo

    def system_theme(self, fallback='light'):
        # replicate content of https://github.com/albertosottile/darkdetect/blob/master/darkdetect/__init__.py
        # as does not work when frozen
        if sys.platform == "darwin":
            from darkdetect import _mac_detect as stylemodule

        elif sys.platform == "win32" and int(platform.release()) >= 10:
            from darkdetect import _windows_detect as stylemodule

        elif sys.platform == "linux":
            from darkdetect import _linux_detect as stylemodule

        current_theme = stylemodule.theme()
        if not current_theme:
            self.logger.warning(
                'System theme could not be determined, using: light'
            )
            current_theme = fallback

        return current_theme.lower()

    def emitConnectUsage(self):
        '''Emit data to intercom to track Connect data usage'''
        connect_stopped_time = time.time()

        metadata = {
            'label': 'ftrack-connect',
            'version': ftrack_connect.__version__,
            'os': platform.platform(),
            'session-duration': connect_stopped_time
            - self.__connect_start_time,
        }

        usage.send_event(
            self.session, 'USED-CONNECT', metadata, asynchronous=True
        )

    @property
    def session(self):
        '''Return current session.'''
        return self._session

    def __init__(self, theme='system', instance=None):
        '''Initialise the main application window.'''
        super(Application, self).__init__()
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self._instance = instance
        self._session = None
        self.__connect_start_time = time.time()

        self.defaultPluginDirectory = appdirs.user_data_dir(
            'ftrack-connect-plugins', 'ftrack'
        )
        self._createDefaultPluginDirectory()

        self.pluginHookPaths = self._discover_hook_paths()

        # Register widget for error handling.
        self.uncaughtError = _uncaught_error.UncaughtError(parent=self)

        if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            raise ftrack_connect.error.ConnectError('No system tray located.')

        self._login_server_thread = None
        self._initialiseTray()
        self._initialiseMenuBar()

        self.setTheme(theme)

        self.plugins = {}

        self.setObjectName('ftrack-connect-window')
        self.setWindowTitle('ftrack Connect')
        self.resize(450, 700)
        self.move(50, 50)

        self._login_overlay = None
        self.loginWidget = _login.Login(theme=self.theme())
        self.loginSignal.connect(self.loginWithCredentials)
        self.loginSuccessSignal.connect(self._post_login_settings)
        self.login()

    def _post_login_settings(self):

        if self.tray:
            self.tray.show()

    def _assign_session_theme(self, theme):
        if self.session:
            self.session.connect_theme = theme

    def theme(self):
        '''Return current theme.'''
        return self._theme

    def setTheme(self, theme='system'):
        '''Set *theme*.'''
        if theme not in ['light', 'dark']:
            theme = self.system_theme()

        self.logger.debug('Setting theme {}'.format(theme))
        self._theme = theme

        self.setWindowIcon(
            QtGui.QIcon(QtGui.QPixmap(self.ftrack_title_icon(theme)))
        )
        self.tray.setIcon(
            QtGui.QIcon(QtGui.QPixmap(self.ftrack_tray_icon(theme)))
        )

        qtawesome_style = getattr(qta, theme)
        qtawesome_style(QtWidgets.QApplication.instance())

        ftrack_connect.ui.theme.applyFont()
        ftrack_connect.ui.theme.applyTheme(self, self.theme(), 'cleanlooks')

    def _onConnectTopicEvent(self, event):
        '''Generic callback for all ftrack.connect events.

        .. note::
            Events not triggered by the current logged in user will be dropped.

        '''
        if event['topic'] != 'ftrack.connect':
            return

        self._routeEvent(event)

    def logout(self):
        '''Clear stored credentials and quit Connect.'''
        self._clear_qsettings()
        config = ftrack_connect.ui.config.read_json_config()

        config['accounts'] = []
        ftrack_connect.ui.config.write_json_config(config)

        QtWidgets.QApplication.quit()

    def _clear_qsettings(self):
        '''Remove credentials from QSettings.'''
        settings = QtCore.QSettings()
        settings.remove('login')

    def _get_credentials(self):
        '''Return a dict with API credentials from storage.'''
        credentials = None

        # Read from json config file.
        json_config = ftrack_connect.ui.config.read_json_config()
        if json_config:
            try:
                data = json_config['accounts'][0]
                credentials = {
                    'server_url': data['server_url'],
                    'api_user': data['api_user'],
                    'api_key': data['api_key'],
                }
            except Exception:
                self.logger.debug(
                    u'No credentials were found in config: {0}.'.format(
                        json_config
                    )
                )

        # Fallback on old QSettings.
        if not json_config and not credentials:
            settings = QtCore.QSettings()
            server_url = settings.value('login/server', None)
            api_user = settings.value('login/username', None)
            api_key = settings.value('login/apikey', None)

            if not None in (server_url, api_user, api_key):
                credentials = {
                    'server_url': server_url,
                    'api_user': api_user,
                    'api_key': api_key,
                }

        return credentials

    def _save_credentials(self, server_url, api_user, api_key):
        '''Save API credentials to storage.'''
        # Clear QSettings since they should not be used any more.
        self._clear_qsettings()

        # Save the credentials.
        json_config = ftrack_connect.ui.config.read_json_config()

        if not json_config:
            json_config = {}

        # Add a unique id to the config that can be used to identify this
        # machine.
        if not 'id' in json_config:
            json_config['id'] = str(uuid.uuid4())

        json_config['accounts'] = [
            {
                'server_url': server_url,
                'api_user': api_user,
                'api_key': api_key,
            }
        ]

        ftrack_connect.ui.config.write_json_config(json_config)

    def login(self):
        '''Login using stored credentials or ask user for them.'''
        credentials = self._get_credentials()
        self.showLoginWidget()

        if credentials:
            # Try to login.
            self.loginWithCredentials(
                credentials['server_url'],
                credentials['api_user'],
                credentials['api_key'],
            )

    def showLoginWidget(self):
        '''Show the login widget.'''
        self._login_overlay = ftrack_connect.ui.widget.overlay.CancelOverlay(
            self.loginWidget, message='<h2>Signing in<h2/>'
        )

        self._login_overlay.hide()
        self.setCentralWidget(self.loginWidget)
        self.loginWidget.login.connect(self._login_overlay.show)
        self.loginWidget.login.connect(self.loginWithCredentials)
        self.loginError.connect(self.loginWidget.loginError.emit)
        self.loginError.connect(self._login_overlay.hide)
        self.focus()

        # Set focus on the login widget to remove any focus from its child
        # widgets.
        self.loginWidget.setFocus()
        self._login_overlay.hide()

    def _setup_session(self, plugin_paths=None):
        '''Setup a new python API session.'''
        if hasattr(self, '_hub_thread'):
            self._hub_thread.cleanup()

        if plugin_paths is None:
            plugin_paths = self.pluginHookPaths
        try:
            session = ftrack_api.Session(
                auto_connect_event_hub=True, plugin_paths=plugin_paths
            )
        except Exception as error:
            raise ftrack_connect.error.ParseError(error)

        # Listen to events using the new API event hub. This is required to
        # allow reconfiguring the storage scenario.
        self._hub_thread = _event_hub_thread.NewApiEventHubThread(self)

        self._hub_thread.start(session)
        weakref.finalize(self._hub_thread, self._hub_thread.cleanup)

        ftrack_api._centralized_storage_scenario.register_configuration(
            session
        )

        return session

    def _report_session_setup_error(self, error):
        '''Format error message and emit loginError.'''
        msg = (
            u'\nAn error occured while starting ftrack-connect: <b>{0}</b>.'
            u'\nPlease check log file for more informations.'
            u'\nIf the error persists please send the log file to:'
            u' support@ftrack.com'.format(error)
        )
        self.loginError.emit(msg)

    def loginWithCredentials(self, url, username, apiKey):
        '''Connect to *url* with *username* and *apiKey*.

        loginError will be emitted if this fails.

        '''
        # Strip all leading and preceeding occurances of slash and space.
        url = url.strip('/ ')

        if not url:
            self.loginError.emit(
                'You need to specify a valid server URL, '
                'for example https://server-name.ftrackapp.com'
            )
            return

        if not 'http' in url:
            if url.endswith('ftrackapp.com'):
                url = 'https://' + url
            else:
                url = 'https://{0}.ftrackapp.com'.format(url)

        try:
            result = requests.get(
                url,
            )
        except requests.exceptions.RequestException:
            self.logger.exception('Error reaching server url.')
            self.loginError.emit(
                'The server URL you provided could not be reached.'
            )
            return

        if result.status_code != 200 or 'FTRACK_VERSION' not in result.headers:
            self.loginError.emit(
                'The server URL you provided is not a valid ftrack server.'
            )
            return

        # If there is an existing server thread running we need to stop it.
        if self._login_server_thread:
            self._login_server_thread.quit()
            self._login_server_thread = None

        # If credentials are not properly set, try to get them using a http
        # server.
        if not username or not apiKey:
            self._login_server_thread = _login_tools.LoginServerThread()
            self._login_server_thread.loginSignal.connect(self.loginSignal)
            self._login_server_thread.finished.connect(
                self._login_server_thread.deleteLater
            )
            self._login_server_thread.start(url)
            return

        # Set environment variables supported by the new API.
        os.environ['FTRACK_SERVER'] = url
        os.environ['FTRACK_API_USER'] = username
        os.environ['FTRACK_API_KEY'] = apiKey

        # Login using the new ftrack API.
        try:
            # Quick session to poll for settings, confirm credentials
            self._session = self._setup_session(plugin_paths='')
            self._assign_session_theme(self.theme())
        except Exception as error:
            self.logger.exception('Error during login:')
            self._report_session_setup_error(error)
            return

        # Store credentials since login was successful.
        self._save_credentials(url, username, apiKey)

        # Verify storage scenario before starting.
        if 'storage_scenario' in self.session.server_information:
            storage_scenario = self.session.server_information.get(
                'storage_scenario'
            )
            if storage_scenario is None:
                ftrack_api.plugin.discover(
                    self.pluginHookPaths, [self.session]
                )
                # Hide login overlay at this time since it will be deleted
                self.logger.debug('Storage scenario is not configured.')
                scenario_widget = _scenario_widget.ConfigureScenario(
                    self.session
                )
                scenario_widget.configuration_completed.connect(
                    self.location_configuration_finished
                )
                self.setCentralWidget(scenario_widget)
                self.focus()
                self.loginSuccessSignal.emit()
                return

        # No change so build if needed
        self.location_configuration_finished(reconfigure_session=False)
        self.loginSuccessSignal.emit()

    def location_configuration_finished(self, reconfigure_session=True):
        '''Continue connect setup after location configuration is done.'''
        if reconfigure_session:
            try:
                self.session.event_hub.disconnect(False)
            except ftrack_api.exception.EventHubConnectionError:
                # Maybe it wasn't connected yet.
                self.logger.exception('Failed to disconnect from event hub.')
                pass

        self._session = self._setup_session()

        try:
            self.configureConnectAndDiscoverPlugins()
        except Exception as error:
            self.logger.exception(u'Error during location configuration:')
            self._report_session_setup_error(error)
        else:
            self.focus()

        # Send verify startup event to verify that storage scenario is
        # working correctly.
        event = ftrack_api.event.base.Event(
            topic='ftrack.connect.verify-startup',
            data={
                'storage_scenario': self.session.server_information.get(
                    'storage_scenario'
                )
            },
        )
        results = self.session.event_hub.publish(event, synchronous=True)
        problems = [problem for problem in results if isinstance(problem, str)]
        if problems:
            msgBox = QtWidgets.QMessageBox(parent=self)
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
            msgBox.setText('\n\n'.join(problems))
            msgBox.exec_()

    def configureConnectAndDiscoverPlugins(self):
        '''Configure connect and load plugins.'''

        self.tabPanel = _tab_widget.TabWidget()
        self.tabPanel.tabBar().setObjectName('application-tab-bar')
        self.setCentralWidget(self.tabPanel)

        self.session.event_hub.subscribe(
            'topic=ftrack.connect and source.user.username="{0}"'.format(
                self.session.api_user
            ),
            self._relayEventHubEvent,
        )
        self.eventHubSignal.connect(self._onConnectTopicEvent)

        self.focus()

        # Listen to discover connect event and respond to let the sender know
        # that connect is running.
        self.session.event_hub.subscribe(
            'topic=ftrack.connect.discover and source.user.username="{0}"'.format(
                self.session.api_user
            ),
            lambda event: True,
        )
        self.session._configure_locations()
        self._discoverConnectWidget()

    def _discover_hook_paths(self):
        '''Return a list of paths to pass to ftrack_api.Session()'''

        plugin_paths = []

        plugin_paths.extend(
            self._gatherPluginHooks(self.defaultPluginDirectory)
        )

        for apiPluginPath in os.environ.get(
            'FTRACK_EVENT_PLUGIN_PATH', ''
        ).split(os.pathsep):
            if apiPluginPath not in plugin_paths:
                plugin_paths.append(os.path.expandvars(apiPluginPath))

        for connectPluginPath in os.environ.get(
            'FTRACK_CONNECT_PLUGIN_PATH', ''
        ).split(os.pathsep):
            plugin_paths.extend(
                self._gatherPluginHooks(os.path.expandvars(connectPluginPath))
            )

        self.logger.info(
            u'Connect plugin hooks directories: {0}'.format(
                ', '.join(plugin_paths)
            )
        )

        return list(plugin_paths)

    def _gatherPluginHooks(self, path):
        '''Return plugin hooks from *path*.'''
        paths = []
        self.logger.debug(u'Searching {0!r} for plugin hooks.'.format(path))

        if os.path.isdir(path):
            for candidate in os.listdir(path):
                candidate_path = os.path.join(path, candidate)
                if os.path.isdir(candidate_path):
                    full_hook_path = os.path.join(candidate_path, 'hook')
                    if full_hook_path not in paths:
                        paths.append(full_hook_path)

        self.logger.debug(
            u'Found {0!r} plugin hooks in {1!r}.'.format(paths, path)
        )

        return paths

    def _relayEventHubEvent(self, event):
        '''Relay all ftrack.connect events.'''
        self.eventHubSignal.emit(event)

    def _initialiseTray(self):
        '''Initialise and add application icon to system tray.'''
        self.trayMenu = self._createTrayMenu()

        self.tray = QtWidgets.QSystemTrayIcon(self)

        self.tray.setContextMenu(self.trayMenu)

    def _initialiseMenuBar(self):
        '''Initialise and add connect widget to widgets menu.'''

        self.menu_bar = QtWidgets.QMenuBar()
        self.setMenuWidget(self.menu_bar)
        widget_menu = self.menu_bar.addMenu('Widgets')
        self.menu_widget = widget_menu
        self.menu_bar.setVisible(False)

    def _createTrayMenu(self):
        '''Return a menu for system tray.'''
        menu = QtWidgets.QMenu(self)

        logoutAction = QtWidgets.QAction(
            'Log Out && Quit', self, triggered=self.logout
        )

        quitAction = QtWidgets.QAction(
            'Quit', self, triggered=QtWidgets.QApplication.quit
        )

        focusAction = QtWidgets.QAction('Open', self, triggered=self.focus)

        openPluginDirectoryAction = QtWidgets.QAction(
            'Open plugin directory',
            self,
            triggered=self.openDefaultPluginDirectory,
        )

        aboutAction = QtWidgets.QAction(
            'About', self, triggered=self.showAbout
        )

        alwaysOnTopAction = QtWidgets.QAction('Always on top', self)
        restartAction = QtWidgets.QAction(
            'Restart', self, triggered=self.restart
        )
        alwaysOnTopAction.setCheckable(True)
        alwaysOnTopAction.triggered[bool].connect(self.setAlwaysOnTop)

        menu.addAction(aboutAction)
        menu.addSeparator()
        menu.addAction(focusAction)
        menu.addAction(alwaysOnTopAction)
        menu.addSeparator()

        menu.addAction(openPluginDirectoryAction)
        menu.addSeparator()

        menu.addAction(logoutAction)
        menu.addSeparator()
        menu.addAction(restartAction)
        menu.addAction(quitAction)

        return menu

    def _discoverConnectWidget(self):
        '''Find and load connect widgets in search paths.'''

        event = ftrack_api.event.base.Event(topic=ConnectWidgetPlugin.topic)

        responses = self.session.event_hub.publish(event, synchronous=True)
        if not responses:
            widget_plugin = WelcomePlugin(self.session)
            identifier = widget_plugin.getIdentifier()
            if not self.plugins.get(identifier):
                self.plugins[identifier] = widget_plugin
                self.addPlugin(widget_plugin)
        else:
            for ResponsePlugin in responses:

                try:
                    load_icons(os.path.join(os.path.dirname(__file__),  '..', 'fonts'))
                    widget_plugin = ResponsePlugin(self.session)

                except Exception:
                    self.logger.exception(
                        msg='Error while loading plugin : {}'.format(widget_plugin)
                    )
                    continue

                if not isinstance(widget_plugin, ConnectWidget):
                    self.logger.warning(
                        'Widget {} is not a valid ConnectWidget'.format(
                            widget_plugin
                        )
                    )
                    continue
                try:
                    identifier = widget_plugin.getIdentifier()
                    if not self.plugins.get(identifier):
                        self.plugins[identifier] = widget_plugin
                    else:
                        self.logger.debug(
                            'Widget {} already registered'.format(identifier)
                        )
                        continue

                    self.addPlugin(widget_plugin)

                except Exception as error:
                    self.logger.warning(
                        'Connect Widget Plugin "{}" could not be loaded. Reason: {}'.format(
                            widget_plugin.getName(), str(error)
                        )
                    )

    def _routeEvent(self, event):
        '''Route websocket *event* to publisher plugin.

        Expect event['data'] to contain:

            * plugin - The name of the plugin to route to.
            * action - The action to execute on the plugin.

        Raise `ConnectError` if no plugin is found or if action is missing on
        plugin.

        '''
        plugin = event['data']['plugin']
        action = event['data']['action']

        try:
            pluginInstance = self.plugins[plugin]
        except KeyError:
            raise ftrack_connect.error.ConnectError(
                'Plugin "{0}" not found.'.format(plugin)
            )

        try:
            method = getattr(pluginInstance, action)
        except AttributeError:
            raise ftrack_connect.error.ConnectError(
                'Method "{0}" not found on "{1}" plugin({2}).'.format(
                    action, plugin, pluginInstance
                )
            )

        method(event)

    def _onWidgetRequestApplicationFocus(self, widget):
        '''Switch tab to *widget* and bring application to front.'''
        self.tabPanel.setCurrentWidget(widget)
        self.focus()

    def _onWidgetRequestApplicationClose(self, widget):
        '''Hide application upon *widget* request.'''
        self.hide()

    def addPlugin(self, plugin, name=None):
        '''Add *plugin* in new tab with *name* and *identifier*.

        *plugin* should be an instance of :py:class:`ApplicationPlugin`.

        *name* will be used as the label for the tab. If *name* is None then
        plugin.getName() will be used.

        *identifier* will be used for routing events to plugins. If
        *identifier* is None then plugin.getIdentifier() will be used.

        '''
        if name is None:
            name = plugin.getName()

        icon = self._prep_tab_icon(plugin.icon)

        self.tabPanel.addTab(plugin, icon, name)

        # Connect standard plugin events.
        plugin.requestApplicationFocus.connect(
            self._onWidgetRequestApplicationFocus
        )
        plugin.requestApplicationClose.connect(
            self._onWidgetRequestApplicationClose
        )
        plugin.requestConnectRestart.connect(
            self.restart
        )
        plugin.requestIconUpdate.connect(
            self.update_tab_icon
        )

    def _prep_tab_icon(self, icon):
        icon = None
        try:
            icon = qta.icon(icon)
        except Exception as err:
            icon = QtGui.QIcon(icon)
        return icon

    def update_tab_icon(self, icon):
        widget = self.sender()
        widget_index = self.tabPanel.indexOf(widget)
        new_icon = self._prep_tab_icon(icon)
        self.tabPanel.setTabIcon(widget_index, new_icon)

    def removePlugin(self, plugin):
        '''Remove plugin registered with *identifier*.

        Raise :py:exc:`KeyError` if no plugin with *identifier* has been added.

        '''
        identifier = plugin.getIdentifier()
        registered_plugin = self.plugins.get(identifier)

        if registered_plugin is None:
            self.logger.warning(
                'No plugin registered with identifier "{0}".'.format(
                    identifier
                )
            )
            return

        index = self.tabPanel.indexOf(registered_plugin)
        self.tabPanel.removeTab(index)

    def focus(self):
        '''Focus and bring the window to top.'''
        self.activateWindow()
        self.show()
        self.raise_()

    def setAlwaysOnTop(self, state):
        '''Set the application window to be on top'''
        if state:
            self.setWindowFlags(
                self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint
            )
        else:
            self.setWindowFlags(
                self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint
            )
        self.focus()

    def showAbout(self):
        '''Display window with about information.'''
        self.focus()

        aboutDialog = _about.AboutDialog(self)

        environmentData = os.environ.copy()
        environmentData.update(
            {
                'PLATFORM': platform.platform(),
                'PYTHON_VERSION': platform.python_version(),
            }
        )

        versionData = [
            {
                'name': 'ftrack connect',
                'version': ftrack_connect.__version__,
                'core': True,
                'debug_information': environmentData,
            }
        ]

        # Gather information about API versions and other
        # plugin hooks.

        try:
            event = ftrack_api.event.base.Event(
                topic='ftrack.connect.plugin.debug-information'
            )

            responses = self.session.event_hub.publish(event, synchronous=True)

            for response in responses:
                if isinstance(response, dict):
                    versionData.append(response)
                elif isinstance(response, list):
                    versionData = versionData + response

        except Exception as error:
            self.logger.error(error)

        sorted_version_data = sorted(versionData, key=itemgetter('name'))

        aboutDialog.setInformation(
            versionData=sorted_version_data,
            server=os.environ.get('FTRACK_SERVER', 'Not set'),
            user=self.session.api_user,
            widget_plugins=self.plugins,
        )

        aboutDialog.exec_()

    def _createDefaultPluginDirectory(self):
        directory = self.defaultPluginDirectory

        if not os.path.exists(directory):
            # Create directory if not existing.
            try:
                os.makedirs(directory)
            except Exception:
                raise

        return directory

    def openDefaultPluginDirectory(self):
        '''Open default plugin directory in platform default file browser.'''

        try:
            self._createDefaultPluginDirectory()
        except OSError:
            messageBox = QtWidgets.QMessageBox(parent=self)
            messageBox.setIcon(QtWidgets.QMessageBox.Warning)
            messageBox.setText(
                u'Could not open or create default plugin '
                u'directory: {0}.'.format(self.defaultPluginDirectory)
            )
            messageBox.exec_()
            return

        ftrack_connect.util.open_directory(self.defaultPluginDirectory)
