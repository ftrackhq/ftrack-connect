# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import logging
import functools
import json
import appdirs

import ftrack_api.session
logger = logging.getLogger('ftrack_connect:publish-components')


def publish_components(event, session=None):
    '''Handle *event* and publish components.'''
    components_config = event['data'].get('components_config')

    prefix = appdirs.user_data_dir(
        'ftrack-connect/data', 'ftrack'
    )

    if not components_config.startswith(prefix):
        return {
            'success': False,
            'message': 'Components config should be in connect data folder.'
        }

    with open(components_config) as data:
        components = json.load(data)

    logger.info('Publishing components: {0!r}'.format(components))

    for component in components:
        component_data = component.copy()

        # Query version and set the relation to ensure standard structure knows
        # how to find it.
        # TODO: Remove this when Standard structure has been updated.
        if 'version_id' in component_data:
            component_data['version'] = session.get(
                'AssetVersion', component_data['version_id']
            )

        path = component_data.pop('path')
        location = component_data.pop('location', 'auto')
        session.create_component(path, data=component_data, location=location)

    session.commit()
    return { 'success': True }


def subscribe(session):
    '''Subscribe to events.'''
    topic = 'ftrack.connect.publish-components'
    logger.info('Subscribing to event topic: {0!r}'.format(topic))
    session.event_hub.subscribe(
        u'topic="{0}" and source.user.username="{1}"'.format(
            topic, session.api_user
        ),
        functools.partial(publish_components, session=session)
    )


def register(session, **kw):
    '''Register plugin. Called when used as an plugin.'''
    # Validate that session is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an old or incompatible API and
    # return without doing anything.
    if not isinstance(session, ftrack_api.session.Session):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack_api.Session instance.'.format(session)
        )
        return

    subscribe(session)
    logger.debug('Plugin registered')


if __name__ == '__main__':
    '''Set up event listener manually, used for development.'''
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('ftrack_api').setLevel(logging.INFO)
    logger.info('Starting as standalone script')
    _session = ftrack_api.Session()
    subscribe(_session)
    _session.event_hub.wait()
