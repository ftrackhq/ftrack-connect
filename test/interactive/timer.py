# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys
import argparse
import logging

from PySide import QtGui

import ftrack_connect.ui.theme
import ftrack_connect.ui.widget.timer


class TestHarness(QtGui.QDialog):
    '''Test harness for widget.'''

    def __init__(self, parent=None):
        '''Initialise harness.'''
        super(TestHarness, self).__init__(parent=parent)
        self.setLayout(QtGui.QVBoxLayout())

        self.timer = ftrack_connect.ui.widget.timer.Timer(
            title='Compositing',
            description=('drones / sequence / a very very / long path / that '
                         'should be / elided / is-cu / station')
        )
        self.layout().addWidget(self.timer)
        self.layout().setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)


def main(arguments=None):
    '''Interactive test of timer widget.'''
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

    logging.basicConfig(level=loggingLevels[namespace.verbosity])

    # Construct global application.
    application = QtGui.QApplication(arguments)

    # Construct test harness and apply theme.
    dialog = TestHarness()
    ftrack_connect.ui.theme.applyTheme(dialog, namespace.theme)

    dialog.show()

    return application.exec_()


if __name__ == '__main__':
    raise SystemExit(
        main(sys.argv[1:])
    )
