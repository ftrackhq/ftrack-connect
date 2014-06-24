# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import subprocess
import os
import sys

BUILD_SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

SCSS_BUILD_PATH = os.path.join(
    BUILD_SCRIPT_PATH, 'resource', 'sass'
)

RESOURCE_DESTINATION_PATH = os.path.join(
    BUILD_SCRIPT_PATH, 'source', 'ftrack_connect', 'resource.py'
)

RESOURCE_QRC_PATH = os.path.join(
    BUILD_SCRIPT_PATH, 'resource', 'resource.qrc'
)


def main():
    '''Compile scss to css and generate PySide resouce file.'''
    os.chdir(SCSS_BUILD_PATH)

    compassCommand = 'compass'
    if os.name in ('nt',):
        compassCommand += '.bat'

    code = subprocess.call([compassCommand, 'compile'])

    if code != 0:
        raise SystemExit(code)

    os.chdir(BUILD_SCRIPT_PATH)
    try:
        subprocess.check_call(
            [
                'pyside-rcc',
                '-o',
                RESOURCE_DESTINATION_PATH,
                RESOURCE_QRC_PATH
            ]
        )
    except subprocess.CalledProcessError as error:
        if error.returncode == 2:
            print(
                'Error compiling resource.py using pyside-rcc.'
                'See ftrack connect README for more information.'
            )
        raise SystemExit(error.returncode)

if __name__ == '__main__':
    raise SystemExit(main())
