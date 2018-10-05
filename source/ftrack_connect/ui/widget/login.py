# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from QtExt import QtWidgets, QtCore, QtGui


class ClickableLabel(QtWidgets.QLabel):
    '''Clickable label class.'''

    clicked = QtCore.Signal()

    def mousePressEvent(self, event):
        '''Override mouse press to emit signal.'''
        self.clicked.emit()


class Login(QtWidgets.QWidget):
    '''Login widget class.'''
    # Login signal with params url, username and API key.
    login = QtCore.Signal(object, object, object)

    # Error signal that can be used to present an error message.
    loginError = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        '''Instantiate the login widget.'''
        super(Login, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()
        layout.addSpacing(50)
        layout.setContentsMargins(50, 0, 50, 0)
        layout.setSpacing(15)
        self.setLayout(layout)

        logo = QtWidgets.QLabel()
        logoPixmap = QtGui.QPixmap(':ftrack/image/default/ftrackLogoLabelDark')
        logo.setPixmap(
            logoPixmap.scaled(
                QtCore.QSize(100, 100),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
        )
        layout.addWidget(logo, alignment=QtCore.Qt.AlignCenter)
        layout.addSpacing(25)

        label = QtWidgets.QLabel()
        label.setText('Sign in')
        label.setObjectName('login-label')
        layout.addWidget(label, alignment=QtCore.Qt.AlignCenter)

        self.server = QtWidgets.QLineEdit()
        self.server.setPlaceholderText('Site name or custom domain URL')
        layout.addWidget(self.server)

        self.username = QtWidgets.QLineEdit()
        self.username.setPlaceholderText('User name')
        self.username.hide()
        layout.addWidget(self.username)

        self.apiKey = QtWidgets.QLineEdit()
        self.apiKey.setPlaceholderText('API key')
        self.apiKey.hide()
        layout.addWidget(self.apiKey)

        loginButton = QtWidgets.QPushButton(text='SIGN IN')
        loginButton.setObjectName('primary')
        loginButton.clicked.connect(self.handleLogin)
        loginButton.setMinimumHeight(35)
        layout.addWidget(loginButton)

        label = QtWidgets.QLabel()
        label.setObjectName('lead-label')
        label.setContentsMargins(0, 0, 0, 0)
        label.setText(
            'Your site name is your ftrackapp.com web address '
            '(e.g https://sitename.ftrackapp.com OR your custom domain URL).'
        )
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)

        # Min height is required due to issue when word wrap is True and window
        # being resized which cases text to dissapear.
        label.setMinimumHeight(50)

        label.setMinimumWidth(300)
        layout.addWidget(label, alignment=QtCore.Qt.AlignCenter)

        self.errorLabel = QtWidgets.QLabel()
        self.errorLabel.setWordWrap(True)
        layout.addWidget(self.errorLabel)
        self.loginError.connect(self.on_set_error)

        layout.addStretch(1)

        self.toggle_api_label = label = ClickableLabel()
        self.toggle_api_label.setObjectName('lead-label')
        self.toggle_api_label.setText(
            'Trouble signing in? '
            '<a href="#" style="color: #935BA2;">Sign in with username and API key</a>'
        )
        self.toggle_api_label.clicked.connect(self._toggle_credentials)
        layout.addWidget(self.toggle_api_label, alignment=QtCore.Qt.AlignCenter)
        layout.addSpacing(20)

    def on_set_error(self, error):
        '''Set the error text and disable the login widget.'''
        self.errorLabel.setText(error)

    def handleLogin(self):
        '''Fetch login data from form fields and emit login event.'''
        serverUrl = self.server.text()
        username = self.username.text()
        apiKey = self.apiKey.text()

        self.login.emit(serverUrl, username, apiKey)

    def _toggle_credentials(self):
        '''Toggle credential fields.'''
        self.apiKey.show()
        self.username.show()
        self.toggle_api_label.hide()
