# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack


class ConnectError(Exception):
    '''Base ftrack connect error.'''
    pass


class NotUniqueError(ConnectError):
    '''Raise when something that should be unique is not.'''
