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
import glob

import ftrack


class ApplicationStore(object):
    '''Discover and store available applications on this host.'''

    def __init__(self):
        '''Instantiate store and discover applications.'''
        super(ApplicationStore, self).__init__()
        self.logger = logging.getLogger(
            'ftrack.hook.' + self.__class__.__name__
        )
        # Construct default version expression that will match last set of
        # numbers in string where numbers may contain a digit followed by zero
        # or more digits, periods, or the letters 'a', 'b', 'c' or 'v'.
        # E.g. /path/to/x86/some/application/folder/v1.8v2b1/app.exe -> 1.8v2b1
        self.defaultVersionExpression = re.compile(
            r'(?P<version>\d[\d.vabc]*)[^\d]*$'
        )
        self.applications = self._getApplications()

    def getApplications(self):
        '''Return list of available applications.'''
        return self.applications

    def _findApplications(self, expression, label, applicationIdentifier,
                          versionExpression=None):
        '''
        Return list of found applications base on *expression*.

        *expression* is passed directly to the :py:mod:`glob` module to match
        path names.

        *versionExpression* is a regular expression used to find the version of
        the application. This expression should include a named backreference.
        For example::

            '(?P<version>[\d]{4})'

        If not specified, a default expression will be used that will attempt
        to match the last numbers found in the path following standard version
        schemes.

        *label* is the label the application will be given. *label* should be on
        the format "Name of app {version}".

        *applicationIdentifier* should be on the form
        "application_name_{version}" where version is the first match in the
        regexp.

        '''
        if versionExpression is None:
            versionExpression = self.defaultVersionExpression
        else:
            versionExpression = re.compile(versionExpression)

        applications = []
        results = glob.glob(expression)
        for result in results:
            match = versionExpression.search(result)
            if match:
                version = match.group('version')
                applications.append({
                    'applicationIdentifier': applicationIdentifier.format(
                        version=version
                    ),
                    'path': result,
                    'version': version,
                    'label': label.format(version=version)
                })
            else:
                self.logger.debug(
                    'Found application executable did not appear to contain '
                    'required version information: {0}'.format(result)
                )

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
            prefix = '/Applications/'

            applications.extend(self._findApplications(
                expression=(
                    prefix +
                    'Adobe Premiere Pro CC */Adobe Premiere Pro CC *.app'
                ),
                label='Premiere Pro CC {version}',
                applicationIdentifier='premiere_pro_cc_{version}'
            ))

            applications.extend(self._findApplications(
                expression=prefix + 'Autodesk/maya*/Maya.app',
                label='Maya {version}',
                applicationIdentifier='maya_{version}'
            ))

            applications.extend(self._findApplications(
                expression=prefix + 'Nuke*/Nuke*.app',
                label='Nuke {version}',
                applicationIdentifier='nuke_{version}'
            ))

            applications.extend(self._findApplications(
                expression=prefix + 'HieroPlayer*/HieroPlayer*.app',
                label='HieroPlayer {version}',
                applicationIdentifier='hieroplayer_{version}'
            ))

            applications.extend(self._findApplications(
                expression=prefix + 'Hiero*/Hiero*.app',
                label='Hiero {version}',
                applicationIdentifier='hiero_{version}'
            ))

        elif sys.platform == 'win32':
            prefix = 'C:\\Program Files*\\'

            applications.extend(self._findApplications(
                expression=(
                    prefix +
                    'Adobe\\Adobe Premiere Pro CC *\\Adobe Premiere Pro.exe'
                ),
                label='Premiere Pro CC {version}',
                applicationIdentifier='premiere_pro_cc_{version}'
            ))

            applications.extend(self._findApplications(
                expression=prefix + 'Autodesk\\Maya*\\bin\\maya.exe',
                label='Maya {version}',
                applicationIdentifier='maya_{version}'
            ))

            applications.extend(self._findApplications(
                expression=prefix + 'Nuke*\\nuke.exe',
                label='Nuke {version}',
                applicationIdentifier='premiere_pro_cc_{version}'
            ))

            applications.extend(self._findApplications(
                expression=(
                    prefix + 'The Foundry\\HieroPlayer*\\hieroplayer.exe'
                ),
                label='HieroPlayer {version}',
                applicationIdentifier='hieroplayer_{version}'
            ))

            applications.extend(self._findApplications(
                expression=prefix + 'The Foundry\\Hiero*\\hiero.exe',
                label='Hiero {version}',
                applicationIdentifier='hiero_{version}'
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
        super(GetApplicationsHook, self).__init__()
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
        super(LaunchApplicationHook, self).__init__()
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
                'Unable to find launch command for {0} on this platform.'
                .format(applicationIdentifier)
            )

        # Figure out if the command should be started with the file path of
        # the latest published version.
        if command is not None and applicationData is not None:
            selection = context.get('selection')
            if selection and applicationData.get('launchWithLatest', False):
                entity = selection[0]
                component = None

                if applicationIdentifier.startswith('premiere_pro_cc'):
                    component = self._findLatestComponent(
                        entity['entityId'],
                        entity['entityType'],
                        'prproj'
                    )

                if component is not None:
                    command.append(component.getFilesystemPath())

        return command

    def _findLatestComponent(self, entityId, entityType, extension=''):
        '''Return latest published component from *entityId* and *entityType*.

        *extension* can be used to find suitable components by matching with
        their file system path.

        '''
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
        # Copy appropriate environment variables to new environment.
        environment = {
            'FTRACK_SERVER': os.environ.get('FTRACK_SERVER'),
            'FTRACK_PROXY': os.environ.get('FTRACK_PROXY'),
            'FTRACK_APIKEY': os.environ.get('FTRACK_APIKEY'),
            'LOGNAME': os.environ.get('LOGNAME'),
            'FTRACK_EVENT_SERVER': ftrack.EVENT_HUB.getServerUrl(),
            'FTRACK_LOCATION_PLUGIN_PATH': os.environ.get(
                'FTRACK_LOCATION_PLUGIN_PATH'
            )
        }

        if sys.platform == 'win32':
            # Required for launching executables on Windows.
            environment['SystemRoot'] = os.environ.get('SystemRoot')
            environment['SystemDrive'] = os.environ.get('SystemDrive')

            # Many applications also need access to temporary storage and other
            # executable.
            environment['PATH'] = os.environ.get('PATH')
            environment['TMP'] = os.environ.get('TMP')

        # Add discovered ftrack API to PYTHONPATH.
        environment['PYTHONPATH'] = os.path.dirname(ftrack.__file__)

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
    applicationStore = ApplicationStore()

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.get-applications',
        GetApplicationsHook(applicationStore)
    )

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.launch-application',
        LaunchApplicationHook(applicationStore)
    )
