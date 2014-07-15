# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys

from PySide import QtGui

import ftrack_connect.ui.widget.components_list


def main(arguments=None):
    '''Interactive test of components list.'''
    if arguments is None:
        arguments = sys.argv

    application = QtGui.QApplication(arguments)

    dialog = ftrack_connect.ui.widget.components_list.ComponentsList()
    dialog.resize(800, 400)
    dialog.show()
    dialog.addItem({
        'resourceIdentifier': '/path/to/file.png'
    })
    dialog.addItem({
        'resourceIdentifier': '/path/to/sequence.%04d.png [1-20]'
    })

    sys.exit(application.exec_())


if __name__ == '__main__':
    raise SystemExit(main())

