# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from Qt import QtCore, QtWidgets, QtGui

from ftrack_connect.ui.widget import thumbnail

# Cache of user names.
NAME_CACHE = dict()


class Header(QtWidgets.QFrame):
    '''Header widget with name and thumbnail.'''

    def __init__(self, session, parent=None):
        '''Instantiate the header widget for a user with *username*.'''

        super(Header, self).__init__(parent=parent)
        self.session = session
        self.setObjectName('ftrack-header-widget')

        self.pre_build()
        self.build()

    def pre_build(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        # self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.main_layout)

    def build(self):
        # Logo & User ID
        self.id_container = QtWidgets.QWidget(self)
        self.id_container_layout = QtWidgets.QHBoxLayout()
        self.id_container_layout.setContentsMargins(0, 0, 0, 0)
        # self.id_container_layout.setSpacing(0)
        self.id_container_layout.setAlignment(QtCore.Qt.AlignTop)
        self.id_container.setLayout(self.id_container_layout)

        spacer = QtWidgets.QSpacerItem(
            0,
            0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum,
        )

        self.logo = Logo(self)
        self.user = User(self.session, self)

        self.id_container_layout.addWidget(self.logo)
        # self.id_container_layout.addItem(spacer)
        self.id_container_layout.addWidget(self.user)

        # Add (Logo & User ID) & Message
        self.main_layout.addWidget(self.id_container)


class Logo(QtWidgets.QLabel):
    '''Logo widget.'''

    def __init__(self, parent=None):
        '''Instantiate logo widget.'''
        super(Logo, self).__init__(parent=parent)

        self.setObjectName('ftrack-logo-widget')

        self.pre_build()
        self.build()

    def pre_build(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.main_layout)

    def build(self):
        logoPixmap = QtGui.QPixmap(':ftrack/image/default/ftrackLogoLabel')
        if not logoPixmap is None:
            self.setPixmap(
                logoPixmap.scaled(
                    QtCore.QSize(self.width(), 20),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
            )
        else:
            self.setText("ftrack1")


class User(QtWidgets.QWidget):
    '''User name and logo widget.'''

    def __init__(self, session, parent=None):
        '''Instantiate user name and logo widget using *username*.'''

        super(User, self).__init__(parent=parent)
        self.session = session

        self.setObjectName('ftrack-userid-widget')

        self.pre_build()
        self.build()

    def pre_build(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(QtCore.Qt.AlignRight)
        self.setLayout(self.main_layout)

    def build(self):
        username = self.session.api_user
        self.label = QtWidgets.QLabel(self)
        self.image = thumbnail.User(self.session, parent=self)
        self.image.setFixedSize(35, 35)

        self.main_layout.addWidget(self.image)
        self.main_layout.addWidget(self.label)

        self.image.load(username)

        if username not in NAME_CACHE:
            user = self.session.query(
                'select first_name, last_name from User where username is "{}"'.format(
                    username
                )
            ).first()

            NAME_CACHE[username] = '{} {}'.format(
                user['first_name'], user['last_name']
            ).title()

        self.label.setText(NAME_CACHE[username])


class MessageBox(QtWidgets.QWidget):
    '''Message widget.'''

    def __init__(self, parent=None):
        '''Instantiate message widget.'''

        super(MessageBox, self).__init__(parent=parent)
        self.setObjectName('ftrack-message-box')

        self.pre_build()
        self.build()

    def pre_build(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.main_layout)

    def build(self):
        self.label = QtWidgets.QLabel(parent=self)
        self.label.resize(QtCore.QSize(450, 80))

        self.icon = QtWidgets.QLabel(parent=self)
        self.icon.resize(QtCore.QSize(45, 45))

        self.label.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.label.hide()
        self.label.setObjectName('ftrack-header-message-info')

        self.main_layout.addWidget(self.icon)
        self.main_layout.addStretch()

        self.main_layout.addWidget(self.label)

    def setMessage(self, message, level):
        '''Set *message* and *level*.'''

        class_type = 'ftrack-header-message-%s' % level

        self.label.setObjectName(class_type)

        self.setStyleSheet(self.styleSheet())
        self.label.setText(str(message))
        self.icon.setVisible(True)
        self.label.setVisible(True)

    def dismissMessage(self):
        '''Dismiss the message.'''
        self.label.setText('')
        self.label.setVisible(False)
        self.icon.setText('')
        self.icon.setVisible(False)
