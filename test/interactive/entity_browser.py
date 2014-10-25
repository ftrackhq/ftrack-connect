# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import functools

from PySide import QtGui, QtCore

import ftrack_connect.ui.widget.entity_browser
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        widget = ftrack_connect.ui.widget.entity_browser.EntityBrowser()
        widget.setMinimumSize(600, 400)
        self._browser = widget
        return widget

    def constructController(self, widget):
        '''Return controller for *widget*.'''
        controlWidget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        controlWidget.setLayout(layout)

        self._location = QtGui.QLineEdit()
        layout.addWidget(self._location)

        self._applyButton = QtGui.QPushButton('Apply')
        layout.addWidget(self._applyButton)

        self._location.returnPressed.connect(self._applyButton.click)
        self._applyButton.clicked.connect(self.setLocation)
        widget.locationChanged.connect(self._updateLocation)

        return controlWidget

    def setLocation(self):
        '''Set location to currently entered value.'''
        locationParts = self._location.text().split('/')
        location = []
        for part in locationParts:
            part = part.strip()
            if part:
                location.append(part)

        self._browser.setLocation(location)

    def _updateLocation(self):
        '''Update displayed location.'''
        location = self._browser.getLocation()
        self._location.setText(' / '.join(location))


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
