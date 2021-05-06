# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import platform
import requests
import requests.exceptions
import uuid
import logging
import weakref

import appdirs

from Qt import QtCore, QtWidgets, QtGui

import ftrack_api
import ftrack_api._centralized_storage_scenario
import ftrack_api.event.base

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
from ftrack_connect.error import NotUniqueError as _NotUniqueError
from ftrack_connect.ui import login_tools as _login_tools
from ftrack_connect.ui.widget import configure_scenario as _scenario_widget
import ftrack_connect.ui.config



class ConnectWidget(QtWidgets.QWidget):
    '''Base widget for ftrack connect application plugin.'''
    topic = 'ftrack.connect.plugin.connect-widget'
    icon = None
    #: Signal to emit to request focus of this plugin in application.
    requestApplicationFocus = QtCore.Signal(object)

    #: Signal to emit to request closing application.
    requestApplicationClose = QtCore.Signal(object)

    @property
    def session(self):
        '''Return current session.'''
        return self._session

    def __init__(self, session, parent=None):
        super(ConnectWidget, self).__init__(parent=parent)
        self._session = session

    def getName(self):
        '''Return name of widget.'''
        return self.__class__.__name__

    def getIdentifier(self):
        '''Return identifier for widget.'''
        return self.getName().lower().replace(' ', '.')

    def _return_widget(self, event):
        return self

    def register(self, priority):
        '''register a new connect widget with given **priority**.'''
        priority = -100000 + priority
        self.session.event_hub.subscribe(
            'topic={0} '
            'and source.user.username={1}'.format(
                self.topic, self.session.api_user
            ),
            self._return_widget,
            priority=priority
        )


class PluginWarning(ConnectWidget):
    '''Warning missing plugin widget.'''
    def __init__(self, session, parent=None):
        '''Instantiate the actions widget.'''
        super(PluginWarning, self).__init__(session, parent=parent)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        label = QtWidgets.QLabel(
            'Warning!  no tab plugin found to register for connect.'
        )
        layout.addWidget(label, QtCore.Qt.AlignCenter)


class Application(QtWidgets.QMainWindow):
    '''Main application window for ftrack connect.'''

    #: Signal when login fails.
    loginError = QtCore.Signal(object)

    #: Signal when event received via ftrack's event hub.
    eventHubSignal = QtCore.Signal(object)

    # Login signal.
    loginSignal = QtCore.Signal(object, object, object)
    loginSuccessSignal = QtCore.Signal()

    @property
    def session(self):
        '''Return current session.'''
        return self._session

    def __init__(self, theme='light'):
        '''Initialise the main application window.'''
        super(Application, self).__init__()
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._session = None

        self.defaultPluginDirectory = appdirs.user_data_dir(
            'ftrack-connect-plugins', 'ftrack'
        )

        self.pluginHookPaths = self._discover_hook_paths()

        # Register widget for error handling.
        self.uncaughtError = _uncaught_error.UncaughtError(
            parent=self
        )

        if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            raise ftrack_connect.error.ConnectError(
                'No system tray located.'
            )

        self.logoIcon = QtGui.QIcon(
            QtGui.QPixmap(':/ftrack/image/default/ftrackLogoGreyDark')
        )

        self._login_server_thread = None

        self._theme = None
        self.setTheme(theme)

        self.plugins = {}

        self.setObjectName('ftrack-connect-window')
        self.setWindowTitle('ftrack connect')
        self.resize(450, 700)
        self.move(50, 50)

        self.setWindowIcon(self.logoIcon)

        self._initialiseTray()
        self._initialiseMenuBar()

        self._login_overlay = None
        self.loginWidget = _login.Login(theme=theme)
        self.loginSignal.connect(self.loginWithCredentials)
        self.loginSuccessSignal.connect(self._post_login_settings)
        self.login()

    def _post_login_settings(self):

        if self.menu_bar:
            self.menu_bar.setVisible(True)

        if self.tray:
            self.tray.show()

    def _assign_session_theme(self, theme):
        if self.session:
            self.session.connect_theme = theme

    def theme(self):
        '''Return current theme.'''
        return self._theme

    def setTheme(self, theme):
        '''Set *theme*.'''
        self._theme = theme
        ftrack_connect.ui.theme.applyFont()
        ftrack_connect.ui.theme.applyTheme(self, self._theme, 'cleanlooks')

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
                    'api_key': data['api_key']
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
                    'api_key': api_key
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

        json_config['accounts'] = [{
            'server_url': server_url,
            'api_user': api_user,
            'api_key': api_key
        }]

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
                credentials['api_key']
            )

    def showLoginWidget(self):
        '''Show the login widget.'''
        self._login_overlay = ftrack_connect.ui.widget.overlay.CancelOverlay(
            self.loginWidget,
            message='Signing in'
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
                auto_connect_event_hub=True,
                plugin_paths=plugin_paths
            )
        except Exception as error:
            raise ftrack_connect.error.ParseError(error)

        # Listen to events using the new API event hub. This is required to
        # allow reconfiguring the storage scenario.
        self._hub_thread = _event_hub_thread.NewApiEventHubThread()
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

        if (
            result.status_code != 200 or 'FTRACK_VERSION' not in result.headers
        ):
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
                ftrack_api.plugin.discover(self.pluginHookPaths, [self.session])
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

        ftrack_api.plugin.discover(self.pluginHookPaths, [self.session])

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
            }
        )
        results = self.session.event_hub.publish(event, synchronous=True)
        problems = [
            problem for problem in results if isinstance(problem, str)
        ]
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

        self._discoverConnectWidget()

        self.session.event_hub.subscribe(
            'topic=ftrack.connect and source.user.username="{0}"'.format(
                self.session.api_user
            ),
            self._relayEventHubEvent
        )
        self.eventHubSignal.connect(self._onConnectTopicEvent)

        self.focus()

        # Listen to discover connect event and respond to let the sender know
        # that connect is running.
        self.session.event_hub.subscribe(
            'topic=ftrack.connect.discover and source.user.username="{0}"'.format(
                self.session.api_user
            ),
            lambda event : True
        )
        self.session._configure_locations()

    def _discover_hook_paths(self):
        '''Return a list of paths to pass to ftrack_api.Session()'''

        plugin_paths = set()

        plugin_paths.update(
            self._gatherPluginHooks(
                self.defaultPluginDirectory
            )
        )

        for apiPluginPath in (
            os.environ.get('FTRACK_EVENT_PLUGIN_PATH', '').split(os.pathsep)
        ):
            plugin_paths.add(
                    os.path.expandvars(apiPluginPath)
            )

        for connectPluginPath in (
            os.environ.get('FTRACK_CONNECT_PLUGIN_PATH', '').split(os.pathsep)
        ):
            plugin_paths.update(
                self._gatherPluginHooks(
                    os.path.expandvars(connectPluginPath)
                )
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
                candidatePath = os.path.join(path, candidate)
                if os.path.isdir(candidatePath):
                    paths.append(
                        os.path.join(candidatePath, 'hook')
                    )

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

        self.tray.setContextMenu(
            self.trayMenu
        )
        self.tray.setIcon(self.logoIcon)

    def _initialiseMenuBar(self):
        '''Initialise and add connect widget to widgets menu.'''

        self.menu_bar = QtWidgets.QMenuBar()
        self.setMenuWidget(self.menu_bar)
        widget_menu = self.menu_bar.addMenu('widgets')
        self.menu_widget = widget_menu
        self.menu_bar.setVisible(False)

    def _get_widget_preferences(self):
        '''Return a dict with API credentials from storage.'''
        widgets = {}

        # Read from json config file.
        json_config = ftrack_connect.ui.config.read_json_config()
        if json_config:
            try:
                widgets = json_config['widgets']
            except Exception:
                self.logger.debug(
                    u'No widget preferences were found in config: {0}.'.format(
                        json_config
                    )
                )

        # Fallback on old QSettings.
        if not json_config and not widgets:
            settings = QtCore.QSettings()
            settings.value('widgets', {})

        return widgets

    def _save_widget_preferences(self, plugin_name, state):
        '''Save widget preferences to storage.'''
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
        json_config.setdefault('widgets', {})
        json_config['widgets'][plugin_name] = state
        ftrack_connect.ui.config.write_json_config(json_config)

    def _createTrayMenu(self):
        '''Return a menu for system tray.'''
        menu = QtWidgets.QMenu(self)

        logoutAction = QtWidgets.QAction(
            'Log Out && Quit', self,
            triggered=self.logout
        )

        quitAction = QtWidgets.QAction(
            'Quit', self,
            triggered=QtWidgets.QApplication.quit
        )

        focusAction = QtWidgets.QAction(
            'Open', self,
            triggered=self.focus
        )

        openPluginDirectoryAction = QtWidgets.QAction(
            'Open plugin directory', self,
            triggered=self.openDefaultPluginDirectory
        )

        aboutAction = QtWidgets.QAction(
            'About', self,
            triggered=self.showAbout
        )

        menu.addAction(aboutAction)
        menu.addAction(focusAction)
        menu.addSeparator()

        menu.addAction(openPluginDirectoryAction)
        menu.addSeparator()

        menu.addAction(logoutAction)
        menu.addSeparator()
        menu.addAction(quitAction)

        return menu

    def _creteConnectWidgetMenu(self, entry,  stored_state):
        '''create widget menu off plugin *entry* and *stored_state* in preferences store.'''
        widget_menu_action = QtWidgets.QAction(entry.getName(), self)
        widget_menu_action.setData(entry)
        widget_menu_action.setCheckable(True)
        widget_menu_action.setChecked(stored_state)
        widget_menu_action.changed.connect(self._manage_custom_widget)
        self.menu_widget.addAction(widget_menu_action)

    def _discoverConnectWidget(self):
        '''Find and load connect widgets in search paths.'''
        #: TODO: Add discover functionality and search paths.

        event = ftrack_api.event.base.Event(
            topic = ConnectWidget.topic
        )

        responses = self.session.event_hub.publish(
            event, synchronous=True
        )
        widgets = self._get_widget_preferences()

        for response in responses:
            stored_state = True
            try:
                stored_state = widgets.get(response.getName(), stored_state)
                self._creteConnectWidgetMenu(response, stored_state)
                self._setConnectWidgetState(response, stored_state)

            except Exception:
                self.logger.warning(
                    'Tab Plugin {} could not be loaded'.format(
                        response.getName()
                    )
                )

    def _setConnectWidgetState(self, item, state):
        '''Set plugin *item* as give visible *state*'''
        plugin_exists = self.plugins.get(item.getIdentifier())
        if not plugin_exists:
            self.plugins[item.getIdentifier()] = item

        if state is False:
            self.removePlugin(item.getIdentifier())

        elif state is True:
            self.addPlugin(item)

        self._save_widget_preferences(item.getName(), state)

    def _manage_custom_widget(self):
        action = self.sender()
        state = action.isChecked()
        item = action.data()
        self._setConnectWidgetState(item, state)

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
                'Plugin "{0}" not found.'.format(
                    plugin
                )
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

    def addPlugin(self, plugin, name=None, identifier=None):
        '''Add *plugin* in new tab with *name* and *identifier*.

        *plugin* should be an instance of :py:class:`ApplicationPlugin`.

        *name* will be used as the label for the tab. If *name* is None then
        plugin.getName() will be used.

        *identifier* will be used for routing events to plugins. If
        *identifier* is None then plugin.getIdentifier() will be used.

        '''
        if name is None:
            name = plugin.getName()

        if identifier is None:
            identifier = plugin.getIdentifier()

        # if identifier in self.plugins:
        #     self.logger.warning(
        #         'An existing plugin has already been '
        #         'registered with identifier {0}, it will be replaced'.format(identifier)
        #     )

        if identifier not in self.plugins:
            self.plugins[identifier] = plugin

        icon = QtGui.QIcon(plugin.icon)
        self.tabPanel.addTab(plugin, icon, name)

        # Connect standard plugin events.
        plugin.requestApplicationFocus.connect(
            self._onWidgetRequestApplicationFocus
        )
        plugin.requestApplicationClose.connect(
            self._onWidgetRequestApplicationClose
        )

    def removePlugin(self, identifier):
        '''Remove plugin registered with *identifier*.

        Raise :py:exc:`KeyError` if no plugin with *identifier* has been added.

        '''
        plugin = self.plugins.get(identifier)
        if plugin is None:
            raise KeyError(
                'No plugin registered with identifier "{0}".'.format(identifier)
            )

        index = self.tabPanel.indexOf(plugin)
        self.tabPanel.removeTab(index)

    def focus(self):
        '''Focus and bring the window to top.'''
        self.activateWindow()
        self.show()
        self.raise_()

    def showAbout(self):
        '''Display window with about information.'''
        self.focus()

        aboutDialog = _about.AboutDialog(self)

        environmentData = os.environ.copy()
        environmentData.update({
            'PLATFORM': platform.platform(),
            'PYTHON_VERSION': platform.python_version()
        })

        versionData = [{
            'name': 'ftrack connect',
            'version': ftrack_connect.__version__,
            'core': True,
            'debug_information': environmentData
        }]

        # Gather information about API versions and other
        # plugin hooks.

        try:
            event = ftrack_api.event.base.Event(
                topic = 'ftrack.connect.plugin.debug-information'
            )

            responses = self.session.event_hub.publish(
                event, synchronous=True
            )
            self.logger.info('debug-info {}'.format(responses))

            for response in responses:
                if isinstance(response, dict):
                    versionData.append(response)
                elif isinstance(response, list):
                    versionData = versionData + response

        except Exception as error:
            self.logger.error(
                error
            )

        aboutDialog.setInformation(
            versionData=versionData,
            server=os.environ.get('FTRACK_SERVER', 'Not set'),
            user=self.session.api_user,
            widget_plugins=self.plugins
        )

        aboutDialog.exec_()

    def openDefaultPluginDirectory(self):
        '''Open default plugin directory in platform default file browser.'''

        directory = self.defaultPluginDirectory

        if not os.path.exists(directory):
            # Create directory if not existing.
            try:
                os.makedirs(directory)
            except OSError:
                messageBox = QtWidgets.QMessageBox(parent=self)
                messageBox.setIcon(QtWidgets.QMessageBox.Warning)
                messageBox.setText(
                    u'Could not open or create default plugin '
                    u'directory: {0}.'.format(directory)
                )
                messageBox.exec_()
                return

        ftrack_connect.util.open_directory(directory)
