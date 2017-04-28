# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import abc
import os
import datetime
import uuid
import tempfile
import urlparse
import traceback
import glob
import imp
import urllib2
import re
import sys

from QtExt import QtWidgets, QtNetwork, QtCore, QtGui

import ftrack
import ftrack_api
from ftrack_api import symbol
import ftrack_connect.session as connect_session


# Append ftrack to urlparse.
for method in filter(lambda s: s.startswith('uses_'), dir(urlparse)):
    getattr(urlparse, method).append('ftrack')


class Connector(object):
    '''Main connector.'''

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, session=None):
        '''Instantiate base connector.'''
        super(Connector, self).__init__()
        self.session = session or connect_session.get_shared_session()

    @staticmethod
    @abc.abstractmethod
    def getAssets():
        '''Return list of asset tuples from scene.'''
        pass

    @staticmethod
    @abc.abstractmethod
    def getFileName():
        '''Return full path filename.'''
        pass

    @staticmethod
    @abc.abstractmethod
    def getMainWindow():
        '''Return main window.'''
        pass

    @staticmethod
    @abc.abstractmethod
    def importAsset(iAObj):
        '''Import asset into application.'''
        pass

    @staticmethod
    @abc.abstractmethod
    def selectObject(applicationObject=''):
        '''Set selection from *applicationObject*.'''
        pass

    @staticmethod
    @abc.abstractmethod
    def removeObject(applicationObject=''):
        '''Remove *applicationObject* from scene.'''
        pass

    @staticmethod
    @abc.abstractmethod
    def changeVersion(applicationObject=None, iAObj=None):
        '''Change version of *applicationObject* and *iAObj*.'''
        pass

    @staticmethod
    @abc.abstractmethod
    def getSelectedObjects():
        '''Return selected objects from scene.'''
        pass

    @staticmethod
    def setNodeColor(applicationObject='', latest=True):
        '''Set node indication of version if this feature exist.'''
        pass

    @staticmethod
    @abc.abstractmethod
    def publishAsset(iAObj=None):
        '''Publish asset and return list of components.'''
        pass

    @staticmethod
    @abc.abstractmethod
    def getConnectorName():
        '''Return name of this connector.'''
        return 'main'

    @staticmethod
    @abc.abstractmethod
    def getUniqueSceneName():
        '''Return a unique scene name.'''
        pass

    @staticmethod
    def takeScreenshot():
        '''Save screenshot of current application and return file path.'''
        fileName = os.path.join(
            tempfile.gettempdir(), str(uuid.uuid4()) + '.jpg'
        )
        QtWidgets.QPixmap.grabWindow(
            QtWidgets.QApplication.activeWindow().winId()
        ).save(fileName, 'jpg')
        return fileName

    @staticmethod
    @abc.abstractmethod
    def batch():
        '''Return true if batch is enabled.'''
        #: TODO: Clarify this and how it is used.
        return False

    @classmethod
    def registerAssets(cls):
        '''Register custom assets from FTRACK_OVERRIDE_PATH.'''
        if 'FTRACK_OVERRIDE_PATH' in os.environ:
            splitPath = os.environ['FTRACK_OVERRIDE_PATH'].split(os.pathsep)
            for path in splitPath:
                for f in glob.glob(path + '/*.py'):
                    try:
                        foo = imp.load_source(
                            os.path.splitext(os.path.basename(f))[0], f
                        )
                        if foo.connector() == cls.getConnectorName():
                            foo.registerAssetTypes()
                    except:
                        pass

    @staticmethod
    def executeInThread(function, arg):
        '''Execute *function* in thread with *arg* if supported.'''
        function(arg)

    @classmethod
    def prePublish(cls, iAObj):
        '''Make certain scene validations before actualy publishing *iAObj*.'''
        parent = ftrack.Task(iAObj.taskId).getParent()
        if parent.get('entityType') == 'show':
            return None, 'Task parent cant be show'
        else:
            return True, ''

    @staticmethod
    def postPublish(iAObj=None, publishedComponents=None):
        '''Run post publish for *iAObj* and *publishedComponents*.'''
        if 'FTRACK_OVERRIDE_PATH' in os.environ:
            splittedPath = os.environ['FTRACK_OVERRIDE_PATH'].split(os.pathsep)
            for path in splittedPath:
                fileName = os.path.join(path, 'postpublish.py')
                if os.path.isfile(fileName):
                    postPublishMod = imp.load_source('postPublishMod', fileName)
                    postPublishMod.postPublish(iAObj, publishedComponents)

    @staticmethod
    def objectById(identifier):
        '''Return object from *identifier*.'''
        obj = None

        if identifier != '':
            if 'ftrack://' in identifier:
                url = urlparse.urlparse(identifier)
                query = urlparse.parse_qs(url.query)
                entityType = query.get('entityType')[0]

                identifier = url.netloc

                if entityType == 'assettake':
                    obj = ftrack.Component(identifier)
                elif entityType == 'asset_version':
                    obj = ftrack.AssetVersion(identifier)
                elif entityType == 'asset':
                    obj = ftrack.Asset(identifier)
                elif entityType == 'show':
                    obj = ftrack.Project(identifier)
                elif entityType == 'task':
                    obj = ftrack.Task(identifier)

            else:
                ftrackObjectClasses = [
                    ftrack.Task,
                    ftrack.Asset, ftrack.AssetVersion, ftrack.Component,
                    ftrack.Project
                ]

                for cls in ftrackObjectClasses:
                    try:
                        obj = cls(id=identifier)
                        break
                    except:
                        pass

        return obj

    @staticmethod
    def publishAssetFiles(publishedComponents, assetVersion, pubObj,
                          moveFiles=False, copyFiles=True,
                          progressCallback=None, startProgress=0,
                          endProgress=100):
        '''Publish asset files.'''
        session = connect_session.get_shared_session()
        if progressCallback:
            progressCallback(startProgress)

        asset_version = session.get('AssetVersion', assetVersion.getId())
        for componentNumber, ftComponent in enumerate(publishedComponents):
            path = HelpFunctions.safeString(ftComponent.path)

            if ftComponent.componentname != 'thumbnail':

                location = Connector.pickLocation(copyFiles=copyFiles)

                try:
                    component = asset_version.create_component(
                        path=path,
                        data={'name': ftComponent.componentname},
                        location=location
                    )

                    session.commit()

                except Exception as error:
                    errorMessage = (
                        'A problem occurred while writing your files. It is '
                        'possible the disk settings in ftrack are incorrect. If '
                        'you are an administrator in ftrack you can check the '
                        'settings in the Settings->Disks section from the web '
                        'interface. If you are not an administrator then please '
                        'ask your administrator to check the settings for you '
                        'or drop us a line at support@ftrack.com.'
                    )
                    QtWidgets.QMessageBox.critical(
                        None,
                        'ftrack: Failed to publish.',
                        errorMessage
                    )
                    print traceback.format_exc()
                    print error

                    return

            else:
                thumb = assetVersion.createThumbnail(path)
                try:
                    currentTask = assetVersion.getTask()
                    currentTask.setThumbnail(thumb)
                except Exception:
                    print 'no task'

                try:
                    shot = assetVersion.getAsset().getParent()
                    shot.setThumbnail(thumb)
                except Exception:
                    print 'no shot for some reason'

            if len(ftComponent.metadata) > 0:
                for k, v in ftComponent.metadata:
                    component['metadata'][k] = v

            if progressCallback:
                progressStep = (endProgress - startProgress) / len(publishedComponents)
                progressCallback(startProgress + progressStep * (componentNumber + 1))

        asset_version['is_published'] = True
        session.commit()
        Connector.postPublish(pubObj, publishedComponents)

        if progressCallback:
            progressCallback(endProgress)

    @staticmethod
    def pickLocation(copyFiles=False):
        '''Return a location based on *copyFiles*.'''
        location = None
        session = connect_session.get_shared_session()
        locations = session.query('select id, name from Location').all()

        sorted_locations = sorted(
            locations, key=lambda _location: _location.priority
        )

        visible_locations = filter(
            lambda _location: _location['name'] not in ('ftrack.origin',),
            sorted_locations
        )

        for candidateLocation in visible_locations:
            if candidateLocation.accessor is not symbol.NOT_SET:
                # Can't copy files to an unmanaged location.
                if (
                    copyFiles and
                    isinstance(
                        candidateLocation,
                        ftrack_api.entity.location.UnmanagedLocationMixin
                    )
                ):
                    continue

                location = candidateLocation
                break

        return location


class HelpFunctions(object):
    '''Help functions.'''

    def __init__(self):
        super(HelpFunctions, self).__init__()

    @staticmethod
    def safeString(string):
        '''Return utf-8 encoded string from unicode *string*.'''
        if isinstance(string, unicode):
            return string.encode('utf-8')

        return string

    @staticmethod
    def temporaryDirectory():
        '''Return a temporary directory for storing data.'''
        return tempfile.mkdtemp()

    @staticmethod
    def temporaryFile(suffix=None):
        '''Return a temporary file for storing data.'''
        _, path = tempfile.mkstemp(suffix=suffix)
        return path

    @staticmethod
    def getUniqueNumber():
        '''Return unique number.'''
        return str(datetime.datetime.today()).split('.')[1]

    @staticmethod
    def getPath(task, unders=False, slash=False):
        '''Return path from *task*.'''
        path = ''
        if task.get('entityType') == 'show':
            path = task.getName()
        else:
            shotparentstemp = task.getParents()
            shotparents = []
            for t in reversed(shotparentstemp):
                if t.getName() == 'Asset builds':
                    shotparents.append('assetb')
                else:
                    shotparents.append(t.getName())

            path = shotparents + [task.getName()]
            if unders:
                shotpath = '_'.join(path)
            elif slash:
                shotpath = ' / '.join(path)
            else:
                shotpath = '.'.join(path)
            path = shotpath
        return path

    @staticmethod
    def getFileFromUrl(url, toFile=None, returnResponse=None):
        '''Return file from *url.'''
        ftrackProxy = os.getenv('FTRACK_PROXY', '')
        ftrackServer = os.getenv('FTRACK_SERVER', '')
        if ftrackProxy != '':
            if ftrackServer.startswith('https'):
                httpHandle = 'https'
            else:
                httpHandle = 'http'

            proxy = urllib2.ProxyHandler({httpHandle: ftrackProxy})
            opener = urllib2.build_opener(proxy)
            response = opener.open(url)
            html = response.read()
        else:
            response = urllib2.urlopen(url)
            html = response.read()

        if toFile:
            output = open(toFile, 'wb')
            output.write(html)
            output.close()

        if returnResponse:
            return response

        return html

    @staticmethod
    def getFtrackQNetworkProxy():
        '''Return ftrack proxy if configured.'''
        ftrackProxy = os.getenv('FTRACK_PROXY', '')
        if ftrackProxy != '':

            # Must start with http, or overflow error.
            if not ftrackProxy.startswith('http'):
                ftrackProxy = 'http://%s' % ftrackProxy

            proxy_url = QtCore.QUrl(ftrackProxy)
            proxy = QtNetwork.QNetworkProxy(
                QtNetwork.QNetworkProxy.HttpProxy,
                proxy_url.host(),
                proxy_url.port(),
                proxy_url.userName(),
                proxy_url.password()
            )

            return proxy

        return None

    @staticmethod
    def getFileSequenceStartEnd(path):
        '''Return file sequence start and end from *path*.'''
        try:
            if '%V' in path:
                path = path.replace('%V', 'left')
            hashMatch = re.search('#+', path)
            if hashMatch:
                path = path[:hashMatch.start(0)] + '*' + path[hashMatch.end(0):]

            nukeFormatMatch = re.search('%\d+d', path)
            if nukeFormatMatch:
                path = (
                    path[:nukeFormatMatch.start(0)] + '*' +
                    path[nukeFormatMatch.end(0):]
                )

            fileExtension = os.path.splitext(path)[1].replace('.', '\.')
            files = sorted(glob.glob(path))
            regexp = '(\d+)' + fileExtension + ''
            first = int(re.findall(regexp, files[0])[0])
            last = int(re.findall(regexp, files[-1])[0])
        except:
            traceback.print_exc(file=sys.stdout)
            first = 1
            last = 1

        return first, last


class FTAssetType(object):
    '''Base class for assets used when importing or publishing.'''

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        '''Instantiate asset class.'''
        super(FTAssetType, self).__init__()

    @abc.abstractmethod
    def importAsset(self):
        '''Import asset.'''
        pass

    @abc.abstractmethod
    def publishAsset(self):
        '''Publish asset.'''
        pass

    @abc.abstractmethod
    def changeVersion(self):
        '''Change version of asset.'''
        pass

    def getTotalSteps(self, steps=[]):
        '''Return total steps.'''
        totalSteps = 0
        for step in steps:
            if step:
                totalSteps += 1
        return totalSteps

    def validate(self):
        '''Return true if valid.'''
        pass


class FTAssetObject(object):
    '''Class to easier store the variables passed around when importing.'''

    def __init__(
        self, componentId='', filePath='', componentName='', assetVersionId='',
        options={}, taskId=''
    ):
        '''Instantiate asset object.'''
        super(FTAssetObject, self).__init__()
        self.componentId = componentId
        self.filePath = filePath
        self.componentName = componentName
        self.shared_session = connect_session.get_shared_session()
        self.options = options
        self.setTotalSteps = True
        self.taskId = taskId

        if assetVersionId != '':
            assetVersion = self.shared_session.query(
                'select id, asset, asset.name,'
                ' asset.id, asset.type.short '
                ' from AssetVersion where id is "{0}"'.format(assetVersionId)
            ).one()
            self.assetVersionId = assetVersionId
            assetVersionStr = str(assetVersion['version'])
            self.assetVersion = assetVersionStr
            self.assetName = assetVersion['asset']['name']
            self.assetType = assetVersion['asset']['type']['short']
            self.assetId = assetVersion['asset']['id']

        if self.componentId != '':
            component = self.shared_session.query(
                'select name, version.asset.type.short, version.asset.name, '
                'version.asset.type.name, version.asset.versions.version, '
                'version.id, version.version, version.asset.versions, '
                'version.date, version.comment, version.asset.name, version, '
                'version_id, version.user.first_name, version.user.last_name '
                ' from Component where id is {0}'.format(self.componentId)
            ).one()
            self.metadata = []
            for k, v in component['metadata'].items():
                self.metadata.append((k, v))

        try:
            self.zversion = assetVersionStr.zfill(3)
        except:
            self.zversion = '000'


class FTAssetHandler(object):
    '''Class for handling assets.'''

    def __init__(self):
        '''Instantiate asset handler.'''
        super(FTAssetHandler, self).__init__()
        self.assetTypeClasses = dict()

    def registerAssetType(self, name, cls):
        '''Register asset type *cls* with *name*.'''
        self.assetTypeClasses[name] = cls

    def getAssetTypes(self):
        '''Return all registered asset types.'''
        assetTypes = []
        for key, value in self.assetTypeClasses.items():
            assetTypes.append(key)
        return assetTypes

    def getAssetClass(self, assetType):
        '''Return asset class from *assetType* name.'''
        if assetType in self.assetTypeClasses:
            return self.assetTypeClasses[assetType]()
        else:
            return None

# Variable to keep singleton asset handler.
_ftHandler = None


class FTAssetHandlerInstance(object):
    '''Return singleton asset handler.'''

    def __init__(self):
        '''Instantiate asset handler.'''
        super(FTAssetHandlerInstance, self).__init__()

    @staticmethod
    def instance():
        '''Return singleton asset handler.'''
        global _ftHandler
        if not _ftHandler:
            _ftHandler = FTAssetHandler()
        return _ftHandler


class FTComponent(object):
    '''Component class.'''

    def __init__(self, path='', files=None, componentname='', metadata=[]):
        '''Instantiate component.'''
        self.path = path
        self.files = files
        self.componentname = componentname
        self.metadata = metadata
