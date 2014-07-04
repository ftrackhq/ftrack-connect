# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore


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
        self.server.setPlaceholderText('Server url')
        layout.addWidget(self.server)

        self.username = QtGui.QLineEdit()
        self.username.setPlaceholderText('Username')
        layout.addWidget(self.username)

        self.apiKey = QtGui.QLineEdit()
        self.apiKey.setPlaceholderText('API key')
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

    def handleLogin(self):
        '''Fetch login data from form fields and emit login event.'''
        serverUrl = self.server.text()
        username = self.username.text()
        apiKey = self.apiKey.text()

        self.login.emit(serverUrl, username, apiKey)
