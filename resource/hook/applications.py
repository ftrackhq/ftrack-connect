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
import pprint

import ftrack

#: Default expression to match version component of executable path.
#: Will match last set of numbers in string where numbers may contain a digit
#: followed by zero or more digits, periods, or the letters 'a', 'b', 'c' or 'v'
#: E.g. /path/to/x86/some/application/folder/v1.8v2b1/app.exe -> 1.8v2b1
DEFAULT_VERSION_EXPRESSION = re.compile(
    r'(?P<version>\d[\d.vabc]*?)[^\d]*$'
)


class ApplicationStore(object):
    '''Discover and store available applications on this host.'''

    def __init__(self):
        '''Instantiate store and discover applications.'''
        super(ApplicationStore, self).__init__()
        self.logger = logging.getLogger(
            'ftrack.hook.' + self.__class__.__name__
        )

        # Discover applications and store.
        self.applications = self._discoverApplications()

    def getApplication(self, identifier):
        '''Return first application with matching *identifier*.

        *identifier* may contain a wildcard at the end to match the first
        substring matching entry.

        Return None if no application matches.

        '''
        hasWildcard = identifier[-1] == '*'
        if hasWildcard:
            identifier = identifier[:-1]

        for application in self.applications:
            if hasWildcard:
                if application['identifier'].startswith(identifier):
                    return application
            else:
                if application['identifier'] == identifier:
                    return application

        return None

    def _discoverApplications(self):
        '''Return a list of applications that can be launched from this host.

        An application should be of the form:

            dict(
                'identifier': 'name_version',
                'label': 'Name version',
                'path': 'Absolute path to the file',
                'version': 'Version of the application'
            )

        '''
        applications = []

        if sys.platform == 'darwin':
            prefix = ['/', 'Applications']

            applications.extend(self._searchFilesystem(
                expression=prefix + [
                    'Adobe Premiere Pro CC .+', 'Adobe Premiere Pro CC .+.app'
                ],
                label='Premiere Pro CC {version}',
                applicationIdentifier='premiere_pro_cc_{version}'
            ))

            applications.extend(self._searchFilesystem(
                expression=prefix + ['Autodesk', 'maya.+', 'Maya.app'],
                label='Maya {version}',
                applicationIdentifier='maya_{version}'
            ))

            applications.extend(self._searchFilesystem(
                expression=prefix + ['Nuke.*', 'Nuke\d.+.app'],
                label='Nuke {version}',
                applicationIdentifier='nuke_{version}'
            ))

            applications.extend(self._searchFilesystem(
                expression=prefix + ['HieroPlayer\d.*', 'HieroPlayer\d.+.app'],
                label='HieroPlayer {version}',
                applicationIdentifier='hieroplayer_{version}'
            ))

            applications.extend(self._searchFilesystem(
                expression=prefix + ['Hiero\d.+', 'Hiero\d.+.app'],
                label='Hiero {version}',
                applicationIdentifier='hiero_{version}'
            ))

        elif sys.platform == 'win32':
            prefix = ['C:\\', 'Program Files.*']

            applications.extend(self._searchFilesystem(
                expression=(
                    prefix +
                    ['Adobe', 'Adobe Premiere Pro CC .+',
                     'Adobe Premiere Pro.exe']
                ),
                label='Premiere Pro CC {version}',
                applicationIdentifier='premiere_pro_cc_{version}'
            ))

            applications.extend(self._searchFilesystem(
                expression=prefix + ['Autodesk', 'Maya.+', 'bin', 'maya.exe'],
                label='Maya {version}',
                applicationIdentifier='maya_{version}'
            ))

            applications.extend(self._searchFilesystem(
                expression=prefix + ['Nuke.*', 'Nuke\d.+.exe'],
                label='Nuke {version}',
                applicationIdentifier='nuke_{version}'
            ))

            applications.extend(self._searchFilesystem(
                expression=(
                    prefix +
                    ['The Foundry', 'HieroPlayer\d.+', 'hieroplayer.exe']
                ),
                label='HieroPlayer {version}',
                applicationIdentifier='hieroplayer_{version}'
            ))

            applications.extend(self._searchFilesystem(
                expression=prefix + ['The Foundry', 'Hiero\d.+', 'hiero.exe'],
                label='Hiero {version}',
                applicationIdentifier='hiero_{version}'
            ))

        self.logger.debug(
            'Discovered applications:\n{0}'.format(pprint.pformat(applications))
        )

        return applications

    def _searchFilesystem(self, expression, label, applicationIdentifier,
                          versionExpression=None):
        '''
        Return list of applications found in filesystem matching *expression*.

        *expression* should be a list of regular expressions to match against
        path segments up to the executable. Each path segment traversed will be
        matched against the corresponding expression part. The first expression
        part must not contain any regular expression syntax and must match
        directly to a path existing on disk as it will form the root of the
        search. Example::

            ['C:\\', 'Program Files.*', 'Company', 'Product\d+', 'product.exe']

        *versionExpression* is a regular expression used to find the version of
        *the application. It will be applied against the full matching path of
        *any discovered executable. It must include a named 'version' group
        *which can be used in the label and applicationIdentifier templates.

        For example::

            '(?P<version>[\d]{4})'

        If not specified, then :py:data:`DEFAULT_VERSION_EXPRESSION` will be
        used.

        *label* is the label the application will be given. *label* should be on
        the format "Name of app {version}".

        *applicationIdentifier* should be on the form
        "application_name_{version}" where version is the first match in the
        regexp.

        '''
        applications = []

        if versionExpression is None:
            versionExpression = DEFAULT_VERSION_EXPRESSION
        else:
            versionExpression = re.compile(versionExpression)

        pieces = expression[:]
        start = pieces.pop(0)
        if sys.platform == 'win32':
            # On Windows C: means current directory so convert roots that look
            # like drive letters to the C:\ format.
            if start and start[-1] == ':':
                start += '\\'

        if not os.path.exists(start):
            raise ValueError(
                'First part "{0}" of expression "{1}" must match exactly to an '
                'existing entry on the filesystem.'
                .format(start, expression)
            )

        expressions = map(re.compile, pieces)
        expressionsCount = len(expressions)

        for location, folders, files in os.walk(start, topdown=True):
            level = location.rstrip(os.path.sep).count(os.path.sep)
            expression = expressions[level]

            if level < (expressionsCount - 1):
                # If not yet at final piece then just prune directories.
                folders[:] = [folder for folder in folders
                              if expression.match(folder)]
            else:
                # Match executable. Note that on OSX executable might equate to
                # a folder (.app).
                for entry in folders + files:
                    match = expression.match(entry)
                    if match:
                        # Extract version from full matching path.
                        path = os.path.join(start, location, entry)

                        versionMatch = versionExpression.search(path)
                        if versionMatch:
                            version = versionMatch.group('version')
                            applications.append({
                                'identifier': applicationIdentifier.format(
                                    version=version
                                ),
                                'path': path,
                                'version': version,
                                'label': label.format(version=version)
                            })
                        else:
                            self.logger.debug(
                                'Discovered application executable, but it '
                                'does not appear to o contain required version '
                                'information: {0}'.format(path)
                            )

                # Don't descend any further as out of patterns to match.
                del folders[:]

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
        applications = self.applicationStore.applications
        applications = sorted(
            applications, key=lambda application: application['label']
        )

        for application in applications:
            applicationIdentifier = application['identifier']
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
        data = event['data']['applicationData']

        # Look up application.
        applicationIdentifierPattern = applicationIdentifier
        if applicationIdentifierPattern == 'hieroplayer':
            applicationIdentifierPattern += '*'

        application = self.applicationStore.getApplication(
            applicationIdentifierPattern
        )

        if application is None:
            return {
                'success': False,
                'message': (
                    '{0} application not found.'
                    .format(applicationIdentifier)
                )
            }

        # Construct command and environment.
        command = self._getApplicationLaunchCommand(application, context, data)

        environment = self._getApplicationEnvironment({
            'data': event['data'],
            'source': event['source']
        })

        success = True
        message = '{0} application started.'.format(application['label'])

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
                application['label']
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

    def _getApplicationLaunchCommand(self, application, context, data):
        '''Return *application* command based on OS, *context* and *data*.

        *application* should be a mapping describing the application, as in the
        :py:class:`ApplicationStore`.

        *context* is the entity the application should be started for.

        *data* provides additional information about how the application should
        be launched.

        '''
        command = None

        if sys.platform in ('win32', 'linux2'):
            command = [application['path']]

        elif sys.platform == 'darwin':
            command = ['open', application['path']]

        else:
            self.logger.warning(
                'Unable to find launch command for {0} on this platform.'
                .format(application['identifier'])
            )

        # Figure out if the command should be started with the file path of
        # the latest published version.
        if command is not None and data is not None:
            selection = context.get('selection')
            if selection and data.get('launchWithLatest', False):
                entity = selection[0]
                component = None

                if application['identifier'].startswith('premiere_pro_cc'):
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

    def _mapEnvironmentVariables(self, keys, targetEnvironment,
                                 sourceEnvironment=os.environ):
        '''Map *keys* from *sourceEnvironment* to *targetEnvironment*.

        Only map a key if it is present in *sourceEnvironment* and not already
        present in *targetEnvironment*.

        '''
        for key in keys:
            if key not in targetEnvironment and key in sourceEnvironment:
                targetEnvironment[key] = sourceEnvironment[key]

    def _getApplicationEnvironment(self, eventData=None):
        '''Return mapping of environment variables based on *eventData*.'''
        # Copy appropriate environment variables to new environment.
        environment = {
            'FTRACK_EVENT_SERVER': ftrack.EVENT_HUB.getServerUrl()
        }

        self._mapEnvironmentVariables(
            [
                'FTRACK_SERVER',
                'FTRACK_PROXY',
                'FTRACK_APIKEY',
                'FTRACK_LOCATION_PLUGIN_PATH',
                'LOGNAME'
            ],
            environment
        )

        if sys.platform == 'win32':
            # Required for launching executables on Windows.
            self._mapEnvironmentVariables(
                ['SystemRoot', 'SystemDrive'], environment
            )

            # Many applications also need access to temporary storage and
            # other standard Windows locations.
            self._mapEnvironmentVariables(
                [
                    'APPDATA', 'LOCALAPPDATA',

                    'COMMONPROGRAMW6432',
                    'COMMONPROGRAMFILES', 'COMMONPROGRAMFILES(X86)',

                    'PROGRAMW6432', 'PROGRAMFILES', 'PROGRAMFILES(X86)'

                    'PATH', 'PATHEXT',

                    'TMP', 'TEMP'
                ],
                environment
            )

        # Prepend discovered ftrack API to PYTHONPATH.
        environment['PYTHONPATH'] = (
            os.pathsep.join([
                os.path.dirname(ftrack.__file__),
                os.environ.get('PYTHONPATH', '')
            ])
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
    applicationStore = ApplicationStore()

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.get-applications',
        GetApplicationsHook(applicationStore)
    )

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.launch-application',
        LaunchApplicationHook(applicationStore)
    )
