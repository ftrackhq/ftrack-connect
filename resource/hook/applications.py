# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import getpass

import ftrack
import ftrack_connect.application

ACTION_IDENTIFIER = 'ftrack-connect-launch-applications-action'


def register(registry, **kw):
    '''Register hooks.'''
    applicationStore = ftrack_connect.application.ApplicationStore()

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.action.discover and source.user.username={0}'.format(
            getpass.getuser()
        ),
        ftrack_connect.application.ApplicationDiscoverer(
            applicationStore, ACTION_IDENTIFIER
        )
    )

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.action.launch and source.user.username={0} '
        'and data.actionIdentifier={1}'.format(
            getpass.getuser(), ACTION_IDENTIFIER
        ),
        ftrack_connect.application.ApplicationLauncher(applicationStore)
    )
