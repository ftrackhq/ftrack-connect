# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys

from PySide import QtGui

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
        arguments = sys.argv

    application = QtGui.QApplication(arguments)

    dialog = TestHarness()
    dialog.show()

    dialog.timer.start()

    sys.exit(application.exec_())


if __name__ == '__main__':
    raise SystemExit(main())
