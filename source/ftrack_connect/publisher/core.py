# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import threading
import time

from PySide import QtGui, QtCore
import ftrack


def asynchronous(f):
    '''Decorator to make a method asynchronous using its own thread.'''
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=f, args=args, kwargs=kwargs)
        thread.start()
    return wrapper


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
        from view.idle import BlockingIdleView
        idleView = BlockingIdleView(
            parent=self, text='Select task in ftrack to start publisher.'
        )
        self.addWidget(
            idleView
        )

        # Inline to avoid circular import
        from view.publish import PublishView
        self.publishView = PublishView(parent=self)
        self.addWidget(
            self.publishView
        )

        # Inline to avoid circular import
        from view.loading import LoadingView
        loadingView = LoadingView(parent=self)
        self.addWidget(
            loadingView
        )

        self.publishView.publishStarted.connect(
            lambda: self._setView(loadingView)
        )

        self.publishView.publishStarted.connect(loadingView.setLoadingState)
        self.publishView.publishFinished.connect(loadingView.setDoneState)
        self.publishView.publishFailed.connect(loadingView.setDoneState)

        loadingView.loadingDone.connect(
            lambda: self._setView(idleView)
        )

        loadingView.loadingDone.connect(
            lambda: self.requestClose.emit(self)
        )

        self.entityChanged.connect(
            lambda: self._setView(self.publishView)
        )

    def getName(self):
        '''Return name of widget.'''
        return 'Publish'

    def _setView(self, view):
        '''Set active widget of the publisher.'''
        self.setCurrentWidget(view)

    def setEntity(self, entity):
        '''Set the *entity* for the publisher.'''
        self._entity = entity
        self.entityChanged.emit(entity)

        self.publishView.setEntity(entity)

    def start(self, entity, **kwargs):
        entity = ftrack.Task(
            entity.get('entityId')
        )

        self.setEntity(entity)
        self.requestFocus.emit(self)
