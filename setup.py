# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


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

setup(
    name='ftrack-connect',
    version='0.1.0',
    description='Core for ftrack connect.',
    long_description=open(readme_path).read(),
    keywords='ftrack, publish',
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
    zip_safe=False
)
