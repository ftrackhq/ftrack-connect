# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import logging
import sys
import pprint

import ftrack
import ftrack_connect.application


class HoudiniAction(object):
    '''Launch Houdini action.'''

    # Unique action identifier.
    identifier = 'my-houdini-launch-action'

    def __init__(self, applicationStore, launcher):
        '''Initialise action with *applicationStore* and *launcher*.

        *applicationStore* should be an instance of
        :class:`ftrack_connect.application.ApplicationStore`.

        *launcher* should be an instance of
        :class:`ftrack_connect.application.ApplicationLauncher`.

        '''
        super(HoudiniAction, self).__init__()

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self.applicationStore = applicationStore
        self.launcher = launcher

        if self.identifier is None:
            raise ValueError('The action must be given an identifier.')

    def register(self):
        '''Register action to respond to discover and launch events.'''
        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.action.discover',
            self.discover
        )

        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.action.launch and data.actionIdentifier={0}'.format(
                self.identifier
            ),
            self.launch
        )

    def discover(self, event):
        '''Return available actions based on *event*.

        Each action should contain

            actionIdentifier - Unique identifier for the action
            label - Nice name to display in ftrack
            icon(optional) - predefined icon or URL to an image
            applicationIdentifier - Unique identifier to identify application
                                    in store.

        '''
        items = []
        applications = self.applicationStore.applications
        applications = sorted(
            applications, key=lambda application: application['label']
        )

        for application in applications:
            applicationIdentifier = application['identifier']
            label = application['label']
            items.append({
                'actionIdentifier': self.identifier,
                'label': label,
                'icon': application.get('icon', 'default'),
                'applicationIdentifier': applicationIdentifier
            })

        return {
            'items': items
        }

    def launch(self, event):
        '''Callback method for Houdini action.'''
        applicationIdentifier = (
            event['data']['applicationIdentifier']
        )

        context = event['data'].copy()

        return self.launcher.launch(
            applicationIdentifier, context
        )


class ApplicationStore(ftrack_connect.application.ApplicationStore):
    '''Store used to find and keep track of available applications.'''

    def _discoverApplications(self):
        '''Return a list of applications that can be launched from this host.
        '''
        applications = []

        if sys.platform == 'darwin':
            prefix = ['/', 'Applications']

            applications.extend(self._searchFilesystem(
                expression=prefix + [
                    'Houdini*', 'Houdini.app'
                ],
                label='Houdini {version}',
                applicationIdentifier='houdini_{version}'
            ))

        elif sys.platform == 'win32':
            prefix = ['C:\\', 'Program Files.*']

            applications.extend(self._searchFilesystem(
                expression=(
                    prefix +
                    ['Side Effects Software', 'Houdini*', 'bin', 'houdini.exe']
                ),
                label='Houdini {version}',
                applicationIdentifier='houdini_{version}'
            ))

        self.logger.debug(
            'Discovered applications:\n{0}'.format(
                pprint.pformat(applications)
            )
        )

        return applications


class ApplicationLauncher(ftrack_connect.application.ApplicationLauncher):
    '''Custom launcher to modify environment before launch.'''

    def _getApplicationEnvironment(
        self, application, context=None
    ):
        '''Override to modify environment before launch.'''

        # Make sure to call super to retrieve original environment
        # which contains the selection and ftrack API.
        environment = super(
            ApplicationLauncher, self
        )._getApplicationEnvironment(application, context)

        # Append or Prepend values to the environment.
        # Note that if you assign manually you will overwrite any
        # existing values on that variable.

        # Add my custom path to the HOUDINI_SCRIPT_PATH.
        environment = ftrack_connect.application.appendPath(
            'path/to/my/custom/scripts',
            'HOUDINI_SCRIPT_PATH',
            environment
        )

        # Set an internal user id of some kind.
        environment = ftrack_connect.application.appendPath(
            'my-unique-user-id-123',
            'STUDIO_SPECIFIC_USERID',
            environment
        )

        # Always return the environment at the end.
        return environment


def register(registry, **kw):
    '''Register hooks.'''

    # Validate that registry is the correct ftrack.Registry. If not,
    # assume that register is being called with another purpose or from a
    # new or incompatible API and return without doing anything.
    if registry is not ftrack.EVENT_HANDLERS:
        # Exit to avoid registering this plugin again.
        return

    # Create store containing applications.
    applicationStore = ApplicationStore()

    # Create a launcher with the store containing applications.
    launcher = ApplicationLauncher(
        applicationStore
    )

    # Create action and register to respond to discover and launch actions.
    action = HoudiniAction(applicationStore, launcher)
    action.register()
