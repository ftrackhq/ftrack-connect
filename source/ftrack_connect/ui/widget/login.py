# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore


class ClickableLabel(QtGui.QLabel):
    clicked = QtCore.Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()


class Login(QtGui.QWidget):
    '''Login widget class.'''
    # Login signal with params url, username and API key.
    login = QtCore.Signal(object, object, object)

    # Error signal that can be used to present an error message.
    loginError = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        '''Instantiate the login widget.'''
        super(Login, self).__init__(*args, **kwargs)

        layout = QtGui.QVBoxLayout()
        layout.addSpacing(100)
        layout.setContentsMargins(50, 0, 50, 0)
        self.setLayout(layout)

        label = QtGui.QLabel()
        label.setText('Sign in')
        label.setObjectName('login-label')
        layout.addWidget(label, alignment=QtCore.Qt.AlignCenter)

        self.server = QtGui.QLineEdit()
        self.server.setPlaceholderText('Server name/url')
        layout.addWidget(self.server)

        self.username = QtGui.QLineEdit()
        self.username.setPlaceholderText('Username')
        self.username.hide()
        layout.addWidget(self.username)

        self.apiKey = QtGui.QLineEdit()
        self.apiKey.setPlaceholderText('API key')
        self.apiKey.hide()
        layout.addWidget(self.apiKey)

        loginButton = QtGui.QPushButton(text='Sign in')
        loginButton.setObjectName('primary')
        loginButton.clicked.connect(self.handleLogin)
        layout.addWidget(loginButton)

        self.errorLabel = QtGui.QLabel()
        self.errorLabel.setWordWrap(True)
        layout.addWidget(self.errorLabel)
        self.loginError.connect(self.errorLabel.setText)

        layout.addStretch(1)

        self.toggle_api_label = label = ClickableLabel()
        self.toggle_api_label.setText(
            '<a href="#">Click here to sign in with username and API key</a>'
        )
        self.toggle_api_label.clicked.connect(self._toggle_credentials)
        layout.addWidget(self.toggle_api_label, alignment=QtCore.Qt.AlignCenter)
        layout.addSpacing(10)

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
