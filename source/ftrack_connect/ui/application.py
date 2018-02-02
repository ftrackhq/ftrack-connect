# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import sys
import getpass
import platform
import requests
import requests.exceptions
import uuid
import logging

import appdirs

from QtExt import QtCore, QtWidgets, QtGui

import ftrack_api
import ftrack_api._centralized_storage_scenario
import ftrack_api.event.base

import ftrack_connect
import ftrack_connect.session
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


class ApplicationPlugin(QtWidgets.QWidget):
    '''Base widget for ftrack connect application plugin.'''

    #: Signal to emit to request focus of this plugin in application.
    requestApplicationFocus = QtCore.Signal(object)

    #: Signal to emit to request closing application.
    requestApplicationClose = QtCore.Signal(object)

    def getName(self):
        '''Return name of widget.'''
        return self.__class__.__name__

    def getIdentifier(self):
        '''Return identifier for widget.'''
        return self.getName().lower().replace(' ', '.')


class Application(QtWidgets.QMainWindow):
    '''Main application window for ftrack connect.'''

    #: Signal when login fails.
    loginError = QtCore.Signal(object)

    #: Signal when event received via ftrack's event hub.
    eventHubSignal = QtCore.Signal(object)

    # Login signal.
    loginSignal = QtCore.Signal(object, object, object)

    def __init__(self, *args, **kwargs):
        '''Initialise the main application window.'''
        theme = kwargs.pop('theme', 'light')
        super(Application, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self.defaultPluginDirectory = appdirs.user_data_dir(
            'ftrack-connect-plugins', 'ftrack'
        )

        self.pluginHookPaths = set()
        self.pluginHookPaths.update(
            self._gatherPluginHooks(
                self.defaultPluginDirectory
            )
        )
        if 'FTRACK_CONNECT_PLUGIN_PATH' in os.environ:
            for connectPluginPath in (
                os.environ['FTRACK_CONNECT_PLUGIN_PATH'].split(os.pathsep)
            ):
                self.pluginHookPaths.update(
                    self._gatherPluginHooks(
                        connectPluginPath
                    )
                )

        self.logger.info(
            u'Connect plugin hooks directories: {0}'.format(
                ', '.join(self.pluginHookPaths)
            )
        )

        # Register widget for error handling.
        self.uncaughtError = _uncaught_error.UncaughtError(
            parent=self
        )

        if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            raise ftrack_connect.error.ConnectError(
                'No system tray located.'
            )

        self.logoIcon = QtGui.QIcon(
            QtGui.QPixmap(':/ftrack/image/default/ftrackLogoColor')
        )

        self._login_server_thread = None

        self._theme = None
        self.setTheme(theme)

        self.plugins = {}

        self._initialiseTray()

        self.setObjectName('ftrack-connect-window')
        self.setWindowTitle('ftrack connect')
        self.resize(450, 700)
        self.move(50, 50)

        self.setWindowIcon(self.logoIcon)

        self._login_overlay = None
        self.loginWidget = _login.Login()
        self.loginSignal.connect(self.loginWithCredentials)
        self.login()

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

        QtWidgets.qApp.quit()

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

    def _setup_session(self):
        '''Setup a new python API session.'''
        if hasattr(self, '_hub_thread'):
            self._hub_thread.quit()

        plugin_paths = os.environ.get(
            'FTRACK_EVENT_PLUGIN_PATH', ''
        ).split(os.pathsep)

        plugin_paths.extend(self.pluginHookPaths)

        try:
            session = ftrack_connect.session.get_shared_session(
                plugin_paths=plugin_paths
            )
        except Exception as error:
            raise ftrack_connect.error.ParseError(error)

        # Listen to events using the new API event hub. This is required to
        # allow reconfiguring the storage scenario.
        self._hub_thread = _event_hub_thread.NewApiEventHubThread()
        self._hub_thread.start(session)

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
                allow_redirects=False  # Old python API will not work with redirect.
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

        # Set environment variables supported by the old API.
        os.environ['FTRACK_SERVER'] = url
        os.environ['LOGNAME'] = username
        os.environ['FTRACK_APIKEY'] = apiKey

        # Set environment variables supported by the new API.
        os.environ['FTRACK_API_USER'] = username
        os.environ['FTRACK_API_KEY'] = apiKey

        # Login using the new ftrack API.
        try:
            self._session = self._setup_session()
        except Exception as error:
            self.logger.exception(u'Error during login.:')
            self._report_session_setup_error(error)
            return

        # Store credentials since login was successful.
        self._save_credentials(url, username, apiKey)

        # Verify storage scenario before starting.
        if 'storage_scenario' in self._session.server_information:
            storage_scenario = self._session.server_information.get(
                'storage_scenario'
            )
            if storage_scenario is None:
                # Hide login overlay at this time since it will be deleted
                self.logger.debug('Storage scenario is not configured.')
                scenario_widget = _scenario_widget.ConfigureScenario(
                    self._session
                )
                scenario_widget.configuration_completed.connect(
                    self.location_configuration_finished
                )
                self.setCentralWidget(scenario_widget)
                self.focus()
                return

        self.location_configuration_finished(reconfigure_session=False)

    def location_configuration_finished(self, reconfigure_session=True):
        '''Continue connect setup after location configuration is done.'''
        if reconfigure_session:
            ftrack_connect.session.destroy_shared_session()
            self._session = self._setup_session()

        try:
            self.configureConnectAndDiscoverPlugins()
        except Exception as error:
            self.logger.exception(u'Error during location configuration.:')
            self._report_session_setup_error(error)
        else:
            self.focus()

        # Send verify startup event to verify that storage scenario is
        # working correctly.
        event = ftrack_api.event.base.Event(
            topic='ftrack.connect.verify-startup',
            data={
                'storage_scenario': self._session.server_information.get(
                    'storage_scenario'
                )
            }
        )
        results = self._session.event_hub.publish(event, synchronous=True)
        problems = [
            problem for problem in results if isinstance(problem, basestring)
        ]
        if problems:
            msgBox = QtWidgets.QMessageBox(parent=self)
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
            msgBox.setText('\n\n'.join(problems))
            msgBox.exec_()

    def configureConnectAndDiscoverPlugins(self):
        '''Configure connect and load plugins.'''

        # Local import to avoid connection errors.
        import ftrack
        ftrack.EVENT_HANDLERS.paths.extend(self.pluginHookPaths)
        ftrack.LOCATION_PLUGINS.paths.extend(self.pluginHookPaths)

        ftrack.setup()
        self.tabPanel = _tab_widget.TabWidget()
        self.tabPanel.tabBar().setObjectName('application-tab-bar')
        self.setCentralWidget(self.tabPanel)

        self._discoverTabPlugins()

        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.connect and source.user.username={0}'.format(
                getpass.getuser()
            ),
            self._relayEventHubEvent
        )
        self.eventHubSignal.connect(self._onConnectTopicEvent)

        self.eventHubThread = _event_hub_thread.EventHubThread()
        self.eventHubThread.start()

        self.focus()

        # Listen to discover connect event and respond to let the sender know
        # that connect is running.
        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.connect.discover and source.user.username={0}'.format(
                getpass.getuser()
            ),
            lambda event : True
        )

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
        self.tray.show()

    def _createTrayMenu(self):
        '''Return a menu for system tray.'''
        menu = QtWidgets.QMenu(self)

        logoutAction = QtWidgets.QAction(
            'Log Out && Quit', self,
            triggered=self.logout
        )

        quitAction = QtWidgets.QAction(
            'Quit', self,
            triggered=QtWidgets.qApp.quit
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

    def _discoverTabPlugins(self):
        '''Find and load tab plugins in search paths.'''
        #: TODO: Add discover functionality and search paths.

        from . import (publisher, actions)
        actions.register(self)
        publisher.register(self)

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

        if identifier in self.plugins:
            raise _NotUniqueError(
                'Cannot add plugin. An existing plugin has already been '
                'registered with identifier {0}.'.format(identifier)
            )

        self.plugins[identifier] = plugin
        self.tabPanel.addTab(plugin, name)

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

        plugin.deleteLater()
        del self.plugins[identifier]

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

        import ftrack

        environmentData['FTRACK_API_VERSION'] = ftrack_api.__version__
        environmentData['FTRACK_API_LEGACY_VERSION'] = ftrack.api.version_data.ftrackVersion

        api_versions = (
            (
                ftrack.EVENT_HUB.publish,
                ftrack.Event(
                    'ftrack.connect.plugin.debug-information'
                )
            ),
            (
                self._session.event_hub.publish,
                ftrack_api.event.base.Event(
                    topic = 'ftrack.connect.plugin.debug-information'
                )
            )
        )

        for publish_fn, event in api_versions:
            # For each api version.
            try:
                responses = publish_fn(
                    event, synchronous=True
                )

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
            user=getpass.getuser(),
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
