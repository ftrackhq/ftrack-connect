# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys
import logging
import argparse
import signal

from PySide import QtGui

import ftrack_connect.ui.theme


# Enable ctrl+c to quit test when started from command line.
signal.signal(signal.SIGINT, signal.SIG_DFL)


class HarnessGui(QtGui.QDialog):
    '''Harness gui for widget.'''

    def __init__(self, widget, controller=None, parent=None):
        '''Initialise harness with *widget* and optional *controller*.'''
        super(HarnessGui, self).__init__(parent=parent)
        self.setLayout(QtGui.QVBoxLayout())

        self.widget = widget
        self.layout().addWidget(self.widget, stretch=1)

        self.controller = controller
        if self.controller:
            self.controlGroup = QtGui.QFrame()
            self.controlGroup.setObjectName('HarnessGuiController')
            self.layout().addWidget(self.controlGroup, stretch=0)

            controlGroupLayout = QtGui.QVBoxLayout()
            controlGroupLayout.setContentsMargins(0, 0, 0, 0)
            self.controlGroup.setLayout(controlGroupLayout)

            controlGroupLayout.addWidget(self.controller, stretch=0)

            self.controlGroup.setSizePolicy(
                QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum
            )

        self.layout().setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)


class Harness(object):
    '''Test harness.

    Subclass this and implement constructWidget. Then call run.

    '''

    def constructWidget(self):
        '''Return widget instance to test.'''
        raise NotImplementedError()

    def constructController(self, widget):
        '''Return widget that provides controls for manipulating the test.

        *widget* is the widget returned from :py:meth:`constructWidget`.

        '''
        return None

    def run(self, arguments=None):
        '''Run harness.'''
        if arguments is None:
            arguments = sys.argv[1:]

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
        widget = self.constructWidget()
        controller = self.constructController(widget)
        harnessGui = HarnessGui(widget, controller)
        ftrack_connect.ui.theme.applyTheme(harnessGui, namespace.theme)

        harnessGui.show()

        # Fix for Windows where font size is incorrect for some widgets. For
        # some reason, resetting the font here solves the sizing issue.
        font = application.font()
        application.setFont(font)

        return application.exec_()
