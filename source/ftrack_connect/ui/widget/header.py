# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os
# import webbrowser

from PySide import QtCore, QtGui

import ftrack
from ftrack_connect.ui import resource
from thumbnail import User


class HeaderWidget(QtGui.QFrame):
    def __init__(self, parent=None):
        super(HeaderWidget, self).__init__(parent=parent)
        self.setObjectName('ftrack-header-widget')
        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(
            QtCore.Qt.AlignTop
        )
        self.setLayout(self.main_layout)

        # Logo & User ID
        self.id_container = QtGui.QWidget(self)
        self.id_container_layout = QtGui.QHBoxLayout()
        self.id_container_layout.setContentsMargins(0, 0, 0, 0)
        self.id_container_layout.setSpacing(0)
        self.id_container_layout.setAlignment(
            QtCore.Qt.AlignTop
        )
        self.id_container.setLayout(self.id_container_layout)

        spacer = QtGui.QSpacerItem(
            0,
            0,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum
        )

        self.logo = FtrackLogo(self)
        self.user_id = UserId(self)

        self.id_container_layout.addWidget(self.logo)
        self.id_container_layout.addItem(spacer)
        self.id_container_layout.addWidget(self.user_id)

        # Message
        self.message_container = QtGui.QWidget(self)
        self.message_container.hide()
        self.message_container_layout = QtGui.QHBoxLayout()
        self.message_container_layout.setContentsMargins(0, 0, 0, 0)
        self.message_container_layout.setSpacing(0)
        self.message_container.setLayout(self.message_container_layout)

        self.message_box = MessageBox(self)
        self.message_container_layout.addWidget(self.message_box)

        # Add (Logo & User ID) & Message
        self.main_layout.addWidget(self.id_container)
        self.main_layout.addWidget(self.message_container)

    def setMessage(self, message, level='info'):
        self.message_container.show()
        self.message_box.setMessage(message, level)

    def dismissMessage(self):
        self.message_container.hide()
        self.message_box.dismissMessage()


class FtrackLogo(QtGui.QLabel):
    def __init__(self, parent=None):
        super(FtrackLogo, self).__init__(parent=parent)
        self.setObjectName('ftrack-logo-widget')
        self.main_layout = QtGui.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            QtCore.Qt.AlignTop
        )
        self.setLayout(self.main_layout)

        logoPixmap = QtGui.QPixmap(':ftrack/image/default/ftrackLogoLabel')
        self.setPixmap(
            logoPixmap.scaled(
                self.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
        )


class UserId(QtGui.QWidget):
    def __init__(self, parent=None):
        super(UserId, self).__init__(parent=parent)
        self.setObjectName('ftrack-userid-widget')
        self.main_layout = QtGui.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(
            QtCore.Qt.AlignRight
        )
        self.setLayout(self.main_layout)

        self.label = QtGui.QLabel(self)
        self.image = User(self)
        self.image.setFixedSize(35, 35)

        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.image)

        logname = os.getenv('LOGNAME')
        self.image.load(logname)
        self.label.setText(ftrack.User(logname).getName().title())


class MessageBox(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MessageBox, self).__init__(parent=parent)
        self.setObjectName('ftrack-message-box')
        self.main_layout = QtGui.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            QtCore.Qt.AlignTop
        )
        self.setLayout(self.main_layout)

        self.label = QtGui.QLabel(parent=self)
        self.label.resize(QtCore.QSize(900, 80))

        self.label.setSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Fixed
        )
        self.label.hide()
        self.label.setObjectName('ftrack-header-message-info')

        self.main_layout.addWidget(self.label)

    def setMessage(self, message, level):
        message_types = ['info', 'warning', 'error']
        if level not in message_types:
            raise ValueError(
                'Message type should be one of: %s' % ', '.join(message_types)
            )

        class_type = 'ftrack-header-message-%s' % level

        self.label.setObjectName(class_type)

        self.setStyleSheet(self.styleSheet())
        self.label.setText(message)
        self.label.setVisible(True)

    def dismissMessage(self):
        self.label.setText('')
        self.label.setVisible(False)
