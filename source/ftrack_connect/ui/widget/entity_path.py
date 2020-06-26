# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from Qt import QtWidgets, QtCore

import ftrack_connect.asynchronous
import ftrack_connect.session


class EntityPath(QtWidgets.QLineEdit):
    '''Entity path widget.'''
    path_ready = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        '''Instantiate the entity path widget.'''
        super(EntityPath, self).__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.path_ready.connect(self.on_path_ready)
        self._session = ftrack_connect.session.get_shared_session()

    @ftrack_connect.asynchronous.asynchronous
    def setEntity(self, entity):
        '''Set the *entity* for this widget.'''
        names = []
        entities=[]
        if entity:
            entities.insert(0, entity)
            entities.extend(entity.get('ancestors', []))

        for entity in entities:
            if entity:
                if isinstance(entity, self._session.types['Project']):
                    names.append(entity['full_name'])
                else:
                    names.append(entity['name'])

        # Reverse names since project should be first.
        names.reverse()
        self.path_ready.emit(names)

    def on_path_ready(self, names):
        '''Set current path to *names*.'''
        self.setText(' / '.join(names))
