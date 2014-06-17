# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui
from PySide import QtCore


class BlockingIdleView(QtGui.QWidget):
    '''Idle view for ftrack connect Publisher.'''

    def __init__(self, parent=None, text=''):
        '''Initiate idle view.'''
        super(BlockingIdleView, self).__init__(parent)
        layout = QtGui.QVBoxLayout()

        self.idleText = text

        self.textLabel = QtGui.QLabel(text)
        layout.addWidget(
            self.textLabel, alignment=QtCore.Qt.AlignCenter
        )

        self.setLayout(layout)
