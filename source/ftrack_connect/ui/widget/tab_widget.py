# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from qtpy import QtWidgets


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, *args, **kwargs):
        '''Instantiate the tab widget.'''
        super(TabWidget, self).__init__(*args, **kwargs)
