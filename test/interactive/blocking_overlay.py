# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore

import ftrack_connect.ui.widget.overlay
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        widget = QtGui.QFrame()
        widget.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain)
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
        for index in range(5):
            label = QtGui.QLineEdit('Label {0}'.format(index))

            if index == 3:
                label.setDisabled(True)
                label.setText(label.text() + ' (Disabled)')

            layout.addWidget(label)

        button = QtGui.QPushButton('Push Button')
        button.setObjectName('primary')
        layout.addWidget(button)

        widget.overlay = ftrack_connect.ui.widget.overlay.BlockingOverlay(
            widget
        )

        widget.setMinimumSize(400, 400)

        return widget

    def constructController(self, widget):
        '''Return controller for *widget*.'''
        controlWidget = QtGui.QWidget()
        controlLayout = QtGui.QVBoxLayout()
        controlWidget.setLayout(controlLayout)

        layout = QtGui.QHBoxLayout()
        controlLayout.addLayout(layout)

        showButton = QtGui.QPushButton('Show')
        layout.addWidget(showButton)

        hideButton = QtGui.QPushButton('Hide')
        layout.addWidget(hideButton)

        showButton.clicked.connect(widget.overlay.show)
        hideButton.clicked.connect(widget.overlay.hide)

        messageEdit = QtGui.QLineEdit()
        messageEdit.setPlaceholderText('Enter message to display')
        controlLayout.addWidget(messageEdit)

        messageEdit.textChanged.connect(
            widget.overlay.setMessage
        )

        return controlWidget


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
