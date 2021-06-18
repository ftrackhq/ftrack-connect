# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import logging
import ftrack_api


class Parser(object):
    '''Resolves location and component data into a path.

    The resolver supports resolving locations implemented in ftrack-python-api.

    '''

    def __init__(self, session):
        '''Instansiate with *session* and *filter_locations*.

        *session* is a ftrack_api.session.Session.

        *filter_locations* is a callable that accepts a location name as
        argument and returns true if it should be resolved.

        '''
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        super(Parser, self).__init__()

        self.session = session

    def __call__(self, event):
        '''Resolve path for *event*.'''
        event['data']['file_path']
        return dict(path=path)


def register(session, **kw):
    '''Register hooks.'''

    logger = logging.getLogger(
        'ftrack_connect.resolver.register'
    )

    # Validate that session is an instance of ftrack_api.session.Session. If
    # not, assume that register is being called from an old or incompatible API
    # and return without doing anything.
    if not isinstance(session, ftrack_api.Session):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack.Registry instance.'.format(session)
        )
        return

    resolver = Parser(
        session=session,
    )

    logger.info('Subscribing to topic ftrack.location.request-resolve')
    session.event_hub.subscribe(
        u'topic=ftrack-connect.parse-file-name'
        u'and source.user.username="{0}"'.format(
            session.api_user
        ),
        resolver
    )
