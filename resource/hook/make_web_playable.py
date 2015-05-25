# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging
import os

import ftrack

log = logging.getLogger(__name__)


def callback(event):
    '''Default make-web-playable hook.

    The hook callback accepts an *event*.

    event['data'] should contain:

        * versionId - The id of the version to make reviewable.
        * path - The path to the file to use as the component.

    Will raise :py:exc:`ValueError` if the provided path is not an accessible
    file and :py:exc:`ftrack.FTrackError` if cloud storage is full or not
    enabled.

    '''
    versionId = event['data']['versionId']
    path = event['data']['path']

    version = ftrack.AssetVersion(versionId)

    # Validate that the path is an accessible file.
    if not os.path.isfile(path):
        raise ValueError(
            '"{0}" is not a valid filepath.'.format(path)
        )

    # ftrack.Review.makeReviewable uploads file to cloud storage and triggers
    # encoding of the file to appropirate formats(mp4 and webm).
    ftrack.Review.makeReviewable(version, path)

    log.info('make-reviewable hook completed.')


def register(registry, **kw):
    '''Register hook.'''

    logger = logging.getLogger(
        'ftrack_connect:make_web_playable.register'
    )

    # Validate that registry is an instance of ftrack.Registry. If not,
    # assume that register is being called from a new or incompatible API and
    # return without doing anything.
    if not isinstance(registry, ftrack.Registry):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack.Registry instance.'.format(registry)
        )
        return

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.connect.publish.make-web-playable',
        callback
    )
