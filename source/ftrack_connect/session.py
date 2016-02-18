# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import os

import ftrack_api

_shared_session = None


def destroy_shared_session():
    '''Destroy the shared session.'''
    global _shared_session

    if _shared_session:
        # Disconnect from event hub but do not unsubscribe as that will be
        # blocking and slow. Also there is no need to unsubscribe since the
        # session will not be used any more.
        _shared_session.event_hub.disconnect(False)

        del _shared_session
        _shared_session = None


def get_shared_session():
    '''Return shared ftrack_api session.'''
    global _shared_session

    if not _shared_session:
        # Create API session using credentials as stored by the application
        # when logging in.
        _shared_session = ftrack_api.Session(
            server_url=os.environ['FTRACK_SERVER'],
            api_key=os.environ['FTRACK_APIKEY'],
            api_user=os.environ['LOGNAME']
        )

    return _shared_session


def get_session():
    '''Return new ftrack_api session configure without plugins or events.'''
    # Create API session using credentials as stored by the application
    # when logging in.
    # TODO: Once API is thread-safe, consider switching to a shared session.
    return ftrack_api.Session(
        server_url=os.environ['FTRACK_SERVER'],
        api_key=os.environ['FTRACK_APIKEY'],
        api_user=os.environ['LOGNAME'],
        auto_connect_event_hub=False,
        plugin_paths=[]
    )