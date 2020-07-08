# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging

import ftrack_connect.session
import ftrack_connect.asynchronous
from ftrack_connect.ui.widget import item_selector as _item_selector


class AssetSelector(_item_selector.ItemSelector):
    '''Asset type selector widget.'''

    def __init__(self, *args, **kwargs):
        '''Instantiate the asset type selector.'''
        super(AssetSelector, self).__init__(
            idField='assetid',
            labelField='name',
            defaultLabel='Unknown asset',
            emptyLabel='Select asset',
            **kwargs
        )

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

    @ftrack_connect.asynchronous.asynchronous
    def loadAssets(self, entity, selectAsset=None):
        '''Load assets for *entity* and set selector items.

        If *selectAsset* is specified, select it after assets has loaded.
        '''
        session = ftrack_connect.session.get_scoped()
        safe_entity = session.get(entity.entity_type, entity['id'])
        assets = []
        try:
            # ftrack does not support having Tasks as parent for Assets.
            # Therefore get parent shot/sequence etc.
            if safe_entity.entity_type == 'Task':
                safe_entity = safe_entity['parent']

            assets = safe_entity['assets']
            self.logger.debug('Loaded {0} assets'.format(len(assets)))
            assets = sorted(assets, key=lambda asset: asset['name'])
        except AttributeError:
            self.logger.warning(
                'Unable to fetch assets for entity: {0}'.format(safe_entity)
            )

        self.setItems(assets)

        if selectAsset:
            self.logger.debug('Selecting asset: {0}'.format(selectAsset))
            self.selectItem(selectAsset)