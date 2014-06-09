# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui
from PySide import QtCore


class LoadingView(QtGui.QWidget):

    loadingDone = QtCore.Signal()

    loadingText = 'Crunching..'
    doneText = 'All done!'

    def __init__(self, parent=None):
        super(LoadingView, self).__init__(parent)
        loadingLayout = QtGui.QVBoxLayout()

        self.textLabel = QtGui.QLabel('Crunching..')
        loadingLayout.addWidget(
            self.textLabel
        )

        self.doneButton = QtGui.QPushButton(text='Close')
        self.doneButton.setDisabled(True)

        self.doneButton.clicked.connect(self.loadingDone.emit)

        loadingLayout.addWidget(self.doneButton)

        self.setLayout(loadingLayout)

    def setDoneMode(self):
        self.textLabel.setText(
            self.doneText
        )
        self.doneButton.setEnabled(True)

    def setLoadingMode(self):
        self.textLabel.setText(
            self.loadingText
        )
        self.doneButton.setDisabled(True)
