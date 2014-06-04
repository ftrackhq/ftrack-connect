# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

from PySide import QtGui

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

        self._initialiseTray()

        self.setWindowTitle('ftrack connect')
        self.resize(300, 500)
        self.move(50, 50)

        self.setWindowIcon(self.logoIcon)

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

        menu.addAction(focusAction)
        menu.addSeparator()
        menu.addAction(quitAction)

        return menu

    def focus(self):
        '''Focus and bring the window to top.'''
        self.activateWindow()
        self.show()
        self.raise_()
