# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

ROOT_FOLDER = os.path.dirname(
    os.path.realpath(__file__)
)

DIST_FOLDER = os.path.join(
    ROOT_FOLDER, 'dist', 'ftrack-connect'
)

RESOURCE_FOLDER = os.path.join(
    ROOT_FOLDER, 'source', 'ftrack_connect', 'resources'
)


class PyTest(TestCommand):
    '''Pytest command.'''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        '''Import pytest and run.'''
        import pytest
        raise SystemExit(pytest.main(self.test_args))


readme_path = os.path.join(os.path.dirname(__file__), 'README.rst')
packages_path = os.path.join(os.path.dirname(__file__), 'source')

PY2APP_OPTIONS = {
    'argv_emulation': False,
    'includes': [
        'PySide.QtCore',
        'PySide.QtGui',
    ],
    'iconfile': 'logo.icns',
    'use_pythonpath': True,
    'dist_dir': DIST_FOLDER,
    'plist': {
        'LSUIElement': True
    }
}

setup(
    name='ftrack-connect',
    version='0.1.0',
    description='Core for ftrack connect.',
    long_description=open(readme_path).read(),
    keywords='ftrack, connect, publish',
    url='https://bitbucket.org/ftrack/ftrack-connect',
    author='ftrack',
    author_email='support@ftrack.com',
    packages=find_packages(packages_path),
    package_dir={
        '': 'source'
    },
    install_requires=[
    ],
    tests_require=['pytest >= 2.3.5'],
    cmdclass={
        'test': PyTest
    },
    app=['source/ftrack_connect/__main__.py'],
    options={
        'py2app': PY2APP_OPTIONS
    },
    data_files=[
        ('', [RESOURCE_FOLDER]),
    ],
    setup_requires=['py2app'],
    zip_safe=False
)
