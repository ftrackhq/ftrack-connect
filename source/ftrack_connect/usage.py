# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import logging

import ftrack_connect.asynchronous
import ftrack_connect.session


logger = logging.getLogger('ftrack_connect:usage')


def _send_event(session, event_name, metadata=None):
    '''Send usage event with *event_name* and *metadata*.'''

    try:
        session.call([{
            'action': '_track_usage',
            'data': {
                'type': 'event',
                'name': event_name,
                'metadata': metadata
            }
        }])
    except Exception:
        logger.exception('Failed to send event.')

@ftrack_connect.asynchronous.asynchronous
def _send_async_event(session, event_name, metadata=None):
    '''Call __send_event in a new thread.'''
    _send_event(session, event_name, metadata)


def send_event(session, event_name, metadata=None, asynchronous=True):
    '''Send usage event with *event_name* and *metadata*.

    If asynchronous is True, the event will be sent in a new thread.
    '''

    if asynchronous:
        _send_async_event(session, event_name, metadata)
    else:
        _send_event(session, event_name, metadata)
