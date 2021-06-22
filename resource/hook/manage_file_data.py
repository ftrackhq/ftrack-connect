import ftrack_api
import logging
from pprint import pformat
import functools


def my_callback(session, event):
    '''Event callback printing all new or updated entities.'''
    entities = event['data'].get('entities', [])
    for entity in entities:
        logging.info(entity)
        # if entity.get('action') != 'remove':
        #     continue

        # if entity.get('entityType') != 'assetversion':
        #     continue
        #
        # logging.info('ENTITY:{}'.format(entity))
        # deleted_entity_id = entity.get('entityId')
        # components = session.query(
        #     'Component where version_id is {}'.format(
        #         deleted_entity_id
        #     )
        # ).all()
        #
        # logging.info('COMPS: {}'.format(components))
        #

def register(session, **kwargs):
    # Subscribe to events with the update topic.
    handle_delete_event = functools.partial(
        my_callback,
        session
    )

    session.event_hub.subscribe('topic=ftrack.update', handle_delete_event)
