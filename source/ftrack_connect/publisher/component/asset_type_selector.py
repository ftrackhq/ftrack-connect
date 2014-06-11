# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui
import ftrack

from ..core import asynchronous


class AssetTypeSelectorComponent(QtGui.QComboBox):
    '''Asset type selector component.'''

    def __init__(self, *args, **kwargs):
        '''Instantiate the asset type selector.'''
        super(AssetTypeSelectorComponent, self).__init__(*args, **kwargs)
        self.loadAssetTypes()

    @asynchronous
    def loadAssetTypes(self):
        '''Load asset types and add to selector.'''
        assetTypes = ftrack.getAssetTypes()
        assetTypes = sorted(
            assetTypes,
            key=lambda assetType: assetType.getName()
        )

        for assetType in assetTypes:
            self.addItem(assetType.getName(), assetType)
