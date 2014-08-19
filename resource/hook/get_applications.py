# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging
import socket

import ftrack


class GetApplicationsHook(object):
    '''Default get-applications hook.

    The class is callable and return an object with a nested list of
    applications that can be launched on this computer.

    Example:

        dict(
            items=[
                dict(
                   label='My applications',
                   type='heading'
                ),
                dict(
                    label='Maya 2014',
                    applicationIdentifier='maya_2014'
                ),
                dict(
                    label='2D applications',
                    items=[
                        dict(
                            label='Premiere Pro CC 2014',
                            applicationIdentifier='pp_cc_2014'
                        ),
                        dict(
                            label='Premiere Pro CC 2014 with latest publish',
                            applicationIdentifier='pp_cc_2014',
                            applicationData=dict(
                                latest=True
                            )
                        )
                    ]
                )
            ]
        )

    '''

    def __init__(self):
        '''Instantiate the hook and setup logging.'''
        self.logger = logging.getLogger(
            'ftrack.hook.' + self.__class__.__name__
        )

    def __call__(self, event):
        '''Default get-applications hook.

        The hook callback accepts an *event*.

        event['data'] should contain:

            context - Context of request to help guide what applications can be
                      launched.

        '''
        context = event['data']['context']
        items = [
            {
                'label': socket.gethostname(),
                'type': 'heading'
            },
            {
                'label': '2D applications',
                'items': [
                    {
                        'label': 'Premiere pro cc 2014',
                        'applicationIdentifier': 'premiere_pro_cc_2014'
                    },
                    {
                        'label': 'Premiere pro cc 2014 with latest publish',
                        'applicationIdentifier': 'premiere_pro_cc_2014',
                        'applicationData': {
                            'latest': True
                        }
                    }
                ]
            }
        ]

        return {
            'items': items
        }


def register(registry, **kw):
    '''Register hook.'''
    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.get-applications',
        GetApplicationsHook()
    )
