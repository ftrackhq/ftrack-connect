# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os
import webbrowser

from PySide import QtCore, QtGui

import ftrack
from ftrack_connect.ui import resource
from thumbnail import User


class Ui_Header(object):

    def setupUi(self, Header):
        Header.setObjectName("Header")
        Header.resize(198, 35)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Header.sizePolicy().hasHeightForWidth())
        Header.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtGui.QHBoxLayout(Header)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setContentsMargins(9, 0, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.logoLabel = QtGui.QLabel(Header)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.logoLabel.sizePolicy().hasHeightForWidth()
        )
        self.logoLabel.setSizePolicy(sizePolicy)
        self.logoLabel.setText("")
        self.logoLabel.setTextFormat(QtCore.Qt.AutoText)
        self.logoLabel.setScaledContents(False)
        self.logoLabel.setObjectName("logoLabel")
        self.horizontalLayout.addWidget(self.logoLabel)


        spacerItem = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)
        self.userLabel = QtGui.QLabel(Header)
        self.userIcon = User()
        self.userIcon.setFixedSize(40, 40)
        self.horizontalLayout.addWidget(self.userLabel)
        self.horizontalLayout.addWidget(self.userIcon)


class SimpleHeaderWidget(QtGui.QWidget):

    def __init__(self, parent=None, task=None):
        QtGui.QWidget.__init__(self, parent)

        logname = os.getenv('LOGNAME')
        self.ui = Ui_Header()
        self.ui.setupUi(self)
        self.setFixedHeight(40)
        self.resize(198, 35)
        self.ui.userIcon.load(logname)
        self.ui.userLabel.setText(ftrack.User(logname).getName())

        logoPixmap = QtGui.QPixmap(':ftrack/image/default/ftrackLogoLabel')
        self.ui.logoLabel.setPixmap(
            logoPixmap.scaled(
                self.ui.logoLabel.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
        )

        self.setAutoFillBackground(True)

    def setTitle(self, title):
        self.ui.titleLabel.setText(title)

    def openHelp(self):
        webbrowser.open(self.helpUrl)

class HeaderWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(HeaderWidget, self).__init__(parent=parent)
        self.header = SimpleHeaderWidget()
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.header)
        self.__create_message_area()

        self.resize(198, 35)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)

    def __create_message_area(self):
        self.message_area = QtGui.QLabel('', parent=self)
        self.message_area.resize(QtCore.QSize(900, 80))
        self.message_area.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed
        )
        self.message_area.setVisible(False)
        self.message_area.setObjectName('ftrack-header-message-info')
        self.layout.addWidget(self.message_area)

    def setMessage(self, message, type='info'):

        message_types = ['info', 'warning', 'error']
        if type not in message_types:
            raise ValueError('Message type should be one of: %' ', '.join(message_types))

        class_type = 'ftrack-header-message-%s' % type

        self.message_area.setObjectName(class_type)
        # for dynamic changes on property, the style has to be reapplied every time...
        # http://www.qtcentre.org/threads/32140-Change-Stylesheet-Using-Dynamic-Property

        self.setStyleSheet(self.styleSheet())
        self.message_area.setText(message)
        self.message_area.setVisible(True)

    def dismissMessage(self):
        self.message_area.setText('')
        self.message_area.setVisible(False)

    def getCurrentUser(self):
        return self.header.current_user

    def setTitle(self, title):
        pass
