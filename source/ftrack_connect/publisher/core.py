# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import threading
import time

from PySide import QtGui, QtCore
import ftrack
from ftrack_connect.core import ConnectError


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

    def __init__(self, *args, **kwargs):
        '''Instantiate the publisher widget.'''
        super(Publisher, self).__init__(*args, **kwargs)

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

        self.publishView.publishStarted.connect(self._toggleView)

        self.publishView.publishStarted.connect(loadingView.setLoadingState)
        self.publishView.publishFinished.connect(loadingView.setDoneState)
        self.publishView.publishFailed.connect(loadingView.setDoneState)

        loadingView.loadingDone.connect(self._toggleView)

    def getName(self):
        '''Return name of widget.'''
        return 'Publish'

    def _toggleView(self):
        '''Toggle between first and second widget.'''
        if self.currentIndex() == 0:
            self.setCurrentIndex(1)
        else:
            self.setCurrentIndex(0)

    def setEntity(self, entity):
        '''Set the *entity* for the publisher.'''
        self._entity = entity
        self.entityChanged.emit(entity)

        self.publishView.setEntity(entity)
