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

from PySide import QtGui, QtNetwork, QtCore

import ftrack


def register_scheme(scheme):
    for method in filter(lambda s: s.startswith('uses_'), dir(urlparse)):
        getattr(urlparse, method).append(scheme)

register_scheme('ftrack')


class Connector(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        super(Connector, self).__init__()

    # Return array of asset-ids in scene
    @staticmethod
    @abc.abstractmethod
    def getAssets():
        pass

    # Return full path filename
    @staticmethod
    @abc.abstractmethod
    def getFileName():
        pass

    # Get some kind of handle to use
    # when attaching panels
    @staticmethod
    @abc.abstractmethod
    def getMainWindow():
        pass

    # Import asset into application
    @staticmethod
    @abc.abstractmethod
    def importAsset(iAObj):
        pass

    # Set selection
    @staticmethod
    @abc.abstractmethod
    def selectObject(applicationObject=''):
        pass

    # Remove object
    @staticmethod
    @abc.abstractmethod
    def removeObject(applicationObject=''):
        pass

    # Change version of asset
    @staticmethod
    @abc.abstractmethod
    def changeVersion(applicationObject=None, iAObj=None):
        pass

    # Get selected objects in scene
    @staticmethod
    @abc.abstractmethod
    def getSelectedObjects():
        pass

    # Set node indication of version if this feature exist
    @staticmethod
    def setNodeColor(applicationObject='', latest=True):
        pass

    # Publish asset. Return array of components
    @staticmethod
    @abc.abstractmethod
    def publishAsset(iAObj=None):
        pass

    # Init available dialogs
    @staticmethod
    @abc.abstractmethod
    def init_dialogs(ftrackDialogs, availableDialogs=[]):
        pass

    # Return connector name
    @staticmethod
    @abc.abstractmethod
    def getConnectorName():
        return 'main'

    # Find a unique name to use when importing
    @staticmethod
    @abc.abstractmethod
    def getUniqueSceneName():
        pass

    # Use Qt to get a screengrab of current application
    @staticmethod
    def takeScreenshot():
        fileName = os.path.join(
            tempfile.gettempdir(), str(uuid.uuid4()) + '.jpg'
        )
        QtGui.QPixmap.grabWindow(
            QtGui.QApplication.activeWindow().winId()
        ).save(fileName, 'jpg')
        return fileName

    @staticmethod
    @abc.abstractmethod
    def batch():
        print 'Maincon debug'
        return False

    # Register custom assets from FTRACK_OVERRIDE_PATH
    @classmethod
    def registerAssets(cls):
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
        function(*arg)

    # Make certain scene validations before actualy publishing
    @classmethod
    def prePublish(cls, iAObj):
        parent = ftrack.Task(iAObj.taskId).getParent()
        if parent.get('entityType') == 'show':
            return None, 'Task parent cant be show'
        else:
            return True, ''

    # Do things after publish as send email or other fun stuff
    @staticmethod
    def postPublish(iAObj=None, publishedComponents=None):
        if 'FTRACK_OVERRIDE_PATH' in os.environ:
            splittedPath = os.environ['FTRACK_OVERRIDE_PATH'].split(os.pathsep)
            for path in splittedPath:
                fileName = os.path.join(path, 'postpublish.py')
                if os.path.isfile(fileName):
                    postPublishMod = imp.load_source('postPublishMod', fileName)
                    postPublishMod.postPublish(iAObj, publishedComponents)

    @staticmethod
    def objectById(identifier):
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

        if progressCallback:
            progressCallback(startProgress)

        for componentNumber, ftComponent in enumerate(publishedComponents):
            if ftComponent.componentname != 'thumbnail':

                location = Connector.pickLocation(copyFiles=copyFiles)
                component = assetVersion.createComponent(
                    name=ftComponent.componentname,
                    path=ftComponent.path,
                    location=None
                )
                try:
                    location.addComponent(component)
                except ftrack.AccessorError as error:
                    errorMessage = (
                        'A problem occurred while writing your files. It is '
                        'possible the disk settings in ftrack are incorrect. If '
                        'you are an administrator in ftrack you can check the '
                        'settings in the Settings->Disks section from the web '
                        'interface. If you are not an administrator then please '
                        'ask your administrator to check the settings for you '
                        'or drop us a line at support@ftrack.com.'
                    )
                    QtGui.QMessageBox.critical(
                        None,
                        'ftrack: Failed to publish.',
                        errorMessage
                    )
                    print traceback.format_exc()
                    print error

                    return

            else:
                thumb = assetVersion.createThumbnail(ftComponent.path)
                try:
                    currentTask = assetVersion.getTask()
                    currentTask.setThumbnail(thumb)
                except:
                    print 'no task'

                try:
                    shot = assetVersion.getAsset().getParent()
                    shot.setThumbnail(thumb)
                except:
                    print 'no shot for some reason'

            if len(ftComponent.metadata) > 0:
                for k, v in ftComponent.metadata:
                    component.setMeta(k, v)

            if progressCallback:
                progressStep = (
                    (endProgress - startProgress) / len(publishedComponents)
                )
                progressCallback(
                    startProgress + progressStep * (componentNumber + 1)
                )

        assetVersion.publish()
        Connector.postPublish(pubObj, publishedComponents)

        if progressCallback:
            progressCallback(endProgress)

    @staticmethod
    def pickLocation(copyFiles=False):
        '''Return a location based on *copyFiles*.'''
        location = None
        locations = ftrack.getLocations()

        for candidateLocation in locations:
            if candidateLocation.getAccessor() is not None:
                # Can't copy files to an unmanaged location.
                if (
                    copyFiles and
                    isinstance(candidateLocation, ftrack.UnmanagedLocation)
                ):
                    continue

                location = candidateLocation
                break

        return location


class HelpFunctions(object):
    def __init__(self):
        super(HelpFunctions, self).__init__()

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
    def createAssetFolder(assetVersionId='', component=None):
        assetVersion = ftrack.AssetVersion(assetVersionId)
        asset = assetVersion.getAsset()
        assettype = asset.getType().getShort()
        assetname = asset.getName()
        zversion = str(assetVersion.getVersion()).zfill(3)

        assetParent = asset.getParent()

        showAssetRoot = assetParent.getProject().getPath(True)
        shotPath = HelpFunctions.getPath(assetParent)

        s = shotPath.split('.')
        assetpath = '_'.join(s) + '_' + assetname + \
            '_' + assettype + '_v' + zversion

        if component:
            assetpath += '_' + component

        endOfPath = os.path.join(*[s[x] for x in range(1, len(s))])
        assetabspath = os.path.join(
            showAssetRoot, endOfPath, assettype, assetpath
        )
        assetpath = os.path.join(endOfPath, assettype, assetpath)

        if(not os.path.isdir(assetabspath)):
            os.makedirs(assetabspath, 00775)

        return assetpath, assetabspath

    @staticmethod
    def getUniqueNumber():
        return str(datetime.datetime.today()).split('.')[1]

    @staticmethod
    def getPath(task, unders=False, slash=False):
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


# Base class for assets used when importing or publishing
class FTAssetType(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(FTAssetType, self).__init__()

    @abc.abstractmethod
    def importAsset(self):
        pass

    @abc.abstractmethod
    def publishAsset(self):
        pass

    @abc.abstractmethod
    def changeVersion(self):
        pass

    def getTotalSteps(self, steps=[]):
        totalSteps = 0
        for step in steps:
            if step:
                totalSteps += 1
        return totalSteps

    def validate(self):
        pass


# Class to easier store the variables passed around when importing
class FTAssetObject(object):
    def __init__(
        self, componentId='', filePath='', componentName='', assetVersionId='',
        options={}, taskId=''
    ):
        super(FTAssetObject, self).__init__()
        self.componentId = componentId
        self.filePath = filePath
        self.componentName = componentName

        self.options = options
        self.setTotalSteps = True
        self.taskId = taskId

        if assetVersionId != '':
            self.assetVersionId = assetVersionId
            assetVersion = ftrack.AssetVersion(assetVersionId)

            assetVersionStr = str(assetVersion.getVersion())

            self.assetVersion = assetVersionStr

            asset = assetVersion.getAsset()
            self.assetName = asset.getName()
            self.assetType = asset.getType().getShort()

        if self.componentId != '':
            metaDict = ftrack.Component(self.componentId).getMeta()
            self.metadata = []
            for k, v in metaDict.items():
                self.metadata.append((k, v))

        try:
            self.zversion = assetVersionStr.zfill(3)
        except:
            self.zversion = '000'


# Class for handling assets
class FTAssetHandler(object):
    def __init__(self):
        super(FTAssetHandler, self).__init__()
        self.assetTypeClasses = dict()

    def registerAssetType(self, name, cls):
        self.assetTypeClasses[name] = cls

    def getAssetTypes(self):
        assetTypes = []
        for key, value in self.assetTypeClasses.items():
            assetTypes.append(key)
        return assetTypes

    def getAssetClass(self, assetType):
        if assetType in self.assetTypeClasses:
            return self.assetTypeClasses[assetType]()
        else:
            return None

_ftHandler = None


class FTAssetHandlerInstance(object):
    def __init__(self):
        super(FTAssetHandlerInstance, self).__init__()

    @staticmethod
    def instance():
        global _ftHandler
        if not _ftHandler:
            _ftHandler = FTAssetHandler()
        return _ftHandler


class FTComponent(object):
    def __init__(self, path='', files=None, componentname='', metadata=[]):
        self.path = path
        self.files = files
        self.componentname = componentname
        self.metadata = metadata
