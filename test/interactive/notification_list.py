# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import getpass

from PySide import QtGui
import ftrack
import ftrack_api

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
            ftrack.User(getpass.getuser()).getId(), 'user', False
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

        def getEvents(event):
            '''Return events for context.'''
            context = notificationList._context
            cases = []
            events = []

            session = ftrack_api.Session()

            if context['asset']:
                cases.append(
                    '(feeds.owner_id in ({asset_ids}) and action is '
                    '"asset.published")'.format(
                        asset_ids=','.join(context['asset'])
                    )
                )

            if context['task']:
                cases.append(
                    'parent_id in ({task_ids}) and action in '
                    '("change.status.shot", "change.status.task")'.format(
                        task_ids=','.join(context['task'])
                    )
                )

                cases.append(
                    '(parent_id in ({task_ids}) and action in '
                    '("update.custom_attribute.fend", "update.custom_attribute.fstart"))'.format(
                        task_ids=','.join(context['task'])
                    )
                )

            if context['user']:
                cases.append(
                    '(feeds.owner_id in ({user_ids}) and action is '
                    '"db.append.task:user" and feeds.distance is "0" '
                    'and feeds.relation is "assigned")'.format(
                        user_ids=','.join(context['user'])
                    )
                )

            if cases:
                events = session.query(
                    'select id, action, parent_id, parent_type, created_at, data '
                    'from Event where {0}'.format(' or '.join(cases))
                ).all()

                events.sort(
                    key=lambda event: event['created_at'], reverse=True
                )

            return events

        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.crew.notification.get-events',
            getEvents
        )

        return widget


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
