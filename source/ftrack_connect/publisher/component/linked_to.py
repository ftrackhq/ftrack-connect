# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui
import ftrack

from ..core import asynchronous


class LinkedToComponent(QtGui.QLineEdit):
    '''Linked to entity component.'''

    def __init__(self, *args, **kwargs):
        '''Instantiate the linked to component.'''
        super(LinkedToComponent, self).__init__(*args, **kwargs)
        self.setReadOnly(True)

    @asynchronous
    def setEntity(self, entity):
        '''Set the entity for this component.'''
        names = []
        for parent in entity.getParents():
            if isinstance(parent, ftrack.Show):
                names.append(parent.getFullName())
            else:
                names.append(parent.getName())

        # Reverse names since project should be first.
        names.reverse()
        self.setText(' / '.join(names))
