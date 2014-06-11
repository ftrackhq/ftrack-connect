# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui


class Component(QtGui.QWidget):
    '''Represent a component.'''

    def __init__(self, value=None, parent=None):
        '''Initialise widget with initial component *value* and *parent*.'''
        super(Component, self).__init__(parent=parent)
        self._value = value
