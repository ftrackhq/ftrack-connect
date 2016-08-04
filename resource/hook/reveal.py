import logging
import os
import subprocess
import sys

import ftrack_api
import ftrack


class RevealComponentAction(object):
    '''Action to reveal component file path in os file browser.'''

    identifier = 'ftrack-connect-reveal-component'

    failed = {
        'success': False,
        'message': (
            'Could not reveal component directory.'
        )
    }

    def __init__(self, session, logger):
        '''Instantiate action with *session*.'''
        self.session = session
        self.logger = logger

    def discover(self, event):
        '''Discover *event*.'''
        selection = event['data'].get('selection', [])
        if (
            len(selection) == 1 and
            selection[0]['entityType'] == 'Component'
        ):
            return {
                'items': [{
                    'label': 'Reveal',
                    'actionIdentifier': self.identifier
                }]
            }

    def launch(self, event):
        '''Launch action for *event*.'''
        selection = event['data']['selection'][0]

        if selection['entityType'] != 'Component':
            return

        component_id = selection['entityId']

        file_path = None
        try:
            legacy_component = ftrack.Component(component_id)
            if (
                legacy_component.getLocation() and
                legacy_component.getFilesystemPath()
            ):
                # Try to resolve with legacy api.
                file_path = legacy_component.getFilesystemPath()

            if file_path is None:
                # Legacy api could not resolve path, try with ftrack-python-api.
                # TODO: Switch to resolving with ftrack-python-api by default.
                component = self.session.get('Component', component_id)
                location = self.session.pick_location(component)
                if hasattr(location, 'get_filesystem_path'):
                    file_path = location.get_filesystem_path(location)

        except Exception:
            self.logger.exception(
                'Could not determine path for component with id {0!r}'.format(
                    component_id
                )
            )

        if file_path is None:
            return self.failed

        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            return self.failed

        if sys.platform == 'win32':
            subprocess.Popen(['start', directory], shell=True)

        elif sys.platform == 'darwin':
            if os.path.exists(file_path):
                # File exists and can be revealed with a selection.
                subprocess.Popen(['open', '-R', file_path])

            else:
                subprocess.Popen(['open', directory])

        else:
            subprocess.Popen(['xdg-open', directory])

        return {
            'success': True,
            'message': 'Successfully revealed component directory.'
        }

    def register(self):
        '''Register to event hub.'''
        self.session.event_hub.subscribe(
            u'topic=ftrack.action.discover '
            u'and source.user.username="{0}"'.format(
                self.session.api_user
            ),
            self.discover
        )

        self.session.event_hub.subscribe(
            'topic=ftrack.action.launch and data.actionIdentifier={0} and '
            'source.user.username="{1}"'.format(
                self.identifier,
                self.session.api_user
            ),
            self.launch
        )


def register(session, **kw):
    '''Register hooks.'''

    logger = logging.getLogger(
        'ftrack_connect:reveal.register'
    )

    # Validate that session is an instance of ftrack_api.session.Session. If
    # not, assume that register is being called from an old or incompatible API
    # and return without doing anything.
    if not isinstance(session, ftrack_api.Session):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'Session instance.'.format(session)
        )
        return

    action = RevealComponentAction(session, logger)
    action.register()
