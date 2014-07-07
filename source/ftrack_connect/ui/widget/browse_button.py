# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore
import riffle.browser


class BrowseButton(QtGui.QPushButton):
    '''File browser widget.'''

    fileSelected = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        '''Initialise browser widget.'''
        super(BrowseButton, self).__init__(*args, **kwargs)
        self.setToolTip('Browse for file(s).')
        self.setObjectName('publisher-browsebutton')
        self._dialog = riffle.browser.FilesystemBrowser(parent=self)
        self._dialog.setMinimumSize(900, 500)

        self._setupConnections()

    def _setupConnections(self):
        '''Setup connections to signals.'''
        self.clicked.connect(self._browse)

    def _browse(self):
        '''Show browse dialog and emit fileSelected signal on file select.'''
        if self._dialog.exec_():
            selected = self._dialog.selected()
            if selected:
                self.fileSelected.emit(selected[0])

    def clear(self):
        '''Clear the browser to it's initial state.'''
        self._dialog.setLocation('')
