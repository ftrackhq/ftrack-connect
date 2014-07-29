# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore

import ftrack_connect.ui.widget.indicator


class OverlayResizeEventFilter(QtCore.QObject):
    '''Relay parent resize events to overlay.

    To use, install this filter on the object to observe and listen for resized
    events::

        filter = OverlayResizeEventFilter()
        filter.resized.connect(onResizedDoSomething)
        parent.installEventFilter(filter)

    '''

    #: Signal when observed object is resized.
    resized = QtCore.Signal(object)

    def eventFilter(self, obj, event):
        '''Filter *event* sent to *obj*.'''
        if event.type() == QtCore.QEvent.Resize:
            # Relay event.
            self.resized.emit(event)

        # Let event propagate.
        return False


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

        # Install event filter on parent so that the overlay can match the
        # parent's size.
        eventFilter = OverlayResizeEventFilter(parent)
        eventFilter.resized.connect(self._onParentResized)
        parent.installEventFilter(eventFilter)

        self._previousEnabledStates = {}

    def _onParentResized(self, event):
        '''Handle parent resize event to make this widget match size.'''
        self.resize(event.size())

    def setVisible(self, visible):
        '''Set whether *visible* or not.'''
        if self.isVisible() == visible:
            return

        if visible:
            self._setParentEnabled(False)
        else:
            self._setParentEnabled(True)

        super(Overlay, self).setVisible(visible)

    def _setParentEnabled(self, enabled):
        '''Set parent widget *enabled* state leaving this widget unaltered.

        This is required as this overlay is a child of the target.

        '''
        parent = self.parent()
        children = parent.findChildren(QtGui.QWidget)
        for child in children:
            if self.isAncestorOf(child):
                # Keep overlay enabled.
                continue
            else:
                childId = id(child)
                self._previousEnabledStates.setdefault(childId, True)

                if not enabled:
                    self._previousEnabledStates[childId] = child.isEnabled()
                    child.setEnabled(enabled)
                else:
                    child.setEnabled(self._previousEnabledStates[childId])


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

        self.icon = QtGui.QLabel()
        pixmap = QtGui.QPixmap(':ftrack/image/default/ftrackLogoColor')
        self.icon.setPixmap(
            pixmap.scaledToHeight(36, mode=QtCore.Qt.SmoothTransformation)
        )
        self.icon.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.icon)

        self.messageLabel = QtGui.QLabel()
        self.messageLabel.setWordWrap(True)
        self.messageLabel.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.messageLabel)

        layout.addStretch()

        self.setStyleSheet('''
            BlockingOverlay {
                background-color: rgba(255, 255, 255, 200);
                border: none;
            }

            BlockingOverlay QLabel {
                background: transparent;
            }
        ''')

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

        layout = self.layout()
        self.indicator = ftrack_connect.ui.widget.indicator.BusyIndicator()
        self.indicator.setFixedHeight(85)

        self.icon.hide()
        layout.insertWidget(1, self.indicator)

    def setVisible(self, visible):
        '''Set whether *visible* or not.'''
        if visible:
            self.indicator.start()
        else:
            self.indicator.stop()

        super(BusyOverlay, self).setVisible(visible)
