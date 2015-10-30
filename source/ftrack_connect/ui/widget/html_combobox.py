# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from PySide import QtGui

import ftrack_connect.ui.widget.html_delegate


class HtmlComboBox(QtGui.QComboBox):
    '''Combo box that draws items with html.'''

    def __init__(self, formatter, *args, **kwargs):
        self.format = formatter
        super(HtmlComboBox, self).__init__(*args, **kwargs)
        self.setItemDelegate(
            ftrack_connect.ui.widget.html_delegate.HtmlDelegate(formatter)
        )
