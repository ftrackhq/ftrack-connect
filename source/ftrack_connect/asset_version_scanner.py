# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack


# :TODO: Move to ftrack-connect-pipeline.

import logging

import ftrack_connect.asynchronous


class Scanner(object):
    '''Scan for new versions.'''

    def __init__(self, session, result_handler):
        '''Instantiate scanner with *session*.'''
        self._session = session
        self.result_handler = result_handler
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        super(Scanner, self).__init__()

    @ftrack_connect.asynchronous.asynchronous
    def scan(self, items):
        '''Search for new versions of *items* and call handler with result.

        *items* should be a list of dictionaries containing `asset_version_id`
        and `component_name`.

        The result_handler will be called with a list of dictionaries containing
        `scanned` and `latest` dictionaries with the following keys.

        `scanned`:

        *   id - id of the asset version.
        *   version - version number of the asset version.

        `latest`:

        *   id - id of the asset version.
        *   version - version number of the asset version.

        The result may contain None instead of a dictionary if the asset
        version scanned is not found on the server.

        '''
        if not items:
            self.result_handler([])
            return

        self.logger.debug('Scanning for assets on {0!r}.'.format(items))

        selects = [
            'asset.versions.version',
            'version'
        ]

        asset_version_ids = [item['asset_version_id'] for item in items]
        query_string = 'select {0} from AssetVersion where id in ({1})'.format(
            ', '.join(selects), ', '.join(asset_version_ids)
        )

        all_related_version_ids = []
        result_lookup = dict()
        for asset_version in self._session.query(query_string):
            result_lookup[asset_version['id']] = asset_version
            for related_asset_version in asset_version['asset']['versions']:
                all_related_version_ids.append(related_asset_version['id'])

        if all_related_version_ids:
            # Because of bug in 3.3.X backend we need to divide the query. The
            # memory cache will allow using entities without caring about this.
            self._session.query(
                'select components.name from AssetVersion where id in '
                '({0})'.format(', '.join(all_related_version_ids))
            ).all()

        result = []
        for item in items:
            asset_version = result_lookup.get(item['asset_version_id'])

            self.logger.debug(
                'Found asset version {0!r} for {1!r}.'.format(
                    asset_version,
                    item['asset_version_id']
                )
            )
            if asset_version is None:
                # No version with the given id was found. This can happen if the
                # version with the given id has been removed.
                result.append(None)
                self.logger.debug(
                    'Asset version with id {0!r} could not be found.'.format(
                        item['asset_version_id']
                    )
                )
            else:
                component_name = item['component_name']
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

                latest = {
                    'id': latest_asset_version['id'],
                    'version': latest_asset_version['version']
                }
                scanned = {
                    'id': asset_version['id'],
                    'version': asset_version['version']
                }
                self.logger.debug(
                    'Scanned {0!r} and found latest version: {1!r} for '
                    'component with name {2!r}.'.format(
                        scanned, latest, component_name
                    )
                )

                if latest_asset_version['id'] != asset_version['id']:
                    self.logger.info(
                        'Found a new asset version of {0!r}: {1!r}'.format(
                            scanned, latest
                        )
                    )

                result.append({
                    'scanned': scanned,
                    'latest': latest
                })

        self.result_handler(result)
