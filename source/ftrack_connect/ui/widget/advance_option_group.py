from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui


class AdvanceOptionGroup(QtWidgets.QGroupBox):

    def collapse(self, status):
        self.content.setVisible(status)

    def __init__(self, parent=None):
        super(AdvanceOptionGroup, self).__init__(parent=parent)
        self.setTitle('Advanced options')
        self.setCheckable(True)
        self.setFlat(True)
        self.setChecked(False)
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        self.content = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content.setLayout(self.content_layout)
        main_layout.addWidget(self.content)
        self.clicked.connect(self.collapse)
        self.clicked.emit()

    def addWidget(self, widget):
        self.content_layout.addWidget(widget)



