# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import uuid
import sys
import signal

from PySide import QtGui

import ftrack_connect.ui.widget.components_list
import ftrack_connect.ui.widget.item_selector

# Enable ctrl+c to quit application when started from command line.
signal.signal(signal.SIGINT, signal.SIG_DFL)


def main(arguments=None):
    '''Interactive test of item selector.

    Uses a component list as data source.

    '''
    application = QtGui.QApplication(arguments)

    dialog = QtGui.QWidget()
    layout = QtGui.QVBoxLayout()
    dialog.setLayout(layout)

    # Create components selector
    selector = ftrack_connect.ui.widget.item_selector.ItemSelector(
        labelField='componentName',
        defaultLabel='Unnamed component',
        emptyLabel='Select component to use as preview'
    )

    # Create components list
    componentsList = ftrack_connect.ui.widget.components_list.ComponentsList()

    # Create a button to add new components
    def _addComponent():
        fileName = str(uuid.uuid4())[:6]
        componentsList.addItem({
            'resourceIdentifier': '/path/to/{}.ext'.format(fileName)
        })
    addComponentButton = QtGui.QPushButton('Add component')
    addComponentButton.clicked.connect(_addComponent)

    # Connect itemsChanged to update selector when list changes.
    def _onItemsChanged():
        selector.setItems(componentsList.items())
    componentsList.itemsChanged.connect(_onItemsChanged)

    # Add widgets and show dialog.
    layout.addWidget(addComponentButton)
    layout.addWidget(componentsList)
    layout.addWidget(selector)
    dialog.resize(640, 480)
    dialog.show()
    
    sys.exit(application.exec_())


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
