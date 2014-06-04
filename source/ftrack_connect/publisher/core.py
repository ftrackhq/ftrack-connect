# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui


def register(connect):
    '''Register publish plugin to ftrack connect.'''
    publisher = Publisher()
    connect.add(publisher, publisher.getName())


class Publisher(QtGui.QWidget):
    '''Base widget for ftrack connect publisher plugin.'''

    def getName(self):
        '''Return name of widget.'''
        return 'Publisher'

    def __init__(self, *args, **kwargs):
        '''Instantiate the publisher widget.'''
        super(Publisher, self).__init__(*args, **kwargs)
        self.setLayout(
            QtGui.QVBoxLayout()
        )

    def addWidget(self, widget):
        '''Add *widget* to internal layout.'''
        layout = self.layout()
        layout.addWidget(widget)
