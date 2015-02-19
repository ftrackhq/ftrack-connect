import os
from PySide import QtCore, QtGui
# import HeaderResources_rc

class Ui_Header(object):
    def setupUi(self, Header):
        Header.setObjectName("Header")
        Header.resize(198, 35)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Header.sizePolicy().hasHeightForWidth())
        Header.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtGui.QHBoxLayout(Header)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setContentsMargins(9, 0, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.logoLabel = QtGui.QLabel(Header)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logoLabel.sizePolicy().hasHeightForWidth())
        self.logoLabel.setSizePolicy(sizePolicy)
        self.logoLabel.setMinimumSize(QtCore.QSize(21, 22))
        self.logoLabel.setMaximumSize(QtCore.QSize(21, 22))
        self.logoLabel.setText("")
        self.logoLabel.setTextFormat(QtCore.Qt.AutoText)
        self.logoLabel.setPixmap(QtGui.QPixmap(":/fbox.png"))
        self.logoLabel.setScaledContents(False)
        self.logoLabel.setObjectName("logoLabel")
        self.horizontalLayout.addWidget(self.logoLabel)
        self.titleLabel = QtGui.QLabel(Header)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.titleLabel.setFont(font)
        self.titleLabel.setObjectName("titleLabel")
        self.horizontalLayout.addWidget(self.titleLabel)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.helpButton = QtGui.QPushButton(Header)
        self.helpButton.setMinimumSize(QtCore.QSize(35, 35))
        self.helpButton.setMaximumSize(QtCore.QSize(35, 35))
        self.helpButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/help.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.helpButton.setIcon(icon)
        self.helpButton.setIconSize(QtCore.QSize(30, 30))
        self.helpButton.setFlat(True)
        self.helpButton.setObjectName("helpButton")
        self.horizontalLayout.addWidget(self.helpButton)

        self.retranslateUi(Header)
        QtCore.QObject.connect(self.helpButton, QtCore.SIGNAL("clicked()"), Header.openHelp)
        QtCore.QMetaObject.connectSlotsByName(Header)

    def retranslateUi(self, Header):
        Header.setWindowTitle(QtGui.QApplication.translate("Header", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.titleLabel.setText(QtGui.QApplication.translate("Header", "Title", None, QtGui.QApplication.UnicodeUTF8))


class HeaderWidget(QtGui.QWidget):
    def __init__(self, parent, task=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Header()
        self.ui.setupUi(self)
        #self.setMaximumHeight(40)
        self.setFixedHeight(40)
        self.helpUrl = 'http://support.ftrack.com/'

        if 'FTRACK_HEADER_LOGO' in os.environ and os.environ['FTRACK_HEADER_LOGO'] != '':
            logoPixmap = QtGui.QPixmap(os.environ['FTRACK_HEADER_LOGO'])
            self.ui.logoLabel.setPixmap(logoPixmap.scaled(self.ui.logoLabel.size(), QtCore.Qt.KeepAspectRatio))

        p = self.palette()
        currentColor = p.color(QtGui.QPalette.Window)
        p.setBrush(QtGui.QPalette.Window, QtGui.QBrush(currentColor.darker(200)))
        self.setPalette(p)
        self.setAutoFillBackground(True)

    def setTitle(self, title):
        self.ui.titleLabel.setText(title)
        
    def openHelp(self):
        import webbrowser
        webbrowser.open(self.helpUrl)
        
    def setHelpUrl(self, url):
        self.helpUrl = url
