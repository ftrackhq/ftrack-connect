# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import ftrack_connect.asynchronous
import ftrack_connect.session


_track_usage_session = None


@ftrack_connect.asynchronous.asynchronous
def track_usage(event_name, metadata=None):
    '''Track usage of *event_name* and *metadata*.'''
    global _track_usage_session

    if _track_usage_session is None:
        _track_usage_session = ftrack_connect.session.get_session()

    _track_usage_session._call([{
        'action': '_track_usage',
        'data': {
            'type': 'event',
            'name': event_name,
            'data': metadata
        }
    }])
