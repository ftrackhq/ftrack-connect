# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import sys

from PySide import QtGui

import ftrack_connect.widget.components_list


def main(arguments=None):
    '''Interactive test of components list.'''
    if arguments is None:
        arguments = sys.argv

    application = QtGui.QApplication(arguments)

    dialog = ftrack_connect.widget.components_list.ComponentsList()
    dialog.resize(800, 400)
    dialog.show()

    sys.exit(application.exec_())


if __name__ == '__main__':
    raise SystemExit(main())

