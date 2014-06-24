# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import subprocess
import os

BUILD_SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

SCSS_BUILD_PATH = os.path.join(
    BUILD_SCRIPT_PATH, 'sass'
)

RESOURCE_DESTINATION_PATH = os.path.join(
    BUILD_SCRIPT_PATH, '..', 'source', 'ftrack_connect', 'resource.py'
)

RESOURCE_QRC_PATH = os.path.join(
    BUILD_SCRIPT_PATH, 'resource.qrc'
)


def main():
    '''Compile scss to css and generate PySide resouce file.'''
    os.chdir(SCSS_BUILD_PATH)
    subprocess.call(['compass', 'compile'])

    os.chdir(BUILD_SCRIPT_PATH)
    subprocess.call(
        [
            'pyside-rcc',
            '-o',
            RESOURCE_DESTINATION_PATH,
            RESOURCE_QRC_PATH
        ]
    )


if __name__ == '__main__':
    raise SystemExit(main())
