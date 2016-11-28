# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack


# :TODO: Move to ftrack-connect-pipeline.

import ftrack_connect.asynchronous


class Scanner(object):
    '''Scan for new versions.'''

    def __init__(self, session, result_handler):
        '''Instantiate scanner with *session*.'''
        self._session = session
        self.result_handler = result_handler
        super(Scanner, self).__init__()

    @ftrack_connect.asynchronous.asynchronous
    def scan(self, items):
        '''Search for new versions of *items*.'''
        if not items:
            return []
        selects = [
            'asset.versions.components.name',
            'version'
        ]

        asset_version_ids = [item['asset_version_id'] for item in items]
        query_string = 'select {0} from AssetVersion where id in ({1})'.format(
            ', '.join(selects), ', '.join(asset_version_ids)
        )

        result_lookup = dict()
        for asset_version in self._session.query(query_string):
            result_lookup[asset_version['id']] = asset_version

        result = []
        for item in items:
            component_name = item['component_name']
            asset_version = result_lookup.get(item['asset_version_id'])
            if asset_version is None:
                # No version with the given id was found. This can happen if the
                # version with the given id has been removed.
                result.append(None)
            else:

                latest_asset_version = asset_version

                for related_asset_version in asset_version['asset']['versions']:
                    if (

                        # Is the version later than the current one.
                        latest_asset_version['version'] <
                        related_asset_version['version'] and

                        # Does the version contain the component name.
                        any([
                            component['name'] == component_name
                            for component in related_asset_version['components']
                        ])
                    ):
                        latest_asset_version = related_asset_version

                result.append({
                    'current_version': asset_version['version'],
                    'latest_version': latest_asset_version['version'],
                    'current_asset_version_id': asset_version['id'],
                    'latest_asset_version_id': latest_asset_version['id']
                })

        self.result_handler(result)
