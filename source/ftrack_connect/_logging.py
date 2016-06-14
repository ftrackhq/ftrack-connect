# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import os
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
from logging import getLogger as _getLogger
from logging import getLevelName, basicConfig
from logging import config as _config
import appdirs

user_data_dir = appdirs.user_data_dir('ftrack-connect', 'ftrack')
log_directory = os.path.join(user_data_dir, 'log')
if not os.path.exists(log_directory):
    os.makedirs(log_directory)


logfile = os.path.join(log_directory, 'ftrack.log')


DEFAULT_LOG_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',
            'formatter': 'file',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'file',
            'filename': logfile,
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 5,
        },

    },
    'formatters': {
        'file': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': True
        },
        'ftrack_api': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': True
        },
        'FTrackCore': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': True
        }
    }
}

_config.dictConfig(DEFAULT_LOG_SETTINGS)


def getLogger(name=None):
    return _getLogger(name)


log = getLogger()
log.warning('Saving log file : %s' % logfile)
