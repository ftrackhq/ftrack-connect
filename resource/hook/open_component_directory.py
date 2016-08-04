import logging
import os
import subprocess
import sys

import ftrack_api
import ftrack


class OpenComponentDirectoryAction(object):
    '''Action to open a component directory in os file browser.'''

    identifier = 'ftrack-connect-open-component-directory'

    failed = {
        'success': False,
        'message': (
            'Could not open component directory.'
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
                    'label': 'Open directory',
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

        legacy_component = None
        legacy_location = None
        try:
            legacy_component = ftrack.Component(component_id)
            legacy_location = legacy_component.getLocation()
        except Exception:
            self.logger.exception(
                'Could not pick location for legacy component {0!r}'.format(
                    legacy_component
                )
            )

        location = None
        component = None
        try:
            component = self.session.get('Component', component_id)
            location = self.session.pick_location(component)
        except Exception:
            self.logger.exception(
                'Could not pick location for component {0!r}'.format(
                    legacy_component
                )
            )

        if legacy_location and location:
            if legacy_location.getPriority() < location.priority:
                file_path = legacy_component.getFilesystemPath()
                self.logger.info(
                    'Location is defined with a higher priority in legacy api: '
                    '{0!r}'.format(
                        legacy_location
                    )
                )

            else:
                file_path = location.get_filesystem_path(component)
                self.logger.info(
                    'Location is defined with a higher priority in api: '
                    '{0!r}'.format(
                        location
                    )
                )

        elif legacy_location:
            file_path = legacy_component.getFilesystemPath()
            self.logger.info(
                'Location is only defined in legacy api: {0!r}'.format(
                    legacy_location
                )
            )

        elif location and hasattr(location, 'get_filesystem_path'):
            file_path = location.get_filesystem_path(component)
            self.logger.info(
                'Location is only in api: {0!r}'.format(
                    legacy_location
                )
            )

        if file_path is None:
            self.logger.info(
                'Could not determine a valid file system path for: '
                '{0!r}'.format(
                    component_id
                )
            )
            return self.failed

        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            self.logger.info(
                'Directory resolved but non-existing {0!r} and {1!r}:'
                '{0!r}'.format(
                    component_id, file_path
                )
            )
            return self.failed

        if sys.platform == 'win32':
            subprocess.Popen(['start', directory], shell=True)

        elif sys.platform == 'darwin':
            if os.path.exists(file_path):
                # File exists and can be opened with a selection.
                subprocess.Popen(['open', '-R', file_path])

            else:
                subprocess.Popen(['open', directory])

        else:
            subprocess.Popen(['xdg-open', directory])

        return {
            'success': True,
            'message': 'Successfully opened component directory.'
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
        'ftrack_connect:open-component-directory'
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

    action = OpenComponentDirectoryAction(session, logger)
    action.register()
