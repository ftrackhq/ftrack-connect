# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack


import ftrack_connect.ui.widget.import_asset
from harness import Harness

import connector


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        dialog = ftrack_connect.ui.widget.import_asset.FtrackImportAssetDialog(
            connector=connector.TestConnector(
                components=[
                    ('69eea69c-bb2e-11e4-85e2-20c9d081909b', 'Foo')
                ]
            )
        )
        return dialog


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
