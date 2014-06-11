# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import ftrack_connect.widget.component
import ftrack_connect.widget.item_list


class ComponentsList(ftrack_connect.widget.item_list.ItemList):
    '''List components with support for dynamic addition and removal.

    The component list is managed using an internal model.

    '''

    def __init__(self, parent=None):
        '''Initialise widget with *parent*.'''
        super(ComponentsList, self).__init__(
            widgetFactory=ftrack_connect.widget.component.Component,
            widgetItem=lambda widget: widget.value(),
            parent=parent
        )

    def onAddButtonClick(self):
        '''Handle add button click.'''
        super(ComponentsList, self).onAddButtonClick()

        row = self._list.count() - 1
        widget = self._list.widgetAt(row)

        # TODO: Use signals.
        #widget.onBrowse()
