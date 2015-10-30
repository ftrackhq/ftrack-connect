# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack


import ftrack_connect.ui.widget.html_combobox
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def format(self, data):
        '''Return data formatted as string.'''
        return (
            '<b>{}</b><br/>{}'
            .format(data.get('title'), data.get('description'))
        )

    def constructWidget(self):
        '''Return widget instance to test.'''
        widget = ftrack_connect.ui.widget.html_combobox.HtmlComboBox(
            self.format
        )

        for index in range(10):
            widget.addItem(
                'Item {0}'.format(index),
                userData={
                    'title': 'My template',
                    'description': 'Lorum ipsum be nadi'
                }
            )

        widget.setMinimumWidth(700)
        return widget


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
