# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys

from PySide import QtGui, QtCore
import ftrack


def register(connect):
    '''Register publish plugin to ftrack connect.'''
    publisher = Publisher()
    connect.add(publisher, publisher.getName())


class Publisher(QtGui.QStackedWidget):
    '''Base widget for ftrack connect publisher plugin.'''

    # Add signal for when the entity is changed.
    entityChanged = QtCore.Signal(object)

    requestFocus = QtCore.Signal(object)
    requestClose = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        '''Instantiate the publisher widget.'''
        super(Publisher, self).__init__(*args, **kwargs)

        # Inline to avoid circular import
        from .widget.blocking_indicator import BlockingIndicator
        self.idleView = BlockingIndicator(
            parent=self, text='Select task in ftrack to start publisher.'
        )
        self.addWidget(
            self.idleView
        )

        # Inline to avoid circular import
        from .widget.publisher import Publisher as Publish
        self.publishView = Publish(parent=self)
        self.addWidget(
            self.publishView
        )

        # Inline to avoid circular import
        from .widget.loading_indicator import LoadingIndicator
        self.loadingView = LoadingIndicator(parent=self)
        self.addWidget(
            self.loadingView
        )

        self.publishView.publishStarted.connect(
            self._onPublishStarted
        )

        self.publishView.publishFinished.connect(
            self._onPublishFinished
        )

        self.loadingView.loadingDone.connect(
            self._onLoadingDone
        )

        self.entityChanged.connect(
            self._onEntityChanged
        )

    def _onPublishFinished(self, success):
        '''Callback for publish finished signal.'''
        self.loadingView.setDoneState()

    def _onPublishStarted(self):
        '''Callback for publish started signal.'''
        self.loadingView.setLoadingState()
        self._setView(self.loadingView)

    def _onEntityChanged(self):
        '''Callback for entityChanged signal.'''
        self._setView(
            self.publishView
        )

    def _onLoadingDone(self):
        '''Callback for loadingDone signal.'''
        self._setView(
            self.idleView
        )

        self.clear()

        self.requestClose.emit(self)

    def _setView(self, view):
        '''Set active widget of the publisher.'''
        self.setCurrentWidget(view)

    def clear(self):
        '''Reset the publisher to it's initial state.'''
        self._entity = None
        self.publishView.clear()

    def getName(self):
        '''Return name of widget.'''
        return 'Publish'

    def setEntity(self, entity):
        '''Set the *entity* for the publisher.'''
        self._entity = entity
        self.entityChanged.emit(entity)

        self.publishView.setEntity(entity)

    def start(self, entity, **kwargs):
        '''Clear state, set the *entity* and request to start the publisher.'''
        self.clear()
        self.setFocus(QtCore.Qt.OtherFocusReason)

        entity = ftrack.Task(
            entity.get('entityId')
        )
        self.setEntity(entity)
        self.requestFocus.emit(self)
