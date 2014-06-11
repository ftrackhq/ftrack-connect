# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

from PySide import QtGui

from ftrack_connect.tabwidget import TabWidget

APPLICATION_ROOT = os.path.dirname(
    os.path.realpath(__file__)
)

# RESOURCEPATH environment variable is set by py2app/py2exe applications.
RESOURCE_ROOT_PATH = os.path.join(
    os.environ.get(
        'RESOURCEPATH',
        APPLICATION_ROOT
    ), 'resources'
)


class ConnectError(Exception):
    '''Base ftrack connect error.'''
    pass


class ApplicationWindow(QtGui.QMainWindow):
    '''Main window class for ftrack connect.'''

    def __init__(self, *args, **kwargs):
        super(ApplicationWindow, self).__init__(*args, **kwargs)

        if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            raise ConnectError('No system tray located.')

        QtGui.QApplication.setQuitOnLastWindowClosed(False)

        self.logoIcon = QtGui.QIcon(
            '{0}/logo.png'.format(RESOURCE_ROOT_PATH)
        )
        self._setupStyle()

        self._initialiseTray()

        self.setObjectName('app-window')
        self.setWindowTitle('ftrack connect')
        self.resize(350, 500)
        self.move(50, 50)

        self.setWindowIcon(self.logoIcon)

        self.tabPanel = TabWidget()
        self.setCentralWidget(self.tabPanel)

        self._discoverPlugins()

        self.focus()

    def _initialiseTray(self):
        '''Initialise and add application icon to system tray.'''
        self.trayMenu = self._createTrayMenu()

        self.tray = QtGui.QSystemTrayIcon(self)

        self.tray.setContextMenu(
            self.trayMenu
        )

        self.tray.setIcon(self.logoIcon)
        self.tray.show()

    def _createTrayMenu(self):
        '''Return a menu for system tray.'''
        menu = QtGui.QMenu(self)

        quitAction = QtGui.QAction(
            'Quit connect', self,
            triggered=QtGui.qApp.quit
        )

        focusAction = QtGui.QAction(
            'Open connect', self,
            triggered=self.focus
        )

        styleAction = QtGui.QAction(
            'Change theme', self,
            triggered=self._changeTheme
        )
        menu.addAction(styleAction)

        menu.addAction(focusAction)
        menu.addSeparator()
        menu.addAction(quitAction)

        return menu

    def _discoverPlugins(self):
        '''Find and load tab plugins in search paths.'''
        #: TODO: Add discover functionality and search paths.

        # Add publisher as a plugin.
        from ftrack_connect.publisher.core import register
        register(self)

    def _changeTheme(self):
        '''Change active application theme.'''
        if not hasattr(self, '_theme'):
            self._theme = 'light'

        if self._theme == 'dark':
            self._theme = 'light'
        else:
            self._theme = 'dark'

        self._setupStyle(self._theme)

    def _setupStyle(self, theme='light'):
        '''Set up application style using *theme*.'''
        QtGui.QApplication.setStyle('cleanlooks')

        # Load font
        QtGui.QFontDatabase.addApplicationFont(
            '{0}/fonts/OpenSans-Regular.ttf'.format(RESOURCE_ROOT_PATH)
        )

        # Load stylesheet
        styleSheetString = open(
            '{0}/style-{1}.css'.format(RESOURCE_ROOT_PATH, theme), 'r'
        ).read()
        self.setStyleSheet(styleSheetString)

    def add(self, widget, name=None):
        '''Add *widget* as tab with *name*.

        If *name* is None the name will be collected from the widget.

        '''
        if name is None:
            name = widget.getName()

        self.tabPanel.addTab(
            widget, name
        )

    def focus(self):
        '''Focus and bring the window to top.'''
        self.activateWindow()
        self.show()
        self.raise_()
