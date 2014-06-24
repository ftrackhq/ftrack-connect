# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys
import traceback
import cStringIO

from PySide import QtGui, QtCore


class UncaughtError(QtGui.QMessageBox):
    '''Widget that handles uncaught errors and presents a message box.'''

    onError = QtCore.Signal(object, object, object)

    def __init__(self, *args, **kwargs):
        '''Initialise and setup widget.'''
        super(UncaughtError, self).__init__(*args, **kwargs)
        self.setIcon(QtGui.QMessageBox.Critical)
        self.onError.connect(self.exceptHook)

        # Listen to all unhandled exceptions.
        sys.excepthook = self.onError.emit

    def getTraceback(self, exceptionTraceback):
        '''Return message from traceback.'''
        tracebackInfoStream = cStringIO.StringIO()
        traceback.print_tb(
            exceptionTraceback,
            None,
            tracebackInfoStream
        )
        tracebackInfoStream.seek(0)
        return tracebackInfoStream.read()

    def exceptHook(self, exceptionType, exceptionValue, exceptionTraceback):
        '''Show message box with error details.'''

        # Print exception to console.
        traceback.print_tb(exceptionTraceback)
        print(exceptionValue)

        # Show exception to user.
        tracebackInfo = self.getTraceback(exceptionTraceback)
        self.setDetailedText(tracebackInfo)
        self.setText(str(exceptionValue))
        self.exec_()

    def resizeEvent(self, event):
        '''Hook into the resize event and force width of detailed text.'''
        result = super(UncaughtError, self).resizeEvent(event)

        details_box = self.findChild(QtGui.QTextEdit)
        if details_box is not None:
            details_box.setFixedSize(500, 200)

        return result
