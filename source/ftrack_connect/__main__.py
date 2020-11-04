# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import appdirs
import argparse
import logging
import sys
import signal
import os
import pkg_resources

bindings = ['PySide2']
os.environ.setdefault('QT_PREFERRED_BINDING', os.pathsep.join(bindings))

from Qt import QtWidgets, QtCore

import ftrack_connect.config
import ftrack_connect.singleton

# Hooks use the ftrack event system. Set the FTRACK_EVENT_PLUGIN_PATH
# to pick up the default hooks if it has not already been set.
try:
    os.environ.setdefault(
        'FTRACK_EVENT_PLUGIN_PATH',
        pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('ftrack-connect'),
            'ftrack_connect_resource/hook'
        )
    )
except pkg_resources.DistributionNotFound:
    # If part of a frozen package then distribution might not be found.
    pass


import ftrack_connect.ui.application
import ftrack_connect.ui.theme


def main(arguments=None):
    '''ftrack connect.'''

    parser = argparse.ArgumentParser(prog='ftrack-connect')

    # Allow setting of logging level from arguments.
    loggingLevels = {}
    for level in (
        logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING,
        logging.ERROR, logging.CRITICAL
    ):
        loggingLevels[logging.getLevelName(level).lower()] = level

    parser.add_argument(
        '-v', '--verbosity',
        help='Set the logging output verbosity.',
        choices=loggingLevels.keys(),
        default='warning'
    )

    parser.add_argument(
        '-t', '--theme',
        help='Set the theme to use.',
        choices=['light', 'dark'],
        default='light'
    )

    parser.add_argument(
        '-s', '--silent',
        help='Set the initial visibility of the connect window.',
        action='store_true'
    )

    parser.add_argument(
        '-a', '--allow-multiple',
        help='Skip lockfile to allow new instance of connect.',
        action='store_true'
    )

    namespace = parser.parse_args(arguments)

    ftrack_connect.config.configure_logging(
        'ftrack_connect', level=loggingLevels[namespace.verbosity]
    )

    if not namespace.allow_multiple:
        lockfile = os.path.join(
            appdirs.user_data_dir(
                'ftrack-connect', 'ftrack'
            ),
            'lock'
        )
        logger = logging.getLogger('ftrack_connect')
        try:
            si = ftrack_connect.singleton.SingleInstance('', lockfile)
        except ftrack_connect.singleton.SingleInstanceException:
            logger.error(
                'Lockfile found: {}\nIs Connect already running?\nClose Connect,'
                ' remove lockfile or pass --allow-multiple and retry.'.format(
                    lockfile
                )
            )
            raise SystemExit(1)

    # If under X11, make Xlib calls thread-safe.
    # http://stackoverflow.com/questions/31952711/threading-pyqt-crashes-with-unknown-request-in-queue-while-dequeuing
    if os.name == 'posix':
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)

    # Ensure support for highdpi
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    # Construct global application.

    application = QtWidgets.QApplication([])

    application.setOrganizationName('ftrack')
    application.setOrganizationDomain('ftrack.com')
    application.setQuitOnLastWindowClosed(False)

    # Enable ctrl+c to quit application when started from command line.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Construct main connect window and apply theme.
    connectWindow = ftrack_connect.ui.application.Application(
        theme=namespace.theme
    )

    if namespace.silent:
        connectWindow.hide()

    # Fix for Windows where font size is incorrect for some widgets. For some
    # reason, resetting the font here solves the sizing issue.
    font = application.font()
    application.setFont(font)

    return application.exec_()


if __name__ == '__main__':
    raise SystemExit(
        main()
    )
