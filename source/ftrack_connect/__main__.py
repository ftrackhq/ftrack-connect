# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import argparse
import logging
import sys
import signal
import os

from PySide import QtGui

# Add hooks to topic plugin path before importing application.
mainPath = os.path.dirname(
    os.path.realpath(__file__)
)

hooksPath = os.path.abspath(
    os.path.join(
        mainPath, '..', '..', 'resource', 'hooks'
    )
)

os.environ.setdefault(
    'FTRACK_TOPIC_PLUGIN_PATH', hooksPath
)

import ftrack_connect.ui.application


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

    namespace = parser.parse_args(arguments)

    logging.basicConfig(level=loggingLevels[namespace.verbosity])

    application = QtGui.QApplication('ftrack-connect')
    application.setOrganizationName('ftrack')
    application.setOrganizationDomain('ftrack.com')
    application.setQuitOnLastWindowClosed(False)

    # Enable ctrl+c to quit application when started from command line.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    connectWindow = ftrack_connect.ui.application.MainWindow()

    return application.exec_()


if __name__ == '__main__':
    raise SystemExit(
        main(sys.argv[1:])
    )
