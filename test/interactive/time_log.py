# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import ftrack_connect.ui.widget.time_log
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        return ftrack_connect.ui.widget.time_log.TimeLog(
            title='Compositing',
            description=('drones / sequence / a very very / long path / that '
                         'should be / elided / is-cu / station'),
            data={'entityId': 12214}
        )


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
