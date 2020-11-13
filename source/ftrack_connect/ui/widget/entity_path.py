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

    @ftrack_connect.asynchronous.asynchronous
    def setEntity(self, entity):
        '''Set the *entity* for this widget.'''
        if not entity:
            return

        session = ftrack_connect.session.factory.get_session()
        entity = session.merge(entity)

        names = [e['name'] for e in entity.get('link', [])]

        self.path_ready.emit(names)

    def on_path_ready(self, names):
        '''Set current path to *names*.'''
        self.setText(' / '.join(names))
