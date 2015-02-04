# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging

from PySide import QtGui
import ftrack

import ftrack_connect.asynchronous
from ftrack_connect.ui.widget import item_selector as _item_selector


class AssetSelector(_item_selector.ItemSelector):
    '''Asset type selector widget.'''

    def __init__(self, *args, **kwargs):
        '''Instantiate the asset type selector.'''
        super(AssetSelector, self).__init__(
            labelField='name',
            defaultLabel='Unknown asset',
            emptyLabel='Select asset',
            **kwargs
        )

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )


    @ftrack_connect.asynchronous.asynchronous
    def loadAssets(self, entity):
        '''Load assets and add to selector.'''
        assets = entity.getAssets()
        self.logger.debug('Loaded {0} assets'.format(len(assets)))
        assets = sorted(assets, key=lambda asset: asset.getName())
        self.setItems(assets)

