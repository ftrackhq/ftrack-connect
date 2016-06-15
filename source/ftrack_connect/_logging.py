# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import os
from logging import *
from logging import config
import appdirs


def getLogFilePath():
    user_data_dir = appdirs.user_data_dir('ftrack-connect', 'ftrack')
    log_directory = os.path.join(user_data_dir, 'log')

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    logfile = os.path.join(log_directory, 'ftrack.log')

    return logfile


LOGGING_SETTINGS = {
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
            'filename': getLogFilePath(),
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
            'handlers': ['console', 'file']
        },
        'ftrack_api': {
            'level': 'INFO',
        },
        'FTrackCore': {
            'level': 'INFO',
        }
    }
}

# Set default logging settings.
config.dictConfig(LOGGING_SETTINGS)

# Redirect warnings to log so can be debugged.
captureWarnings(True)
