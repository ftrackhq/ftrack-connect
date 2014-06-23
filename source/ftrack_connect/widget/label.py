# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore


class Label(QtGui.QLabel):
    '''Label that add support for elide mode.'''

    def __init__(self, elideMode=QtCore.Qt.ElideMiddle, *args, **kwargs):
        '''Instansiate with *elideMode*.

        If *elideMode* is not specified it defaults to
        :py:class:`QtCore.Qt.ElideMiddle.`

        '''
        self.elideMode = elideMode
        super(Label, self).__init__(*args, **kwargs)

    def paintEvent(self, event):
        '''Paint *event* with the configured elideMode.'''
        painter = QtGui.QPainter(self)

        metrics = QtGui.QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), self.elideMode, self.width())

        painter.drawText(self.rect(), self.alignment(), elided)
