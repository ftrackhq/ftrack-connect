# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import subprocess
import os

BUILD_SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

SCSS_BUILD_PATH = os.path.join(
    BUILD_SCRIPT_PATH, 'sass'
)

RESOURCE_DEST_PATH = os.path.join(
    BUILD_SCRIPT_PATH, '..', 'source', 'ftrack_connect'
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
            '{0}/resource.py'.format(RESOURCE_DEST_PATH),
            '{0}/resource.qrc'.format(BUILD_SCRIPT_PATH)
        ]
    )


if __name__ == '__main__':
    main()
