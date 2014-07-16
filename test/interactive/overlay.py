# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui

import ftrack_connect.ui.widget.overlay
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        widget = QtGui.QFrame()
        widget.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain)
        widget.setStyleSheet("QFrame { background-color: blue; }")

        self._overlay = ftrack_connect.ui.widget.overlay.Overlay(widget)
        self._overlay.setMessage('The background should be a pinkish colour!')
        self._overlay.setStyleSheet('''
            QWidget#overlay {
                background-color: red;
                color: white;
                font-size: 16pt;
            }
        ''')

        widget.setMinimumSize(400, 400)
        return widget


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
