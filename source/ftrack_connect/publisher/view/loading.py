# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui
from PySide import QtCore


class LoadingView(QtGui.QWidget):
    '''Loading and progress view for ftrack connect Publisher.'''
    loadingDone = QtCore.Signal()

    def __init__(self, parent=None, loadingText='Crunching', doneText='Done!'):
        '''Initiate loading view.'''
        super(LoadingView, self).__init__(parent)

        self.loadingText = loadingText
        self.doneText = doneText

        loadingLayout = QtGui.QVBoxLayout()

        self.textLabel = QtGui.QLabel(self.loadingText)
        loadingLayout.addWidget(
            self.textLabel,
            alignment=QtCore.Qt.AlignCenter
        )

        self.doneButton = QtGui.QPushButton(text='Close')
        self.doneButton.setDisabled(True)

        self.doneButton.clicked.connect(self.loadingDone.emit)

        loadingLayout.addWidget(
            self.doneButton,
            alignment=QtCore.Qt.AlignCenter
        )

        self.setLayout(loadingLayout)

    def setDoneState(self):
        '''Set view in done state.'''
        self.textLabel.setText(
            self.doneText
        )
        self.doneButton.setEnabled(True)

    def setLoadingState(self):
        '''Set view in loading state.'''
        self.textLabel.setText(
            self.loadingText
        )
        self.doneButton.setDisabled(True)
