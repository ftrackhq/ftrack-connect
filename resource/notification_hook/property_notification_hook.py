# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import logging

import ftrack_legacy

log = logging.getLogger(__name__)


def callback(event):
    '''Handle property notification call to action.'''
    log.exception('Handle property changed event with data "{0}"'.format(
        event['data']
    ))


def register(registry, **kw):
    '''Register hook.'''
    ftrack_legacy.EVENT_HUB.subscribe(
        'topic=ftrack.connect.notification.property',
        callback
    )
