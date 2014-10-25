# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import ftrack_connect.ui.widget.entity_browser
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        widget = ftrack_connect.ui.widget.entity_browser.EntityBrowser()
        widget.setMinimumSize(600, 400)
        return widget


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
