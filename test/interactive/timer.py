# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import ftrack_connect.ui.widget.timer
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        return ftrack_connect.ui.widget.timer.Timer(
            title='Compositing',
            description=('drones / sequence / a very very / long path / that '
                         'should be / elided / is-cu / station')
        )


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
