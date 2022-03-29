# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from ftrack_connect.qt import QtCore, QtWidgets, QtGui


def applyFont():
    '''Add application font.'''
    fonts = [':/ftrack/font/regular', ':/ftrack/font/medium']
    for font in fonts:
        QtGui.QFontDatabase.addApplicationFont(font)


def applyTheme(widget, theme='light', baseTheme=None):
    '''Apply *theme* to *widget*.'''
    # Set base style.
    if baseTheme and QtWidgets.QApplication.style().objectName() != baseTheme:
        QtWidgets.QApplication.setStyle(baseTheme)

    # Load stylesheet from resource file and apply.
    fileObject = QtCore.QFile(':/ftrack/style/{0}'.format(theme))
    fileObject.open(
        QtCore.QFile.ReadOnly | QtCore.QFile.Text
    )
    stream = QtCore.QTextStream(fileObject)
    styleSheetContent = stream.readAll()

    widget.setStyleSheet(styleSheetContent)
