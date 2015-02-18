# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import logging

import ftrack_legacy
import ftrack
import nuke

from ftrack_connect_nuke.ftrackConnector.maincon import FTAssetObject
from ftrack_connect_nuke import ftrackConnector

log = logging.getLogger(__name__)


def _getNodeName(assetId):
    '''Return node name in scene by *assetName*.

    TODO: This should be done with something more unique than asset name.

    '''
    nodes = {}

    for node in nuke.allNodes():
        assetIdKnob = node.knob('assetId')
        if assetIdKnob and assetIdKnob.value():
            nodes[assetIdKnob.value()] = node

    return nodes[assetId].name()


def callback(event):
    '''Handle version notification call to action.'''
    location = ftrack_legacy.Location('ftrack.connect')

    session = ftrack.Session()
    result = session.query(
        'select components, id, asset.name from '
        'AssetVersion where id is "{0}"'.format(event['data']['version_id'])
    ).all()[0]

    # TODO: See if this can be done by using the Locations API in the new
    # API.
    componentInLocation = location.getComponent(
        result['components'][0]['id']
    )

    accessPath = componentInLocation.getFilesystemPath()

    importObj = FTAssetObject(
        componentId=result['components'][0]['id'],
        filePath=accessPath,
        componentName=result['components'][0]['name'],
        assetVersionId=result['id']
    )

    ftrackConnector.Connector.changeVersion(
        iAObj=importObj,
        applicationObject=_getNodeName(result['asset']['id'])
    )


def register(registry, **kw):
    '''Register hook.'''
    ftrack_legacy.EVENT_HUB.subscribe(
        'topic=ftrack.connect.notification.version',
        callback
    )
