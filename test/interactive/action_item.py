# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui

from ftrack_connect.ui.widget.action_item import ActionItem
from ftrack_connect.ui.widget.flow_layout import ScrollingFlowWidget
from harness import Harness


ACTIONS = [
    [dict(
        label='Mega Modeling 2014',
        actionIdentifier='my-action-callback-identifier',
        icon='http://cdn.sstatic.net/stackoverflow/img/logo-10m.svg?v=fc0904eba1b1',
        actionData=dict(
            applicationIdentifier='mega_modeling_2014'
        )
    )],
    [dict(
        label='Professional Painter',
        icon='photoshop',
        variant='v1',
        actionIdentifier='my-action-callback-identifier',
        actionData=dict(
            applicationIdentifier='professional_painter'
        )
    ),dict(
        label='Professional Painter',
        icon='photoshop',
        variant='v2',
        actionIdentifier='my-action-callback-identifier',
        actionData=dict(
            applicationIdentifier='professional_painter'
        )
    )],
    [dict(
        label='Cool Compositor v2',
        actionIdentifier='my-action-callback-identifier',
        actionData=dict(
            cc_plugins=['foo', 'bar'],
            applicationIdentifier='cc_v2'
        )
    )]
]

class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget2(self):
        '''Return widget instance to test.'''
        widget = QtGui.QListView()
        widget.setViewMode(QtGui.QListView.IconMode)
        widget.setWordWrap(True)
        widget.setSpacing(10)
        widget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        widget.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        widget.setModel(QtGui.QStandardItemModel(widget))

        for item in ACTIONS:
            widget.model().appendRow(ActionItem(item))

        widget.setMouseTracking(True)
        widget.entered.connect(self._onEntered)
        widget.clicked.connect(self._onClicked)

        self._view = widget
        return widget


    def constructWidget(self):
        '''Return widget instance to test.'''
        widget = ScrollingFlowWidget()

        for item in 10*ACTIONS:
            widget.addWidget(ActionItem(item))

        self._view = widget
        return widget


    def _onEntered(self, currentIndex):
        print 'entered', currentIndex
        item = self._view.model().itemFromIndex(currentIndex)
        item.entered()

    def _onClicked(self, currentIndex):
        print 'clicked', currentIndex
        item = self._view.model().itemFromIndex(currentIndex)
        item.clicked()

    def constructController(self, widget):
        '''Return controller for *widget*.'''
        controlWidget = QtGui.QWidget()
        controlLayout = QtGui.QVBoxLayout()
        controlWidget.setLayout(controlLayout)
        return controlWidget


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
