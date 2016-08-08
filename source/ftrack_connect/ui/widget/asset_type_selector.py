# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import ftrack

import ftrack_connect.asynchronous
from ftrack_connect.ui.widget import item_selector as _item_selector


class AssetTypeSelector(_item_selector.ItemSelector):
    '''Asset type selector widget.'''

    def __init__(self, *args, **kwargs):
        '''Instantiate the asset type selector.'''
        super(AssetTypeSelector, self).__init__(
            idField='typeid',
            labelField='name',
            defaultLabel='Unknown asset type',
            emptyLabel='Select asset type',
            **kwargs
        )
        self.loadAssetTypes()

    @ftrack_connect.asynchronous.asynchronous
    def loadAssetTypes(self):
        '''Load asset types and add to selector.'''
        assetTypes = ftrack.getAssetTypes()
        assetTypes = sorted(
            assetTypes,
            key=lambda assetType: assetType.getName()
        )
        self.setItems(assetTypes)
