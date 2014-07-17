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

    def _onParentResized(self, event):
        '''Handle parent resize event to make this widget match size.'''
        self.resize(event.size())
