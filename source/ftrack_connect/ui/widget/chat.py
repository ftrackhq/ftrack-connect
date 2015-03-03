# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from PySide import QtGui, QtCore


import ftrack_connect.ui.widget.item_list


CHAT_MESSAGES = dict()


class Message(QtGui.QWidget):

    def __init__(self, text, name, me=False, parent=None):
        super(Message, self).__init__(parent)

        self.setLayout(QtGui.QVBoxLayout())

        if me:
            name = 'You'

        self.sender = QtGui.QLabel(name)
        self.layout().addWidget(self.sender)

        self.text = QtGui.QLabel(text)
        self.layout().addWidget(self.text)

        if me:
            self.sender.setStyleSheet(
                '''
                    QLabel {
                        color: green;
                    }
                '''
            )
        else:
            self.sender.setStyleSheet(
                '''
                    QLabel {
                        color: blue;
                    }
                '''
            )
            self.sender.setAlignment(QtCore.Qt.AlignRight)
            self.text.setAlignment(QtCore.Qt.AlignRight)


class Feed(ftrack_connect.ui.widget.item_list.ItemList):
    '''Chat feed.'''

    def __init__(self, parent=None):
        '''Initialise widget with *parent*.'''
        super(Feed, self).__init__(
            widgetFactory=self._createChatMessageWidget,
            widgetItem=lambda widget: widget.value(),
            parent=parent
        )
        self.list.setSelectionMode(
            QtGui.QAbstractItemView.NoSelection
        )
        self.list.setShowGrid(False)

        self.label = QtGui.QLabel('Messages')
        self.layout().insertWidget(0, self.label)

    def _createChatMessageWidget(self, message):
        '''.'''
        return Message(
            message['text'], message['sender']['name'], message.get('me', False)
        )

    def addItem(self, item, row=None):
        '''.'''
        if row is None:
            row = self.count()

        super(Feed, self).addItem(item, row=row)


class Chat(QtGui.QWidget):
    '''Chat widget.'''

    chatMessageSubmitted = QtCore.Signal(object)

    def __init__(self, parent=None):
        '''Initiate chat widget with *chatHub*.'''
        super(Chat, self).__init__(parent)

        self.setLayout(QtGui.QVBoxLayout())

        self._chatFeed = Feed(parent)
        self.layout().addWidget(self._chatFeed, stretch=1)

        self._messageArea = QtGui.QTextEdit()
        self._messageArea.setMinimumHeight(30)
        self._messageArea.setMaximumHeight(75)
        self.layout().addWidget(self._messageArea, stretch=0)

        self._sendMessageButton = QtGui.QPushButton('Submit')
        self.layout().addWidget(self._sendMessageButton)

        self._sendMessageButton.clicked.connect(self._handleMessageSendClick)

    def load(self, history):
        '''Load chat *history*'''
        self._chatFeed.clearItems()
        for message in history:
            self.addMessage(message)

    def _handleMessageSendClick(self):
        text = self._messageArea.toPlainText()
        self.chatMessageSubmitted.emit(text)
        self._messageArea.setText('')

    def addMessage(self, message):
        self._chatFeed.addItem(message)
