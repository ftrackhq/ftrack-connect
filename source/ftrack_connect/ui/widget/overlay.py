# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore


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


class Overlay(QtGui.QWidget):
    '''Display a transparent overlay over another widget.

    Customise the background colour using stylesheets. The widget has an object
    name of "overlay".

    '''

    def __init__(self, parent, message=None, opacity=150):
        '''Initialise overlay for target *parent*.

        Set *message* to have a message displayed on the overlay.

        Set *opacity* to control transparency of the overlay.

        '''
        super(Overlay, self).__init__(parent=parent)
        self.setObjectName('overlay')
        self._opacity = opacity
        self._message = message

        # Install event filter on parent so that the overlay can match the
        # parent's size.
        eventFilter = OverlayResizeEventFilter(parent)
        eventFilter.resized.connect(self._onParentResized)
        parent.installEventFilter(eventFilter)

        # Make background transparent.
        palette = QtGui.QPalette(self.palette())
        palette.setColor(palette.Background, QtCore.Qt.transparent)
        self.setPalette(palette)

        # Allow mouse events through to prevent interfering with interaction
        # with target when overlay is inactive.
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        # Make initially invisible to avoid consuming resources.
        self.setVisible(True)

    def message(self):
        '''Return currently set message.'''
        return self._message

    def setMessage(self, message):
        '''Set *message* to display on overlay.'''
        self._message = message
        self.repaint()

    def opacity(self):
        '''Return current set opacity.'''
        return self._opacity

    def setOpacity(self, opacity):
        '''Set opacity of overlay to *opacity*.

        *opacity* should be an integer in range 0-255 where 0 is fully
        transparent.

        '''
        self._opacity = opacity
        self.repaint()

    def paintEvent(self, event):
        '''Handle paint *event*.'''
        if not self.isVisible():
            return

        painter = QtGui.QPainter()
        painter.begin(self)

        try:
            palette = self.palette()
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            area = QtCore.QRect(
                0, 0, painter.device().width(), painter.device().height()
            )

            # # Draw background as dictated by style.
            backgroundColor = palette.color(QtGui.QPalette.Window)
            backgroundColor.setAlpha(self._opacity)
            painter.fillRect(area, backgroundColor)

            # Draw text message if set.
            if self._message:
                textColor = palette.color(QtGui.QPalette.WindowText)
                painter.setPen(QtGui.QPen(textColor))
                painter.drawText(
                    area,
                    (
                        QtCore.Qt.AlignCenter
                        | QtCore.Qt.AlignVCenter
                        | QtCore.Qt.TextWordWrap
                    ),
                    self._message
                )

        finally:
            painter.end()

    def _onParentResized(self, event):
        '''Handle parent resize event to make this widget match size.'''
        self.resize(event.size())
