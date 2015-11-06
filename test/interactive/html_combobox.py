# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import ftrack_connect.ui.widget.html_combobox
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def format(self, data):
        '''Return data formatted as string.'''
        return (
            '<b>{}</b><br/><div style="color: green">{}</div>'
            .format(
                data.get('title'),
                data.get('description')
            )
        )

    def constructWidget(self):
        '''Return widget instance to test.'''
        widget = ftrack_connect.ui.widget.html_combobox.HtmlComboBox(
            self.format
        )

        for index in range(10):
            title = 'Item {0}'.format(index)
            widget.addItem(
                title,
                userData={
                    'title': title,
                    'description': (
                        'Lorem ipsum dolor sit amet, consectetur adipiscing '
                        'elit. Donec a diam lectus. Sed sit amet ipsum mauris.'
                        'Maecenas congue ligula ac quam viverra nec consectetur'
                        'ante hendrerit. Donec et mollis dolor. Praesent et '
                        'diameget libero egestas mattis sit amet vitae augue. '
                        'Nam tincidunt congue enim, ut porta lorem lacinia '
                        'consectetur.'
                    )
                }
            )

        widget.setMinimumWidth(700)
        return widget


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
