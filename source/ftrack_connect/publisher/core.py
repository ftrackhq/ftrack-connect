# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import threading

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


class Publisher(QtGui.QWidget):
    '''Base widget for ftrack connect publisher plugin.'''

    # Add signal for when the entity is changed.
    entityChanged = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        '''Instantiate the publisher widget.'''
        super(Publisher, self).__init__(*args, **kwargs)
        self.setLayout(
            QtGui.QVBoxLayout()
        )

        # Create form layout to keep track of publish form items.
        layout = QtGui.QFormLayout()
        self.layout().addLayout(layout)

        # Local import to avoid circular.
        from component.linked_to import LinkedToComponent
        from component.asset_type_selector import AssetTypeSelectorComponent

        # Add linked to component and connect to entityChanged signal.
        linkedTo = LinkedToComponent()
        layout.addRow('Linked to', linkedTo)
        self.entityChanged.connect(linkedTo.setEntity)

        # Add asset selector.
        assetSelector = AssetTypeSelectorComponent()
        layout.addRow('Asset type', assetSelector)

        # TODO: Remove this call when it is possible to select or start
        # publisher with an entity.
        self.setEntity(ftrack.Task('d547547a-66de-11e1-bdb8-f23c91df25eb'))

    def getName(self):
        '''Return name of widget.'''
        return 'Publisher'

    def addWidget(self, widget):
        '''Add *widget* to internal layout.'''
        layout = self.layout()
        layout.addWidget(widget)

    def setEntity(self, entity):
        '''Set the *entity* for the publisher.'''
        self.entity = entity
        self.entityChanged.emit(entity)
