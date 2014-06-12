# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import harmony.ui.filesystem_browser

import ftrack_connect.widget.component
import ftrack_connect.widget.item_list


class ComponentsList(ftrack_connect.widget.item_list.ItemList):
    '''List components with support for dynamic addition and removal.

    The component list is managed using an internal model.

    '''

    def __init__(self, parent=None):
        '''Initialise widget with *parent*.'''
        super(ComponentsList, self).__init__(
            widgetFactory=self._createComponentWidget,
            widgetItem=lambda widget: widget.value(),
            parent=parent
        )

        # Use common browser widget for every component.
        self.browser = harmony.ui.filesystem_browser.FilesystemBrowser(
            parent=self
        )
        self.browser.setMinimumSize(900, 500)

    def _createComponentWidget(self, item):
        '''Return component widget for *item*.'''
        options = {}
        if item is not None:
            options = {}

        options.setdefault('browser', self.browser)
        return ftrack_connect.widget.component.Component(**options)

    def onAddButtonClick(self):
        '''Handle add button click.'''
        super(ComponentsList, self).onAddButtonClick()

        row = self.list.count() - 1
        widget = self.list.widgetAt(row)

        # TODO: Use signals.
        widget.browse()
