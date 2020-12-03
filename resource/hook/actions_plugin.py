# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack
import ftrack_api
import logging
from Qt import QtWidgets, QtCore

import ftrack_connect.ui.application
import ftrack_connect.ui.widget.overlay
import ftrack_connect.ui.widget.actions

logger = logging.getLogger('ftrack_connect.plugin.actions')

class Actions(ftrack_connect.ui.application.TabPlugin):
    '''Base widget for ftrack connect actions plugin.'''

    def __init__(self, session, parent=None):
        '''Instantiate the actions widget.'''
        super(Actions, self).__init__(session, parent=parent)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.actionsView = ftrack_connect.ui.widget.actions.Actions(self.session)
        layout.addWidget(self.actionsView)

def register(session, **kw):
    '''Register plugin. Called when used as an plugin.'''
    # Validate that session is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an old or incompatible API and
    # return without doing anything.
    if not isinstance(session, ftrack_api.session.Session):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack_api.Session instance.'.format(session)
        )
        return

    publisher = Actions(session)
    publisher.register()
    logger.debug('Plugin registered')
