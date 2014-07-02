# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import subprocess
import re

from setuptools import setup, find_packages, Command
from distutils.command.build import build as BuildCommand
from setuptools.command.install import install as InstallCommand
from distutils.command.clean import clean as CleanCommand
from setuptools.command.test import test as TestCommand
import distutils.dir_util
import distutils


ROOT_PATH = os.path.dirname(
    os.path.realpath(__file__)
)

RESOURCE_PATH = os.path.join(
    ROOT_PATH, 'resource'
)

SOURCE_PATH = os.path.join(
    ROOT_PATH, 'source'
)

DISTRIBUTION_PATH = os.path.join(
    ROOT_PATH, 'dist'
)

RESOURCE_TARGET_PATH = os.path.join(
    SOURCE_PATH, 'ftrack_connect', 'resource.py'
)

README_PATH = os.path.join(os.path.dirname(__file__), 'README.rst')

PACKAGES_PATH = os.path.join(os.path.dirname(__file__), 'source')


# Read version from source.
with open(os.path.join(
    SOURCE_PATH, 'ftrack_connect', '_version.py'
)) as _version_file:
    VERSION = re.match(
        r'.*__version__ = \'(.*?)\'', _version_file.read(), re.DOTALL
    ).group(1)


# Custom commands.
class BuildResources(Command):
    '''Build additional resources.'''

    user_options = []

    def initialize_options(self):
        '''Configure default options.'''

    def finalize_options(self):
        '''Finalize options to be used.'''
        self.sass_path = os.path.join(RESOURCE_PATH, 'sass')
        self.css_path = RESOURCE_PATH
        self.resource_source_path = os.path.join(
            RESOURCE_PATH, 'resource.qrc'
        )
        self.resource_target_path = RESOURCE_TARGET_PATH

    def run(self):
        '''Run build.'''
        try:
            import scss
        except ImportError:
            raise RuntimeError(
                'Error compiling sass files. Could not import "scss". '
                'Check you have the pyScss Python package installed.'
            )

        compiler = scss.Scss(
            search_paths=[self.sass_path]
        )

        themes = [
            'style_light',
            'style_dark'
        ]
        for theme in themes:
            scss_source = os.path.join(self.sass_path, '{0}.scss'.format(theme))
            css_target = os.path.join(self.css_path, '{0}.css'.format(theme))

            compiled = compiler.compile(
                scss_file=scss_source
            )
            with open(css_target, 'w') as file_handle:
                file_handle.write(compiled)
                print('Compiled {0}'.format(css_target))

        try:
            subprocess.check_call([
                'pyside-rcc',
                '-o',
                self.resource_target_path,
                self.resource_source_path
            ])
        except (subprocess.CalledProcessError, OSError) as error:
            raise RuntimeError(
                'Error compiling resource.py using pyside-rcc. Possibly '
                'pyside-rcc could not be found. You might need to manually add '
                'it to your PATH. See README for more information.'
            )


class Build(BuildCommand):
    '''Custom build to pre-build resources.'''

    def initialize_options(self):
        '''Configure default options.'''
        BuildCommand.initialize_options(self)

        # Required for cx_freeze.
        self.build_exe = None

    def run(self):
        '''Run build ensuring build_resources called first.'''
        self.run_command('build_resources')
        BuildCommand.run(self)


class Install(InstallCommand):
    '''Custom install to pre-build resources.'''

    def do_egg_install(self):
        '''Run install ensuring build_resources called first.

        .. note::

            `do_egg_install` used rather than `run` as sometimes `run` is not
            called at all by setuptools.

        '''
        self.run_command('build_resources')
        InstallCommand.do_egg_install(self)


class Clean(CleanCommand):
    '''Custom clean to remove built resources and distributions.'''

    def run(self):
        '''Run clean.'''
        relative_resource_path = os.path.relpath(
            RESOURCE_TARGET_PATH, ROOT_PATH
        )
        if os.path.exists(relative_resource_path):
            os.remove(relative_resource_path)
        else:
            distutils.log.warn(
                '\'{0}\' does not exist -- can\'t clean it'
                .format(relative_resource_path)
            )

        if self.all:
            relative_distribution_path = os.path.relpath(
                DISTRIBUTION_PATH, ROOT_PATH
            )
            if os.path.exists(relative_distribution_path):
                distutils.dir_util.remove_tree(
                    relative_distribution_path, dry_run=self.dry_run
                )
            else:
                distutils.log.warn(
                    '\'{0}\' does not exist -- can\'t clean it'
                    .format(relative_distribution_path)
                )

        CleanCommand.run(self)


class PyTest(TestCommand):
    '''Pytest command.'''

    def finalize_options(self):
        '''Finalize options to be used.'''
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        '''Import pytest and run.'''
        import pytest
        raise SystemExit(pytest.main(self.test_args))


# General configuration.
configuration = dict(
    name='ftrack-connect',
    version=VERSION,
    description='Core for ftrack connect.',
    long_description=open(README_PATH).read(),
    keywords='ftrack, connect, publish',
    url='https://bitbucket.org/ftrack/ftrack-connect',
    author='ftrack',
    author_email='support@ftrack.com',
    license='Apache License (2.0)',
    packages=find_packages(PACKAGES_PATH),
    package_dir={
        '': 'source'
    },
    install_requires=[
        'PySide >= 1.2.2, < 2',
        'Riffle >= 0.1.0, < 2'
    ],
    tests_require=['pytest >= 2.3.5'],
    cmdclass={
        'build': Build,
        'build_resources': BuildResources,
        'install': Install,
        'clean': Clean,
        'test': PyTest
    },
    options={},
    data_files=[
    ],
    setup_requires=[
        'pyScss >= 1.2.0, < 2'
    ]
)


# Call main setup.
setup(**configuration)
