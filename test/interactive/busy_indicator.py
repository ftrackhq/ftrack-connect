# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui

import ftrack_connect.ui.widget.indicator
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        indicator = ftrack_connect.ui.widget.indicator.BusyIndicator()
        indicator.setMinimumSize(100, 100)

        return indicator

    def constructController(self, widget):
        '''Return controller for *widget*.'''
        controlWidget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        controlWidget.setLayout(layout)

        startButton = QtGui.QPushButton('Start')
        layout.addWidget(startButton)

        stopButton = QtGui.QPushButton('Stop')
        layout.addWidget(stopButton)

        startButton.clicked.connect(widget.start)
        stopButton.clicked.connect(widget.stop)

        return controlWidget


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
