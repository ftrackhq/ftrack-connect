# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from QtExt import QtWidgets
import ftrack

import ftrack_connect.asynchronous


class EntityPath(QtWidgets.QLineEdit):
    '''Entity path widget.'''

    def __init__(self, *args, **kwargs):
        '''Instantiate the entity path widget.'''
        super(EntityPath, self).__init__(*args, **kwargs)
        self.setReadOnly(True)

    @ftrack_connect.asynchronous.asynchronous
    def setEntity(self, entity):
        '''Set the *entity* for this widget.'''
        names = []
        entities = [entity]
        try:
            entities.extend(entity.getParents())
        except AttributeError:
            pass

        for entity in entities:
            if entity:
                if isinstance(entity, ftrack.Show):
                    names.append(entity.getFullName())
                else:
                    names.append(entity.getName())

        # Reverse names since project should be first.
        names.reverse()
        self.setText(' / '.join(names))
