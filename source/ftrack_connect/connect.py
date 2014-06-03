# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import sys

from PySide import QtGui

from tabwidget import TabWidget

APPLICATION_ROOT = os.path.dirname(
    os.path.realpath(__file__)
)


class ApplicationWindow(QtGui.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(ApplicationWindow, self).__init__(*args, **kwargs)

        if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            QtGui.QMessageBox.critical(
                None, 'Systray',
                'I couldnt detect any system tray on this system.'
            )
            sys.exit(1)

        QtGui.QApplication.setQuitOnLastWindowClosed(False)

        self.logoIcon = QtGui.QIcon(
            '{0}/resources/images/logo.png'.format(APPLICATION_ROOT)
        )

        self._initTray()

        self.setWindowTitle('ftrack connect')
        self.resize(300, 500)
        self.move(50, 50)

        self.setWindowIcon(self.logoIcon)

        self.tabPanel = TabWidget()
        self.setCentralWidget(self.tabPanel)

    def _initTray(self):
        self.trayMenu = self._initTrayMenu()

        self.tray = QtGui.QSystemTrayIcon(self)

        self.tray.setContextMenu(
            self.trayMenu
        )

        self.tray.setIcon(self.logoIcon)
        self.tray.show()

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
