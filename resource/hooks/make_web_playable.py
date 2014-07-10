# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging
import os

import ftrack

log = logging.getLogger(__name__)


def callback(event, versionId, path, **kw):
    '''Default make-web-playable hook.

    The hook callback accepts *event*, the *versionId* of the version to make
    reviewable and the *path* to the file to use as component.

    Will raise a `ValueError` if the provided path is not an accessible file
    and `ftrack.ftrackerror.FTrackError` if cloud storage is full or not
    enabled.

    '''
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
    ftrack.TOPICS.subscribe(
        'ftrack.connect.publish.make-web-playable',
        callback,
        callbackID='ftrack-connect-default-hook'
    )
