# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from QtExt import QtCore, QtWidgets
import ftrack

import ftrack_connect.ui.application
import ftrack_connect.ui.widget.overlay
import ftrack_connect.ui.widget.publisher
import ftrack_connect.usage


def register(connect):
    '''Register publish plugin to ftrack connect.'''
    publisher = Publisher()
    connect.addPlugin(publisher, publisher.getName())


class PublisherBlockingOverlay(
    ftrack_connect.ui.widget.overlay.BlockingOverlay
):
    '''Custom blocking overlay for publisher.'''

    def __init__(self, parent, message=''):
        super(PublisherBlockingOverlay, self).__init__(parent, message=message)
        self.confirmButton = QtWidgets.QPushButton('Ok')
        self.contentLayout.insertWidget(
            3, self.confirmButton, alignment=QtCore.Qt.AlignCenter, stretch=0
        )
        self.confirmButton.hide()
        self.confirmButton.clicked.connect(self.hide)
        self.content.setMinimumWidth(350)


class Publisher(ftrack_connect.ui.application.ApplicationPlugin):
    '''Base widget for ftrack connect publisher plugin.'''

    #: Signal to emit when the entity is changed.
    entityChanged = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        '''Instantiate the publisher widget.'''
        super(Publisher, self).__init__(*args, **kwargs)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.publishView = ftrack_connect.ui.widget.publisher.Publisher()
        layout.addWidget(self.publishView)

        self.blockingOverlay = PublisherBlockingOverlay(self)
        self.blockingOverlay.hide()

        self.busyOverlay = ftrack_connect.ui.widget.overlay.BusyOverlay(self)
        self.busyOverlay.hide()

        self.publishView.publishStarted.connect(
            self._onPublishStarted
        )

        self.publishView.publishFinished.connect(
            self._onPublishFinished
        )

        self.entityChanged.connect(
            self._onEntityChanged
        )

    def _onPublishStarted(self):
        '''Callback for publish started signal.'''
        self.blockingOverlay.hide()
        self.busyOverlay.show()

    def _onPublishFinished(self, success):
        '''Callback for publish finished signal.'''
        self.busyOverlay.hide()
        if success:
            self.blockingOverlay.setMessage(
                'Publish finished!\n \n'
                'Select another task in ftrack or continue to publish using '
                'current task.'
            )
            self.blockingOverlay.confirmButton.show()
            self.blockingOverlay.show()

            ftrack_connect.usage.send_event('PUBLISHED-FROM-CONNECT')


    def _onEntityChanged(self):
        '''Callback for entityChanged signal.'''
        self.blockingOverlay.hide()
        self.busyOverlay.hide()

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

    def start(self, event):
        '''Handle *event*.

        event['data'] should contain:

            * entity - The entity to set on the publisher.

        event['data'] may optionally contain:

            components
                a list of dictionaries with name and path, used to
                automatically populate the list of components.

            thumbnail
                an absolute path to an image file to set as the version's
                thumbnail.

            manageData
                If set, a location which can manage data will be picked.

        Clear state, set the *entity* and request to start the publisher.

        '''
        entity = event['data']['entity']

        self.clear()
        self.setFocus(QtCore.Qt.OtherFocusReason)

        # Add any components from event data
        components = event['data'].get('components', [])
        for componentData in components:
            self.publishView.componentsList.addItem({
                'componentName': componentData.get('name'),
                'resourceIdentifier': componentData.get('path')
            })

        # Add thumbnail from event data
        thumbnail = event['data'].get('thumbnail')
        if thumbnail:
            self.publishView.thumbnailDropZone.setThumbnail(thumbnail)

        # More information from event data
        manageData = event['data'].get('manageData')
        if manageData:
            self.publishView.setManageData(True)

        entity = ftrack.Task(
            entity.get('entityId')
        )
        self.setEntity(entity)
        self.requestApplicationFocus.emit(self)

        ftrack.EVENT_HUB.publishReply(
            sourceEvent=event,
            data={'message': 'Publisher started.'}
        )
