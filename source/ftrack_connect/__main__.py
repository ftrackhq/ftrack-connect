# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import argparse
import logging
import sys

from PySide import QtGui, QtCore

from ftrack_connect.publisher import Publisher


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

    application = QtGui.QApplication('ftrack-connect-publisher')
    publisher = Publisher()

    publisher.resize(600, 800)
    publisher.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    publisher.show()

    return application.exec_()


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
