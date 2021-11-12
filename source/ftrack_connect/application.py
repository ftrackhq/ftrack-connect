# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

def prependPath(path, key, environment):
    '''Prepend *path* to *key* in *environment*.'''
    try:
        environment[key] = (
            os.pathsep.join([
                path, environment[key]
            ])
        )
    except KeyError:
        environment[key] = path

    return environment


def appendPath(path, key, environment):
    '''Append *path* to *key* in *environment*.'''
    try:
        environment[key] = (
            os.pathsep.join([
                environment[key], path
            ])
        )
    except KeyError:
        environment[key] = path

    return environment
