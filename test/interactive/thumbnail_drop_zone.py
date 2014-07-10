# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys
import signal

from PySide import QtGui

import ftrack_connect.ui.widget.thumbnail_drop_zone

# Enable ctrl+c to quit application when started from command line.
signal.signal(signal.SIGINT, signal.SIG_DFL)


def main(arguments=None):
    '''Interactive test of thumbnail drop zone.'''

    application = QtGui.QApplication(arguments)

    dialog = ftrack_connect.ui.widget.thumbnail_drop_zone.ThumbnailDropZone()
    dialog.show()
    dialog.resize(600, 400)
    dialog.move(200, 200)
    sys.exit(application.exec_())


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
