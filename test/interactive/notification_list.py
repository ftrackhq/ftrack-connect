# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from PySide import QtGui
import ftrack

from ftrack_connect.ui.widget import notification_list as _notification_list
from harness import Harness


ftrack.setup()


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)

        notificationList = _notification_list.Notification()

        notificationList.setStyleSheet('''

            QPushButton {
                border: 1px solid black;
                border-radius: 2px;
                background-color: #505050;
                color: #F0F0F0;
                padding: 4px;
                min-width: 80px;
            }

            QFrame {
                background-color: #2A2A2A;
                color: #969696;
            }

            QLabel {
                background-color: #323232;
            }

            QFrame#notification-list {
                border: 0;
                margin: 20px 0 0 0;
            }

            QFrame#notification-list QTableWidget {
                background-color: transparent;
                border: 0;
            }

            QFrame#notification-list QTableWidget::item {
                background-color: #323232;
                border-bottom: 1px solid #282828;
                padding: 0;
            }
        ''')

        layout.addWidget(notificationList)

        notificationList.addContext(
            '157271fc-5fc6-11e2-a771-f23c91df25eb', 'task', False
        )

        notificationList.addContext(
            '01cfdcaa-c5ea-11e1-adec-f23c91df25eb', 'asset', False
        )

        notificationList.addContext(
            '01cfdcaa-c5ea-11e1-adec-f23c91df25es', 'asset', False
        )

        notificationList.removeContext(
            '01cfdcaa-c5ea-11e1-adec-f23c91df25es', False
        )

        notificationList.reload()

        return widget


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
