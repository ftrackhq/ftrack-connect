# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui
import ftrack

import ftrack_connect.asynchronous


class AssetTypeSelector(QtGui.QComboBox):
    '''Asset type selector widget.'''

    def __init__(self, *args, **kwargs):
        '''Instantiate the asset type selector.'''
        super(AssetTypeSelector, self).__init__(*args, **kwargs)
        itemDelegate = QtGui.QStyledItemDelegate()
        self.setItemDelegate(itemDelegate)
        self.loadAssetTypes()

    @ftrack_connect.asynchronous.asynchronous
    def loadAssetTypes(self):
        '''Load asset types and add to selector.'''
        assetTypes = ftrack.getAssetTypes()
        assetTypes = sorted(
            assetTypes,
            key=lambda assetType: assetType.getName()
        )

        for assetType in assetTypes:
            self.addItem(assetType.getName(), assetType)
