# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging
import socket

import ftrack


class GetApplicationsHook(object):
    '''Default get-applications hook.

    The class is callable and return an object with  nested list of applications that can be
    launched on this computer.

    Example:



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
        applications = [
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
            'session': socket.gethostname(),
            'applications': applications
        }


def register(registry, **kw):
    '''Register hook.'''
    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.get-applications',
        GetApplicationsHook()
    )
