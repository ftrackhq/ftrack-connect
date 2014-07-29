# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore

import ftrack_connect.ui.widget.indicator


class Overlay(QtGui.QFrame):
    '''Display a transparent overlay over another widget.

    Customise the background colour using stylesheets. The widget has an object
    name of "overlay".

    '''

    def __init__(self, parent):
        '''Initialise overlay for target *parent*.'''
        super(Overlay, self).__init__(parent=parent)
        self.setObjectName('overlay')
        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain)

        # Install global event filter that will deal with matching parent size
        # and disabling parent interaction when overlay is visible.
        application = QtCore.QCoreApplication.instance()
        application.installEventFilter(self)

    def eventFilter(self, obj, event):
        '''Filter *event* sent to *obj*.

        Maintain sizing of this overlay to match parent widget.

        Disable parent widget of this overlay receiving interaction events
        while this overlay is active.

        '''
        # Match sizing of parent.
        if obj == self.parent():
            if event.type() == QtCore.QEvent.Resize:
                # Relay event.
                self.resize(event.size())

        # Prevent interaction events reaching parent and its child widgets
        # while this overlay is visible.
        if (
            self.isVisible()
            and obj != self
            and event.type() == QtCore.QEvent.FocusIn
        ):
            parent = self.parent()
            if (
                isinstance(obj, QtGui.QWidget)
                and parent.isAncestorOf(obj)
            ):
                # Ensure the targeted object loses its focus.
                obj.clearFocus()

                # Loop through available widgets to move focus to. If an
                # available widget is not a child of the parent widget targeted
                # by this overlay then move focus to it, respecting requested
                # focus direction.
                seen = []
                candidate = obj
                reason = event.reason()

                while True:
                    if reason == QtCore.Qt.TabFocusReason:
                        candidate = candidate.nextInFocusChain()
                    elif reason == QtCore.Qt.BacktabFocusReason:
                        candidate = candidate.previousInFocusChain()
                    else:
                        break

                    if candidate in seen:
                        # No other widget available for focus.
                        break

                    # Keep track of candidates to avoid infinite recursion.
                    seen.append(candidate)

                    if (
                        isinstance(candidate, QtGui.QWidget)
                        and not parent.isAncestorOf(candidate)
                    ):
                        candidate.setFocus(event.reason())
                        break

                # Swallow event.
                return True

        # Let event propagate.
        return False


class BlockingOverlay(Overlay):
    '''Display a standard blocking overlay over another widget.'''

    def __init__(self, parent, message='Processing'):
        '''Initialise with *parent*.

         *message* is the message to display on the overlay.

         '''
        super(BlockingOverlay, self).__init__(parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        layout.addStretch()

        self.content = QtGui.QFrame()
        self.content.setObjectName('content')
        layout.addWidget(
            self.content, alignment=QtCore.Qt.AlignCenter
        )

        self.contentLayout = QtGui.QVBoxLayout()
        self.contentLayout.setContentsMargins(50, 50, 50, 50)
        self.content.setLayout(self.contentLayout)

        self.icon = QtGui.QLabel()
        pixmap = QtGui.QPixmap(':ftrack/image/default/ftrackLogoColor')
        self.icon.setPixmap(
            pixmap.scaledToHeight(36, mode=QtCore.Qt.SmoothTransformation)
        )
        self.icon.setAlignment(QtCore.Qt.AlignCenter)
        self.contentLayout.addWidget(
            self.icon, alignment=QtCore.Qt.AlignCenter
        )

        self.messageLabel = QtGui.QLabel()
        self.messageLabel.setWordWrap(True)
        self.messageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.contentLayout.addWidget(
            self.messageLabel, alignment=QtCore.Qt.AlignCenter
        )

        layout.addStretch()

        self.setStyleSheet('''
            BlockingOverlay {
                background-color: rgba(250, 250, 250, 200);
                border: none;
            }

            BlockingOverlay QFrame#content {
                background-color: white;
                border-radius: 5px;
            }

            BlockingOverlay QLabel {
                background: transparent;
            }
        ''')

        dropShadow = QtGui.QGraphicsDropShadowEffect(self.content)
        dropShadow.setBlurRadius(100)
        dropShadow.setOffset(0)
        dropShadow.setColor(QtGui.QColor(100, 100, 100, 250))
        self.content.setGraphicsEffect(dropShadow)

        self.setMessage(message)

    def message(self):
        '''Return current message.'''
        return self._message

    def setMessage(self, message):
        '''Set current message to display.'''
        self._message = message
        self.messageLabel.setText(message)


class BusyOverlay(BlockingOverlay):
    '''Display a standard busy overlay over another widget.'''

    def __init__(self, parent, message='Processing'):
        '''Initialise with *parent* and busy *message*.'''
        super(BusyOverlay, self).__init__(parent, message=message)

        self.indicator = ftrack_connect.ui.widget.indicator.BusyIndicator()
        self.indicator.setFixedSize(85, 85)

        self.icon.hide()
        self.contentLayout.insertWidget(
            1, self.indicator, alignment=QtCore.Qt.AlignCenter
        )

    def setVisible(self, visible):
        '''Set whether *visible* or not.'''
        if visible:
            self.indicator.start()
        else:
            self.indicator.stop()

        super(BusyOverlay, self).setVisible(visible)
