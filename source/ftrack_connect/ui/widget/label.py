# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore


class Label(QtGui.QLabel):
    '''Label that can elide displayed text automatically.'''

    def __init__(self, elideMode=QtCore.Qt.ElideMiddle, *args, **kwargs):
        '''Instantiate label with *elideMode*.

        If *elideMode* is not specified it defaults to
        :py:class:`QtCore.Qt.ElideMiddle.`

        '''
        self.elideMode = elideMode
        super(Label, self).__init__(*args, **kwargs)

        # Ignore horizontal minimum size so that the label can shrink and make
        # use of eliding. Note the label will still try to take as much
        # horizontal space as possible.
        self.setSizePolicy(
            QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Fixed
        )

    def paintEvent(self, event):
        '''Paint *event* with the configured elideMode.'''
        painter = QtGui.QPainter(self)

        metrics = QtGui.QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), self.elideMode, self.width())

        painter.drawText(self.rect(), self.alignment(), elided)
