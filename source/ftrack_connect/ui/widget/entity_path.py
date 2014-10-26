# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui
import ftrack

import ftrack_connect.asynchronous


class EntityPath(QtGui.QLineEdit):
    '''Entity path widget.'''

    def __init__(self, *args, **kwargs):
        '''Instantiate the entity path widget.'''
        super(EntityPath, self).__init__(*args, **kwargs)
        self.setReadOnly(True)

    @ftrack_connect.asynchronous.asynchronous
    def setEntity(self, entity):
        '''Set the *entity* for this widget.'''
        names = []

        while entity is not None:
            if isinstance(entity, ftrack.Show):
                names.append(entity.getFullName())
                entity = None
            else:
                names.append(entity.getName())
                entity = entity.getParent()

        # Reverse names since project should be first.
        names.reverse()
        self.setText(' / '.join(names))
