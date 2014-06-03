# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

from PySide import QtGui

APPLICATION_ROOT = os.path.dirname(
    os.path.realpath(__file__)
)


class ApplicationWindow(QtGui.QWidget):

    def __init__(self, *args, **kwargs):
        super(ApplicationWindow, self).__init__(*args, **kwargs)

        if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            QtGui.QMessageBox.critical(
                None, 'Systray',
                'I couldnt detect any system tray on this system.'
            )
            sys.exit(1)

        QtGui.QApplication.setQuitOnLastWindowClosed(False)

        self._initTray()

    def _initTray(self):
        self.trayMenu = self._initTrayMenu()

        self.tray = QtGui.QSystemTrayIcon(self)

        self.tray.setContextMenu(
            self.trayMenu
        )

        logoIcon = QtGui.QIcon(
            '{0}/resources/images/logo.png'.format(APPLICATION_ROOT)
        )

        self.tray.setIcon(logoIcon)
        self.tray.show()

        self.resize(300, 500)
        self.move(50, 50)

    def _initTrayMenu(self):

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
        self.activateWindow()
        self.show()
        self.raise_()
