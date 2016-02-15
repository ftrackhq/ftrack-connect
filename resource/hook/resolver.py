# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import logging

import ftrack_api


class Resolver(object):
    '''Resolves location and component data into a path.

    The resolver supports resolving locations implemented in ftrack-python-api.

    '''

    def __init__(self, session, filter_locations):
        '''Instansiate with *session* and *filter_locations*.

        *session* is a ftrack_api.session.Session.

        *filter_locations* is a callable that accepts a location name as
        argument and returns true if it should be resolved.

        '''
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        super(Resolver, self).__init__()

        self.session = session
        self.filter_locations = filter_locations

    def __call__(self, event):
        '''Resolve path for *event*.'''
        location_name = event['data']['locationName']
        component_id = event['data']['componentId']

        self.logger.debug(
            u'Resolving file system path for event: {0!r}.'.format(event)
        )

        if not self.filter_locations(location_name):
            self.logger.debug(
                u'Skipping resolve for location {0}.'.format(location_name)
            )
            return

        location = self.session.query(
            'Location where name is "{0}"'.format(location_name)
        ).one()

        if not location.accessor:
            self.logger.debug(
                u'Skipping resolve for location without accessor: '
                u'{0!r}.'.format(location)
            )
            return

        component = self.session.get('Component', component_id)

        resource_identifier = location.get_resource_identifier(component)

        path = None
        try:
            path = location.accessor.get_filesystem_path(resource_identifier)
        except ftrack_api.exception.AccessorUnsupportedOperationError:
            try:
                path = location.accessor.get_url(resource_identifier)
            except ftrack_api.exception.AccessorUnsupportedOperationError:
                pass

        if path is None:
            raise ValueError(
                u'Could not resolve {0!r} and {1!r} to a file system path or '
                u'URL.'.format(component, location)
            )

        self.logger.debug(u'Successfully resolved {0!r}.'.format(path))

        return dict(path=path)


def register(session, **kw):
    '''Register hooks.'''

    logger = logging.getLogger(
        'ftrack_connect:resolver.register'
    )

    # Validate that session is an instance of ftrack.Registry. If not,
    # assume that register is being called from a new or incompatible API and
    # return without doing anything.
    if not isinstance(session, ftrack_api.Session):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack.Registry instance.'.format(session)
        )
        return

    built_in_locations = (
        'ftrack.connect', 'ftrack.server', 'ftrack.unmanaged', 'ftrack.review',
        'ftrack.origin'
    )

    resolver = Resolver(
        session=session,
        filter_locations=(
            lambda location_name: location_name not in built_in_locations
        )
    )

    session.event_hub.subscribe(
        u'topic=ftrack.location.request-resolve '
        u'and source.user.username="{0}"'.format(
            session.api_user
        ),
        resolver
    )