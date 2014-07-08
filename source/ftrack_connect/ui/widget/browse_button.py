# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging
import os

from PySide import QtGui, QtCore
import riffle.browser
import clique


class BrowseButton(QtGui.QFrame):
    '''File browser widget.'''

    fileSelected = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        '''Initialise browser widget.'''
        super(BrowseButton, self).__init__(*args, **kwargs)

        self.log = logging.getLogger(__name__ + '.' + self.__class__.__name__)
        self.setAcceptDrops(True)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        bottomCenterAlignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter
        topCenterAlignment = QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter

        self._label = QtGui.QLabel('Drop files here or')
        layout.addWidget(
            self._label,
            alignment=bottomCenterAlignment
        )

        self._browseButton = QtGui.QPushButton('Browse')

        self._browseButton.setToolTip('Browse for file(s).')
        self.setObjectName('publisher-browsebutton')

        layout.addWidget(
            self._browseButton, alignment=topCenterAlignment
        )

        self._dialog = riffle.browser.FilesystemBrowser(parent=self)
        self._dialog.setMinimumSize(900, 500)

        self._setupConnections()

    def _setupConnections(self):
        '''Setup connections to signals.'''
        self._browseButton.clicked.connect(self._browse)

    def _browse(self):
        '''Show browse dialog and emit fileSelected signal on file select.'''
        if self._dialog.exec_():
            selected = self._dialog.selected()
            if selected:
                self.fileSelected.emit(selected[0])

    def _updateStyle(self, key, value):
        self.setProperty(key, value)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def clear(self):
        '''Clear the browser to it's initial state.'''
        self._dialog.setLocation('')

    def dragEnterEvent(self, event):
        '''Ovverride dragEnterEvent and accept all events.'''
        event.setDropAction(QtCore.Qt.CopyAction)
        event.accept()
        self._updateStyle('styleCls', 'ft-drag-over')

    def dragLeaveEvent(self, event):
        event.accept()
        self._updateStyle('styleCls', None)

    def dropEvent(self, event):
        '''Handle dropped file event.'''
        self._updateStyle('styleCls', None)

        # TODO: Allow hook into the dropEvent.
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                paths.append(path)
                self.log.debug('Dropped file: {0}'.format(path))

        sequences, singles = clique.assemble(paths)

        self.log.debug('Sequences: {0}'.format(sequences))
        self.log.debug('Singles: {0}'.format(singles))

        for sequence in sequences:
            self.fileSelected.emit(sequence.format())

        for path in singles:
            self.fileSelected.emit(path)
