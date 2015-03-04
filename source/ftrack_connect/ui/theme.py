# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore


def applyTheme(widget, theme='light'):
    '''Apply *theme* to *widget*.'''
    # Set base style.
    if theme != 'integration':
        if QtGui.QApplication.style().objectName() != 'cleanlooks':
            QtGui.QApplication.setStyle('cleanlooks')

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
