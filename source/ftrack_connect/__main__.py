# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import argparse
import logging
import sys
import signal
import os
import pkg_resources

from PySide import QtGui

from ftrack_connect.config import configure_logging


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
    if arguments is None:
        arguments = []

    parser = argparse.ArgumentParser()

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
        default='info'
    )

    parser.add_argument(
        '-t', '--theme',
        help='Set the theme to use.',
        choices=['light', 'dark'],
        default='light'
    )

    namespace = parser.parse_args(arguments)

    configure_logging('connect', level=loggingLevels[namespace.verbosity])

    # Construct global application.
    application = QtGui.QApplication('ftrack-connect')
    application.setOrganizationName('ftrack')
    application.setOrganizationDomain('ftrack.com')
    application.setQuitOnLastWindowClosed(False)

    # Enable ctrl+c to quit application when started from command line.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Construct main connect window and apply theme.
    connectWindow = ftrack_connect.ui.application.Application(
        theme=namespace.theme
    )

    # Fix for Windows where font size is incorrect for some widgets. For some
    # reason, resetting the font here solves the sizing issue.
    font = application.font()
    application.setFont(font)

    return application.exec_()


if __name__ == '__main__':
    raise SystemExit(
        main(sys.argv[1:])
    )
