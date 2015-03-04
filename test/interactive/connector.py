# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack


import ftrack_connect.connector


class TestConnector(ftrack_connect.connector.Connector):

    def __init__(self, components):
        super(TestConnector, self).__init__()
        self._componentIds = components

    # Return array of asset-ids in scene
    def getAssets(self):
        return self._componentIds

    # Return full path filename
    @staticmethod
    def getFileName():
        pass

    # Get some kind of handle to use
    # when attaching panels
    @staticmethod
    def getMainWindow():
        pass

    # Import asset into application
    @staticmethod
    def importAsset(iAObj):
        pass

    # Set selection
    @staticmethod
    def selectObject(applicationObject=''):
        pass

    # Remove object
    @staticmethod
    def removeObject(applicationObject=''):
        pass

    # Change version of asset
    @staticmethod
    def changeVersion(applicationObject=None, iAObj=None):
        pass

    # Get selected objects in scene
    @staticmethod
    def getSelectedObjects():
        pass

    # Set node indication of version if this feature exist
    @staticmethod
    def setNodeColor(applicationObject='', latest=True):
        pass

    # Publish asset. Return array of components
    @staticmethod
    def publishAsset(iAObj=None):
        pass

    # Init available dialogs
    @staticmethod
    def init_dialogs(ftrackDialogs, availableDialogs=[]):
        pass

    # Return connector name
    @staticmethod
    def getConnectorName():
        return 'main'

    # Find a unique name to use when importing
    @staticmethod
    def getUniqueSceneName():
        pass

    @staticmethod
    def batch():
        return False
