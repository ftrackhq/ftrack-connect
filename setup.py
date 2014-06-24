# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys
import os
import subprocess

from setuptools import setup, find_packages, Command
from distutils.command.build import build as BuildCommand
from setuptools.command.install import install as InstallCommand
from setuptools.command.test import test as TestCommand


ROOT_FOLDER = os.path.dirname(
    os.path.realpath(__file__)
)

RESOURCE_FOLDER = os.path.join(
    ROOT_FOLDER, 'resource'
)

DIST_FOLDER = os.path.join(
    ROOT_FOLDER, 'dist', 'ftrack-connect'
)


class BuildResources(Command):
    '''Build additional resources.'''

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        self.sass_path = os.path.join(RESOURCE_FOLDER, 'sass')
        self.css_path = RESOURCE_FOLDER
        self.resource_source_path = os.path.join(
            RESOURCE_FOLDER, 'resource.qrc'
        )
        self.resource_target_path = os.path.join(
            ROOT_FOLDER, 'source', 'ftrack_connect', 'resource.py'
        )

    def run(self):
        '''Run build.'''
        try:
            import scss
        except ImportError:
            print('Error compiling sass files. Could not import "scss". '
                  'Check you have the pyScss Python package installed.')
            raise SystemExit()

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
        except subprocess.CalledProcessError as error:
            if error.returncode == 2:
                print(
                    'Error compiling resource.py using pyside-rcc.'
                    'See ftrack connect README for more information.'
                )
            raise SystemExit(error.returncode)


class Build(BuildCommand):
    '''Custom build to pre-build resources.'''

    def run(self):
        self.run_command('build_resources')
        BuildCommand.run(self)


class Install(InstallCommand):
    '''Custom install to pre-build resources.'''

    def do_egg_install(self):
        self.run_command('build_resources')
        InstallCommand.do_egg_install(self)


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
options = {}
setup_requires = [
    'pyScss >= 1.2.0, < 2'
]


# Platform specific configuration.
if sys.platform.lower() == 'darwin':
    setup_requires.append('py2app')

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

    options['py2app'] = PY2APP_OPTIONS


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
        'build': Build,
        'build_resources': BuildResources,
        'install': Install,
        'test': PyTest
    },
    app=['source/ftrack_connect/__main__.py'],
    options=options,
    data_files=[
    ],
    setup_requires=setup_requires,
    zip_safe=False
)
