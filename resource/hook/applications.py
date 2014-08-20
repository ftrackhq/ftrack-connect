# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging
import os
import json
import base64
import sys
import subprocess
import collections
import socket
import re

import ftrack


class ApplicationsBase(object):
    '''Base class for application hooks.'''

    def __init__(self):
        '''Instantiate the base class and load applications.'''
        self.logger = logging.getLogger(
            'ftrack.hook.' + self.__class__.__name__
        )

        self.applications = self._getApplications()

    def getApplications(self):
        '''Return list of available application on this host.'''
        return self.applications

    def _findApplications(self, darwin, win32, label, applicationIdentifier):
        '''Return list of found applications based on a relative regexp.

        *darwin* will be used on OSX to search in the /Applications folder.

        *win32* will be used on Windows to search in the PROGRAMFILES folder.

        *label* is the label the application will be given. *label* should be on
        the format "Name of app {version}" where version is the first match in
        the regexp.

        *applicationIdentifier* should be on the form
        "application_name_{version}" where version is the first match in the
        regexp.

        '''
        regex = None
        separator = os.path.sep
        if sys.platform == 'win32':
            top = os.environ['PROGRAMFILES']
            regex = win32

            # Separator must properly excaped before it can be used in regular
            # expression.
            separator = r'\\'
        elif sys.platform == 'darwin':
            top = '/Applications'
            regex = darwin
        else:
            return []

        if not regex:
            return []

        matcher = re.compile(regex)
        pieces = regex.split(separator)
        partialMatchers = map(
            re.compile,
            (separator.join(pieces[:i + 1]) + '' for i in range(len(pieces)))
        )

        applications = []
        level = 0
        for root, folders, files in os.walk(top, topdown=True):
            for index in reversed(range(len(folders))):
                folder = os.path.relpath(
                    os.path.join(root, folders[index]),
                    top
                )

                # Discard folders not matching the regexp.
                if (
                    level >= len(partialMatchers) or
                    not partialMatchers[level].match(folder)
                ):
                    del folders[index]

            # Both files and folders are interesting since OSX applications are
            # folders.
            for filename in folders + files:
                filename = os.path.relpath(os.path.join(root, filename), top)
                match = matcher.match(filename)
                if match:
                    version = match.groups()[0]
                    path = os.path.join(top, filename)
                    applications.append({
                        'applicationIdentifier': applicationIdentifier.format(
                            version=version
                        ),
                        'path': path,
                        'version': version,
                        'label': label.format(version=version)
                    })
            level += 1

        return applications

    def _getApplications(self):
        '''Return a list of applications.

        Applications should be on the form:

            dict(
                'applicationIdentifier': 'name_version',
                'label': 'Name version',
                'path': 'Absolute path to the file',
                'version': 'version of the application'
            )

        '''
        applications = []

        # Add Premiere Pro CC.
        applications.extend(self._findApplications(
            darwin=(r'Adobe Premiere Pro CC ([\d]{4})/'
                    r'Adobe Premiere Pro CC \1.app$'),
            win32=r'Adobe\\Adobe Premiere Pro CC ([\d]{4})\\Adobe Premiere Pro.exe$',
            label='Premiere Pro CC {version}',
            applicationIdentifier='premiere_pro_cc_{version}'
        ))

        # Add Nuke.
        applications.extend(self._findApplications(
            darwin=r'Nuke(.{1,10})/Nuke\1.app$',
            win32=r'The Foundry\\Nuke(.{1,10})\\nuke.exe$',
            label='Nuke {version}',
            applicationIdentifier='nuke_{version}'
        ))

        # Add Maya.
        applications.extend(self._findApplications(
            darwin=r'Autodesk/maya([\d]{1,4})/Maya.app$',
            win32=r'Autodesk\\Maya([\d]{1,4})\\bin\\maya.exe$',
            label='Maya {version}',
            applicationIdentifier='maya_{version}'
        ))

        # Add HIEROPLAYER.
        applications.extend(self._findApplications(
            darwin=r'HieroPlayer(.{1,10})/HieroPlayer\1.app$',
            win32=r'The Foundry\\HieroPlayer(.{1,10})\\hieroplayer.exe$',
            label='HieroPlayer {version}',
            applicationIdentifier='hieroplayer_{version}'
        ))

        return applications


class GetApplicationsHook(ApplicationsBase):
    '''Default get-applications hook.

    The class is callable and return an object with a nested list of
    applications that can be launched on this computer.

    Example:

        dict(
            items=[
                dict(
                   label='My applications',
                   type='heading'
                ),
                dict(
                    label='Maya 2014',
                    applicationIdentifier='maya_2014'
                ),
                dict(
                   type='separator'
                ),
                dict(
                    label='2D applications',
                    items=[
                        dict(
                            label='Premiere Pro CC 2014',
                            applicationIdentifier='pp_cc_2014'
                        ),
                        dict(
                            label='Premiere Pro CC 2014 with latest publish',
                            applicationIdentifier='pp_cc_2014',
                            applicationData=dict(
                                latest=True
                            )
                        )
                    ]
                )
            ]
        )

    '''

    def __init__(self):
        '''Instantiate the hook and setup logging.'''
        self.logger = logging.getLogger(
            'ftrack.hook.' + self.__class__.__name__
        )

        super(GetApplicationsHook, self).__init__()

    def __call__(self, event):
        '''Default get-applications hook.

        The hook callback accepts an *event*.

        event['data'] should contain:

            context - Context of request to help guide what applications can be
                      launched.

        '''
        context = event['data']['context']
        items = [
            {
                'label': socket.gethostname(),
                'type': 'heading'
            }
        ]
        applications = self.getApplications()
        applications = sorted(
            applications, key=lambda application: application['label']
        )
        for application in applications:
            items.append({
                'applicationIdentifier': application['applicationIdentifier'],
                'label': application['label']
            })

        return {
            'items': items
        }


class LaunchApplicationHook(ApplicationsBase):
    '''Default launch-application hook.

    The class is callable and accepts information on the event, the application
    identifier and the context it is launched from. When launching the
    application it will configure the environment by copying environment
    variables such as FTRACK_SERVER, FTRACK_APIKEY, etc. from the current
    environment.

    Launched applications are started detached so exiting ftrack connect will
    not close launched applications.

    When called the hook will return information on if the launch was successful
    and a human readable message.

    '''

    def __init__(self):
        '''Instantiate the hook and setup logging.'''
        self.logger = logging.getLogger(
            'ftrack.hook.' + self.__class__.__name__
        )

        super(LaunchApplicationHook, self).__init__()

    def __call__(self, event):
        '''Default launch-application hook.

        The hook callback accepts an *event*.

        event['data'] should contain:

            applicationIdentifier - The identifier of the application to launch.
            context - Context of request to help guide how to launch the
                      application.
            applicationData - Is passed with the applicationIdentifier and can
                              be used to provide additional information about
                              how the application should be launched.

        '''
        applicationIdentifier = event['data']['applicationIdentifier']
        context = event['data']['context']
        applicationData = event['data']['applicationData']

        command = self._getApplicationLaunchCommand(
            applicationIdentifier,
            context,
            applicationData
        )
        environment = self._getApplicationEnvironment({
            'data': event['data'],
            'source': event['source']
        })

        success = True
        message = '{0} application started.'.format(applicationIdentifier)

        # Environment must contain only strings.
        self._conformEnvironment(environment)

        try:
            options = dict(
                env=environment,
                close_fds=True
            )

            if sys.platform == 'win32':
                # Ensure subprocess is detached so closing connect will not also
                # close launched applications.
                options['creationflags'] = subprocess.CREATE_NEW_CONSOLE
            else:
                options['preexec_fn'] = os.setsid

            self.logger.debug(
                'Launching {0} with options {1}'.format(command, options)
            )
            process = subprocess.Popen(command, **options)

        except (OSError, TypeError):
            self.logger.exception(
                '{0} application could not be started with command "{1}".'
                .format(applicationIdentifier, command)
            )

            success = False
            message = '{0} application could not be started.'.format(
                applicationIdentifier
            )

        else:
            self.logger.debug(
                '{0} application started. (pid={1})'.format(
                    applicationIdentifier, process.pid
                )
            )

        return {
            'success': success,
            'message': message
        }

    def _conformEnvironment(self, mapping):
        '''Ensure all entries in *mapping* are strings.

        .. note::

            The *mapping* is modified in place.

        '''
        if not isinstance(mapping, collections.MutableMapping):
            return

        for key, value in mapping.items():
            if isinstance(value, collections.Mapping):
                self._conformEnvironment(value)
            else:
                value = str(value)

            del mapping[key]
            mapping[str(key)] = value

    def _getApplicationLaunchCommand(self, applicationIdentifier, context,
                                     applicationData):
        '''Return application command based on OS and *applicationIdentifier*,
        *context* and *applicationData*.

        *applicationIdentifier* is a unique identifier for each application.

        *context* is the entity the application should be started for.

        *applicationData* is passed with the *applicationIdentifier* and can be
        used to provide additional information about how the application should
        be launched.

        '''
        command = None
        applicationConfig = None
        for application in self.getApplications():
            if application['applicationIdentifier'] == applicationIdentifier:
                applicationConfig = application

            elif (
                applicationIdentifier == 'hieroplayer' and
                application['applicationIdentifier'].startswith('hieroplayer')
            ):
                applicationConfig = application

        if applicationConfig:
            if sys.platform == 'win32':
                command = [
                    applicationConfig['path']
                ]

            elif sys.platform == 'darwin':
                command = [
                    'open',
                    applicationConfig['path']
                ]
        else:
            self.logger.warning(
                ('Unable to find launch command for {0} on this '
                 'platform.').format(
                    applicationIdentifier
                )
            )

        # Figure out if the command should be started with the file path of
        # the latest published version.
        if command is not None and applicationData is not None:
            selection = context.get('selection')
            if selection and applicationData.get('latest', False):
                entity = selection[0]
                entityId = entity['entityId']
                entityType = entity['entityType']

                # Get a list of valid versions based on entityType.
                versions = []
                if entityType == 'task':
                    task = ftrack.Task(entityId)
                    versions = task.getAssetVersions()
                elif entityType == 'assetversion':
                    versions = [ftrack.AssetVersion(entityId)]

                # Find the latest version that can be opened.
                lastDate = None
                path = None
                for version in versions:
                    for component in version.getComponents():
                        fileSystemPath = component.getFilesystemPath()
                        if fileSystemPath.endswith('.prproj'):
                            if (
                                lastDate is None or
                                version.getDate() > lastDate
                            ):
                                path = fileSystemPath
                                lastDate = version.getDate()

                if path is not None:
                    command.append(path)

        return command

    def _getApplicationEnvironment(self, eventData=None):
        '''Return list of environment variables based on *context*.

        The list will also contain the variables available in the current
        session.

        '''
        # Copy appropitate environment variables to new environment.
        environment = {}

        if sys.platform == 'win32':
            # Required for launching executables on Windows.
            environment.setdefault('SystemRoot', os.environ.get('SystemRoot'))
            environment.setdefault('SystemDrive', os.environ.get('SystemDrive'))

            # Many applications also need access to temporary storage and other
            # executable.
            environment.setdefault('PATH', os.environ.get('PATH'))
            environment.setdefault('TMP', os.environ.get('TMP'))

        environment.setdefault(
            'FTRACK_SERVER', os.environ.get('FTRACK_SERVER')
        )
        environment.setdefault(
            'FTRACK_PROXY', os.environ.get('FTRACK_PROXY')
        )
        environment.setdefault(
            'FTRACK_APIKEY', os.environ.get('FTRACK_APIKEY')
        )
        environment.setdefault(
            'LOGNAME', os.environ.get('LOGNAME')
        )

        environment.setdefault(
            'FTRACK_EVENT_SERVER',
            ftrack.EVENT_HUB.getServerUrl()
        )

        environment.setdefault(
            'FTRACK_LOCATION_PLUGIN_PATH',
            os.environ.get('FTRACK_LOCATION_PLUGIN_PATH')
        )

        # Add discovered ftrack API to PYTHONPATH.
        environment.setdefault(
            'PYTHONPATH', os.path.dirname(ftrack.__file__)
        )

        # Add ftrack connect event to environment.
        if eventData is not None:
            try:
                applicationContext = base64.b64encode(
                    json.dumps(
                        eventData
                    )
                )
            except (TypeError, ValueError):
                self.logger.exception(
                    'The eventData could not be converted correctly. {0}'
                    .format(eventData)
                )
            else:
                environment['FTRACK_CONNECT_EVENT'] = applicationContext

        self.logger.debug('Setting new environment to {0}'.format(environment))

        return environment


def register(registry, **kw):
    '''Register hooks.'''
    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.get-applications',
        GetApplicationsHook()
    )

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.launch-application',
        LaunchApplicationHook()
    )
