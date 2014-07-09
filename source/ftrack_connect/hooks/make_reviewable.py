# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging
import os

import ftrack
ftrack.setup()

# TODO: Get logger from connect application
log = logging  # .getLogger(__name__)


def callback(event, versionId, filePath, **kw):
    '''Default make-reviewable hook.

    The hook callback accepts *event*, the *versionId* of the version to make
    reviewable and the *filePath* to the file to use as component.

    '''
    try:
        version = ftrack.AssetVersion(versionId)
    except ftrack.ftrackerror.FTrackError as error:
        log.error(error.message)
        return

    # Validate that the filePath is an accessible file.
    if not os.path.isfile(filePath):
        log.error(
            '{0} is not a valid filepath.'.format(filePath)
        )
        return

    # makeReviewable uploads file to cloud storage and triggers encoding of
    # the file to appropirate formats(mp4 and webm).
    try:
        ftrack.Review.makeReviewable(version, filePath)
    except ftrack.ftrackerror.FTrackError as error:
        log.error(error.message)
        return

    log.info('make-reviewable hook completed.')


ftrack.TOPICS.subscribe('ftrack.connect.publish.make-reviewable', callback)

# TODO: Remove wait since it should be executed synchrounus.
ftrack.TOPICS.wait()
