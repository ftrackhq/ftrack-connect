# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import logging

import ftrack_connect.asynchronous
import ftrack_connect.session


logger = logging.getLogger('ftrack_connect:usage')
_log_usage_session = None


@ftrack_connect.asynchronous.asynchronous
def send_event(event_name, metadata=None):
    '''Send usage event with *event_name* and *metadata*.'''
    global _log_usage_session

    if _log_usage_session is None:
        _log_usage_session = ftrack_connect.session.get_session()

    try:
        _log_usage_session._call([{
            'action': '_track_usage',
            'data': {
                'type': 'event',
                'name': event_name,
                'metadata': metadata
            }
        }])
    except Exception:
        logger.exception('Failed to send event.')
