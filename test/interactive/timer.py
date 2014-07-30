# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui

import ftrack_connect.ui.widget.timer
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        self._timer = ftrack_connect.ui.widget.timer.Timer(
            title='Compositing',
            description=('drones / sequence / a very very / long path / that '
                         'should be / elided / is-cu / station')
        )
        return self._timer

    def constructController(self, widget):
        '''Return controller for *widget*.'''
        controlWidget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        controlWidget.setLayout(layout)

        self._timeInput = QtGui.QSpinBox()
        self._timeInput.setRange(0, 999 * 60 * 60)
        layout.addWidget(self._timeInput)

        applyButton = QtGui.QPushButton('Apply')
        layout.addWidget(applyButton)

        applyButton.clicked.connect(self.setTime)
        widget.timeEdited.connect(self._onTimeCommit)
        widget.stopped.connect(self._onTimeCommit)

        return controlWidget

    def setTime(self):
        '''Set time.'''
        time = self._timeInput.value()
        self._timer.setTime(time)

    def _onTimeCommit(self, time):
        '''Commit *time*.'''
        print('Committing time value of {0}'.format(time))


if __name__ == '__main__':
    raise SystemExit(
        WidgetHarness().run()
    )
