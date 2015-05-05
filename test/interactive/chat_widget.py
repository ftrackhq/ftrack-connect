# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import random
import datetime
import uuid

import ftrack
from PySide import QtCore, QtGui

from harness import Harness

import ftrack_connect.ui.widget.chat


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        ftrack.setup()

        users = ftrack.getUsers()
        me = users.pop()
        you = users.pop()

        self.chat = ftrack_connect.ui.widget.chat.Chat()

        history = []
        for text in (
            'Hi!', 'How are you?', 'Good!', 'You?', 'Great!', 'Thanks!'
        ):
            sender, receiver = random.choice([
                (me, you), (you, me)
            ])
            history.append(dict(
                text=text,
                receiver=receiver.getId(),
                sender=dict(
                    id=sender.getId(),
                    name=sender.getName()
                ),
                date=str(datetime.datetime.utcnow()),
                id=str(uuid.uuid1()),
                me=(sender == me)
            ))

        self.chat.load(history)

        return self.chat

if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
