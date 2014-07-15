# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging
import os
import json
import base64
import sys
import subprocess

import ftrack

log = logging.getLogger(__name__)


import collections


def conformEnvironment(mapping):
    '''Ensure all entries in *mapping* are strings.

    .. note::

        The *mapping* is modified in place.

    '''
    if not isinstance(mapping, collections.MutableMapping):
        return

    for key, value in mapping.items():
        if isinstance(value, collections.Mapping):
            conformEnvironment(value)
        else:
            value = str(value)

        del mapping[key]
        mapping[str(key)] = value


def _getApplicationLaunchCommand(applicationIdentifier):
    '''Return application command based on OS and *applicationIdentifier*.'''
    command = None

    if applicationIdentifier == 'hieroplayer':

        if sys.platform == 'win32':
            # HieroPlayer application command when running Windows.
            command = [
                r'C:\Program Files\The Foundry\HieroPlayer1.8v2\hieroplayer.exe'
            ]

        elif sys.platform == 'darwin':
            # HieroPlayer application command when running OSX.
            command = [
                '/Applications/HieroPlayer1.8v1/HieroPlayer1.8v1.app'
                '/Contents/MacOS/HieroPlayer1.8v1'
            ]

        else:
            # HieroPlayer application command when running something else.
            pass

    return command


def _getApplicationEnvironment(context=None):
    '''Return list of environment variables based on *context*.

    The list will also contain the variables available in the current session.

    '''
    # Copy entire parent environment.
    environment = os.environ.copy()

    # Might be good to remove some keys from the new environment.
    # Such as FTRACK_TOPIC_PLUGIN_PATH.

    # Add ftrack connect event to environment.
    if context is not None:
        try:
            applicationContext = base64.b64encode(
                json.dumps(
                    context
                )
            )
        except:
            log.exception(
                'Context could not be converted correctly. {0}'.format(context)
            )
        else:
            environment['FTRACK_CONNECT_EVENT'] = applicationContext

    log.debug('Setting new environment to {0}'.format(environment))

    return environment


def callback(event, applicationIdentifier, context, **kw):
    '''Default launch-application hook.

    The hook callback accepts *event*, the *applicationIdentifier* and the
    application *context*.

    '''
    command = _getApplicationLaunchCommand(applicationIdentifier)
    environment = _getApplicationEnvironment(applicationIdentifier)

    success = True
    message = 'Application started.'

    # Environment must contain only strings.
    conformEnvironment(environment)

    try:
        process = subprocess.Popen(command, env=environment)
    except (OSError, TypeError):
        log.exception(
            'Application could not be started with command "{0}".'.format(
                command
            )
        )
        success = False
        message = 'Application could not be started.'

    return {
        'success': success,
        'message': message
    }


def register(registry, **kw):
    '''Register hook.'''
    ftrack.TOPICS.subscribe(
        'ftrack.launch-application',
        callback,
        callbackID='ftrack-connect-default-hook'
    )
