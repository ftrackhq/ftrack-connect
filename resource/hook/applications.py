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


class ApplicationsStore(object):
    '''Class used as a store to provide available applications on this host.'''

    def __init__(self):
        '''Instantiate store and load applications.'''
        self.applications = self._getApplications()

    def getApplications(self):
        '''Return list of available applications.'''
        return self.applications

    def _findApplications(self, expression, top, label, applicationIdentifier):
        '''Return list of found applications based on a relative regexp.

        *expression* should be a regular expression matching the path to an
        application together with the prefix *top*.

        *top* should be a file path to a folder where the *expression* matching
        should begin. On OSX *top* would often be '/Applications'.

        *label* is the label the application will be given. *label* should be on
        the format "Name of app {version}" where version is the first match in
        the regexp.

        *applicationIdentifier* should be on the form
        "application_name_{version}" where version is the first match in the
        regexp.

        '''
        separator = os.sep

        # Joined paths will not match regular expression unless separator is
        # escaped on windows.
        if sys.platform == 'win32':
            separator = re.escape(os.sep)

        matcher = re.compile(expression)
        pieces = expression.split(separator)
        partialMatchers = map(
            re.compile,
            (separator.join(pieces[:i + 1]) for i in range(len(pieces)))
        )

        applications = []
        level = 0
        for root, folders, files in os.walk(top, topdown=True):
            for index in reversed(range(len(folders))):
                folder = os.path.relpath(
                    os.path.join(root, folders[index]),
                    top
                )

                # Discard folders not matching the partial regular expression.
                if (
                    level >= len(partialMatchers) or
                    not partialMatchers[level].match(folder)
                ):
                    del folders[index]

            # Both files and folders are interesting since OSX applications are
            # folders.
            for filename in folders + files:
                relativeApplicationPath = os.path.relpath(
                    os.path.join(root, filename),
                    top
                )
                match = matcher.match(relativeApplicationPath)
                if match:
                    version = match.groups()[0]
                    path = os.path.join(top, relativeApplicationPath)
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
        '''Return a list of applications that can be launched from this host.

        An application should be on the form:

            dict(
                'applicationIdentifier': 'name_version',
                'label': 'Name version',
                'path': 'Absolute path to the file',
                'version': 'version of the application'
            )

        '''
        applications = []

        if sys.platform == 'darwin':

            applications.extend(self._findApplications(
                expression=(
                    r'Adobe Premiere Pro CC ([\d]{4})/'
                    r'Adobe Premiere Pro CC \1.app$'
                ),
                top='/Applications',
                label='Premiere Pro CC {version}',
                applicationIdentifier='premiere_pro_cc_{version}'
            ))

            applications.extend(self._findApplications(
                expression=r'Nuke(.{1,10})/Nuke\1.app$',
                top='/Applications',
                label='Nuke {version}',
                applicationIdentifier='nuke_{version}'
            ))

            applications.extend(self._findApplications(
                expression=r'Autodesk/maya([\d]{1,4})/Maya.app$',
                top='/Applications',
                label='Maya {version}',
                applicationIdentifier='maya_{version}'
            ))

            applications.extend(self._findApplications(
                expression=r'HieroPlayer(.{1,10})/HieroPlayer\1.app$',
                top='/Applications',
                label='HieroPlayer {version}',
                applicationIdentifier='hieroplayer_{version}'
            ))

        elif sys.platform == 'win32':

            applications.extend(self._findApplications(
                expression=(
                    r'Adobe\\'
                    r'Adobe Premiere Pro CC ([\d]{4})\\'
                    r'Adobe Premiere Pro.exe$'
                ),
                top=os.environ['PROGRAMFILES'],
                label='Premiere Pro CC {version}',
                applicationIdentifier='premiere_pro_cc_{version}'
            ))

            applications.extend(self._findApplications(
                expression=r'The Foundry\\Nuke(.{1,10})\\nuke.exe$',
                top=os.environ['PROGRAMFILES'],
                label='Nuke {version}',
                applicationIdentifier='nuke_{version}'
            ))

            applications.extend(self._findApplications(
                expression=r'Autodesk\\Maya([\d]{1,4})\\bin\\maya.exe$',
                top=os.environ['PROGRAMFILES'],
                label='Maya {version}',
                applicationIdentifier='maya_{version}'
            ))

            applications.extend(self._findApplications(
                expression=(
                    r'The Foundry\\'
                    r'HieroPlayer(.{1,10})\\'
                    r'hieroplayer.exe$'
                ),
                top=os.environ['PROGRAMFILES'],
                label='HieroPlayer {version}',
                applicationIdentifier='hieroplayer_{version}'
            ))

        return applications


class GetApplicationsHook(object):
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

    def __init__(self, applicationStore):
        '''Instantiate the hook and setup logging.'''
        self.logger = logging.getLogger(
            'ftrack.hook.' + self.__class__.__name__
        )

        self.applicationStore = applicationStore

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
        applications = self._getApplications()
        applications = sorted(
            applications, key=lambda application: application['label']
        )

        for application in applications:
            applicationIdentifier = application['applicationIdentifier']
            label = application['label']
            items.append({
                'applicationIdentifier': applicationIdentifier,
                'label': label
            })

            if applicationIdentifier.startswith('premiere_pro_cc'):
                items.append({
                    'applicationIdentifier': applicationIdentifier,
                    'label': '{label} with latest version'.format(
                        label=label
                    ),
                    'applicationData': {
                        'launchWithLatest': True
                    }
                })

        return {
            'items': items
        }

    def _getApplications(self):
        '''Return applications from the application store.'''
        return self.applicationStore.getApplications()


class LaunchApplicationHook(object):
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

    def __init__(self, applicationStore):
        '''Instantiate the hook and setup logging.'''
        self.logger = logging.getLogger(
            'ftrack.hook.' + self.__class__.__name__
        )

        self.applicationStore = applicationStore

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

    def _getApplications(self):
        '''Return applications from the application store.'''
        return self.applicationStore.getApplications()

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
        for application in self._getApplications():
            if application['applicationIdentifier'] == applicationIdentifier:
                applicationConfig = application

            elif (
                applicationIdentifier == 'hieroplayer' and
                application['applicationIdentifier'].startswith('hieroplayer')
            ):
                applicationConfig = application

        if applicationConfig and sys.platform in ('win32', 'linux2'):
            command = [
                applicationConfig['path']
            ]
        elif applicationConfig and sys.platform == 'darwin':
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
        if (command is not None and applicationData is not None):
            selection = context.get('selection')
            if selection and applicationData.get('launchWithLatest', False):
                entity = selection[0]

                if applicationIdentifier.startswith('premiere_pro_cc'):
                    component = self.findLatestComponent(
                        entity['entityId'],
                        entity['entityType'],
                        'prproj'
                    )

                if component is not None:
                    command.append(component.getFilesystemPath())

        return command

    def findLatestComponent(self, entityId, entityType, extension=''):
        '''Return the latest published component from *entityId* and *entityType*.

        *extension* can be used to find suitable components by matching with
        their file system path.

        '''
        versions = []
        if entityType == 'task':
            task = ftrack.Task(entityId)
            versions = task.getAssetVersions()
        elif entityType == 'assetversion':
            versions = [ftrack.AssetVersion(entityId)]
        else:
            self.logger.debug(
                (
                    'Unable to find latest version from entityId={entityId} '
                    'with entityType={entityType}.'
                ).format(
                    entityId=entityId,
                    entityType=entityType
                )
            )
            return None

        lastDate = None
        latestComponent = None
        for version in versions:
            for component in version.getComponents():
                fileSystemPath = component.getFilesystemPath()
                if fileSystemPath.endswith(extension):
                    if (
                        lastDate is None or
                        version.getDate() > lastDate
                    ):
                        latestComponent = component
                        lastDate = version.getDate()
        return latestComponent

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
    applicationStore = ApplicationsStore()

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.get-applications',
        GetApplicationsHook(applicationStore)
    )

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.launch-application',
        LaunchApplicationHook(applicationStore)
    )
