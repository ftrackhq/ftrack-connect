# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore

import ftrack_connect.ui.widget.indicator
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        widget = QtGui.QFrame()
        widget.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain)
        widget.setStyleSheet('QFrame { background-color: #efefef; }')
        widget.setLayout(QtGui.QVBoxLayout())

        self._indicator = ftrack_connect.ui.widget.indicator.BusyIndicator()
        self._indicator.setMinimumSize(100, 100)

        widget.layout().addWidget(self._indicator)
        return widget


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
