# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import getpass
import logging

import ftrack
import ftrack_connect.application

ACTION_IDENTIFIER = 'ftrack-connect-launch-applications-action'


class DiscoverApplicationsHook(object):
    '''Default action.discover hook.

    The class is callable and return an object with a list of actions that can
    be launched on this computer.

    Example:

        dict(
            items=[
                dict(
                    actionIdentifier='ftrack-connect-launch-applications-action',
                    label='Maya 2014',
                    actionData=dict(
                        applicationIdentifier='maya_2014'
                    )
                ),
                dict(
                    actionIdentifier='ftrack-connect-launch-applications-action',
                    label='Premiere Pro CC 2014',
                    actionData=dict(
                        applicationIdentifier='pp_cc_2014'
                    )
                ),
                dict(
                    actionIdentifier='ftrack-connect-launch-applications-action',
                    label='Premiere Pro CC 2014 with latest publish',
                    actionData=dict(
                        latest=True,
                        applicationIdentifier='pp_cc_2014'
                    )
                )
            ]
        )

    '''

    identifier = ACTION_IDENTIFIER

    def __init__(self, applicationStore):
        '''Instantiate the hook and setup logging.'''
        super(DiscoverApplicationsHook, self).__init__()
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self.applicationStore = applicationStore

    def __call__(self, event):
        '''Default action.discover hook.

        The hook callback accepts an *event*.

        event['data'] should contain:

            context - Context of request to help guide what applications can be
                      launched.

        '''
        context = event['data']['context']

        # If selection contains more than one item return early since
        # applications cannot be started for multiple items or if the
        # selected item is not a "task".
        selection = context.get('selection', [])
        if len(selection) != 1 or selection[0].get('entityType') != 'task':
            return

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
                'actionData': {
                    'applicationIdentifier': applicationIdentifier
                }
            })

            if applicationIdentifier.startswith('premiere_pro_cc'):
                items.append({
                    'actionIdentifier': self.identifier,
                    'label': '{label} with latest version'.format(
                        label=label
                    ),
                    'icon': application.get('icon', 'default'),
                    'actionData': {
                        'launchWithLatest': True,
                        'applicationIdentifier': applicationIdentifier
                    }
                })

        return {
            'items': items
        }


class LaunchApplicationHook(object):

    def __init__(self, launcher):
        '''Initialise hook with *launcher*.'''
        super(LaunchApplicationHook, self).__init__()
        self.logger = logging.getLogger(
            'ftrack.hook.' + self.__class__.__name__
        )
        self.launcher = launcher

    def __call__(self, event):
        '''Handle *event*.

        event['data'] should contain:

            context - Context of request to help guide how to launch the
                      application.
            actionData - Is passed and should contain the applicationIdentifier
                         and other values that can be used to provide
                         additional information about how the application
                         should be launched.
        '''
        applicationIdentifier = (
            event['data']['actionData']['applicationIdentifier']
        )
        context = {}
        context.update(event['data']['context'])
        context.update(event['data']['actionData'])
        context['source'] = event['source']

        self.launcher.launch(
            applicationIdentifier, context
        )


def register(registry, **kw):
    '''Register hooks.'''
    applicationStore = ftrack_connect.application.ApplicationStore()

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.action.discover and source.user.username={0}'.format(
            getpass.getuser()
        ),
        DiscoverApplicationsHook(applicationStore)
    )

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.action.launch and source.user.username={0} '
        'and data.actionIdentifier={1}'.format(
            getpass.getuser(), ACTION_IDENTIFIER
        ),
        LaunchApplicationHook(
            ftrack_connect.application.ApplicationLauncher(
                applicationStore
            )
        )
    )
