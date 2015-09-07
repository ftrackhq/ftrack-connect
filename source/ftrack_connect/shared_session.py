# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import ftrack_api

_shared_session = None

def get_shared_session():
    '''Return shared ftrack_api session.'''
    global _shared_session
    if not _shared_session:
        _shared_session = ftrack_api.Session()

    return _shared_session
