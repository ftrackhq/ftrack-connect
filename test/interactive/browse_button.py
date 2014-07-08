# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys
import signal
import logging

from PySide import QtGui

import ftrack_connect.ui.widget.browse_button

# Enable ctrl+c to quit application when started from command line.
signal.signal(signal.SIGINT, signal.SIG_DFL)


def main(arguments=None):
    '''Interactive test of components list.'''
    if arguments is None:
        arguments = sys.argv

    logging.basicConfig(level=logging.DEBUG)

    application = QtGui.QApplication(arguments)

    browse = ftrack_connect.ui.widget.browse_button.BrowseButton()
    browse.show()
    browse.move(500, 750)

    browse.fileSelected.connect(logging.debug)
    sys.exit(application.exec_())


if __name__ == '__main__':
    raise SystemExit(main())
