# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from PySide import QtGui
import ftrack_legacy

from ftrack_connect.ui.widget import notification_list as _notification_list
from harness import Harness


ftrack_legacy.setup()


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)

        notificationList = _notification_list.Notification()

        layout.addWidget(notificationList)

        notificationList.addContext(
            '879f4658-c4dd-11e1-bf78-f23c91df25eb', 'task', False
        )

        notificationList.addContext(
            '01cfdcaa-c5ea-11e1-adec-f23c91df25eb', 'asset', False
        )

        notificationList.reload()

        return widget


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
