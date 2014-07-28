# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui

import ftrack_connect.ui.widget.timer
from harness import Harness


class WidgetHarness(Harness):
    '''Test harness for widget.'''

    def constructWidget(self):
        '''Return widget instance to test.'''
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        self._timer = timer = ftrack_connect.ui.widget.timer.Timer(
            title='Compositing',
            description=('drones / sequence / a very very / long path / that '
                         'should be / elided / is-cu / station')
        )
        layout.addWidget(timer, stretch=0)

        divider = QtGui.QFrame()
        divider.setFrameShape(QtGui.QFrame.HLine)
        layout.addWidget(divider)

        driverLayout = QtGui.QHBoxLayout()
        layout.addLayout(driverLayout)

        self._timeInput = timeInput = QtGui.QSpinBox()
        timeInput.setRange(0, 999 * 60 * 60)
        driverLayout.addWidget(timeInput)

        applyButton = QtGui.QPushButton('Apply')
        driverLayout.addWidget(applyButton)

        applyButton.clicked.connect(self.setTime)
        self._timer.timeEdited.connect(self._onTimeCommit)
        self._timer.stopped.connect(self._onTimeCommit)

        widget.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed
        )

        return widget

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
