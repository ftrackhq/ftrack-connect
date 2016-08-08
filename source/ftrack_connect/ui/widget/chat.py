# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from Qt import QtWidgets
from Qt import QtCore


import ftrack_connect.ui.widget.item_list


class Message(QtWidgets.QFrame):
    '''Represent a chat message.'''

    def __init__(self, text, name, me=False, parent=None):
        '''Initialise widget with *text* and *name*.'''
        super(Message, self).__init__(parent)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        if me:
            name = 'You'

        self.sender = QtWidgets.QLabel(name)
        self.layout().addWidget(self.sender, stretch=0)

        self.text = QtWidgets.QLabel(text)
        self.text.setWordWrap(True)
        self.text.setObjectName('message-text')

        self.layout().addWidget(self.text, stretch=1)

        if me:
            self.sender.setStyleSheet(
                '''
                    QLabel {
                        color: #1CBC90;
                    }
                '''
            )
            self.sender.setAlignment(QtCore.Qt.AlignRight)
            self.text.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        else:
            self.sender.setStyleSheet(
                '''
                    QLabel {
                        color: rgba(52, 152, 219, 255);
                    }
                '''
            )


class Feed(ftrack_connect.ui.widget.item_list.ItemList):
    '''Chat feed.'''

    def __init__(self, parent=None):
        '''Initialise widget with *parent*.'''
        super(Feed, self).__init__(
            widgetFactory=self._createChatMessageWidget,
            widgetItem=lambda widget: widget.value(),
            parent=parent
        )
        self.setObjectName('message-feed')
        self.list.setSelectionMode(
            QtWidgets.QAbstractItemView.NoSelection
        )
        self.list.setShowGrid(False)
        self._verticalScrollBar = self.list.verticalScrollBar()

    def _createChatMessageWidget(self, message):
        '''Create a message widget from *message*.'''
        return Message(
            message['text'],
            message['name'],
            message.get('me', False)
        )

    def addMessage(self, item, row=None):
        '''Add *item* to feed.'''
        if row is None:
            row = self.count()

        super(Feed, self).addItem(item, row=row)

        currentMaximum = self._verticalScrollBar.maximum()
        self._verticalScrollBar.setMaximum(
            currentMaximum + self._verticalScrollBar.singleStep()
        )

        self._verticalScrollBar.setValue(
            self._verticalScrollBar.maximum()
        )


class ChatTextEdit(QtWidgets.QTextEdit):

    # Signal emitted when return is pressed on it's own.
    returnPressed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(ChatTextEdit, self).__init__(*args, **kwargs)

        # Install event filter at application level in order to handle
        # return pressed events
        application = QtCore.QCoreApplication.instance()
        application.installEventFilter(self)

    def eventFilter(self, obj, event):
        '''Filter *event* sent to *obj*.'''
        if obj == self:

            if event.type() == QtCore.QEvent.KeyPress:

                if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):

                    # If nativeModifiers if not equal to 0 that means return
                    # was pressed in combination with something else.
                    if event.nativeModifiers() == 0:
                        self.returnPressed.emit()
                        return True

        # Let event propagate.
        return False


class Chat(QtWidgets.QFrame):
    '''Chat widget.'''

    chatMessageSubmitted = QtCore.Signal(object)

    def __init__(self, parent=None):
        '''Initiate chat widget with *chatHub*.'''
        super(Chat, self).__init__(parent)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.setObjectName('chat-widget')

        self._chatFeed = Feed(parent)
        self.layout().addWidget(self._chatFeed, stretch=1)

        self._messageArea = ChatTextEdit(self)
        self._messageArea.setMinimumHeight(30)
        self._messageArea.setMaximumHeight(75)
        self._messageArea.returnPressed.connect(self.onReturnPressed)
        self.layout().addWidget(self._messageArea, stretch=0)

        self._sendMessageButton = QtWidgets.QPushButton('Submit')
        self.layout().addWidget(self._sendMessageButton, stretch=0)

        self._sendMessageButton.clicked.connect(self.onReturnPressed)

        self.busyOverlay = ftrack_connect.ui.widget.overlay.BusyOverlay(
            self, message='Loading'
        )
        self.hideOverlay()

    def load(self, history):
        '''Load chat *history*'''
        self._chatFeed.clearItems()
        for message in history:
            self.addMessage(message)

    def onReturnPressed(self):
        '''Handle return pressed events.'''
        text = self._messageArea.toPlainText()

        if text:
            self.chatMessageSubmitted.emit(text)
            self._messageArea.setText('')

    def addMessage(self, message):
        '''Add *message* to feed.'''
        self._chatFeed.addMessage(message)

    def showOverlay(self):
        '''Show chat overlay.'''
        self.busyOverlay.show()

    def hideOverlay(self):
        '''Show chat overlay.'''
        self.busyOverlay.hide()
