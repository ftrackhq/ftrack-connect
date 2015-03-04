# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore


def applyTheme(widget, theme='light', baseTheme=None):
    '''Apply *theme* to *widget*.'''
    # Set base style.
    if baseTheme and QtGui.QApplication.style().objectName() != baseTheme:
        QtGui.QApplication.setStyle(baseTheme)

    # Load main font file
    QtGui.QFontDatabase.addApplicationFont(
        ':/ftrack/font/main'
    )

    # Load stylesheet from resource file and apply.
    fileObject = QtCore.QFile(':/ftrack/style/{0}'.format(theme))
    fileObject.open(
        QtCore.QFile.ReadOnly | QtCore.QFile.Text
    )
    stream = QtCore.QTextStream(fileObject)
    styleSheetContent = stream.readAll()

    widget.setStyleSheet(styleSheetContent)
