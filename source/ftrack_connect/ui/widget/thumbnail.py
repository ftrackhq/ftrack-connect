# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

from PySide import QtGui, QtCore

import ftrack_connect.error

# Thumbnail limits from ftrack server.
THUMBNAIL_UPLOAD_MAX_SIZE = 10 * (1024 ** 2)  # 10 MiB in Bytes
THUMBNAIL_UPLOAD_VALID_FILE_TYPES = (
    'bmp', 'gif', 'jpeg', 'jpg', 'png', 'tif', 'tiff'
)


class ConnectThumbnailValidationError(ftrack_connect.error.ConnectError):
    '''ftrack connect thumbnail validation error.'''
    pass


class Thumbnail(QtGui.QFrame):
    '''Thumbnail widget with support for drag and drop and preview.'''

    def __init__(self, *args, **kwargs):
        '''Initialise widget.'''
        super(Thumbnail, self).__init__(*args, **kwargs)

        self.setObjectName('thumbnail')

        layout = QtGui.QHBoxLayout()
        layout.addSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.setAcceptDrops(True)
        self.setProperty('ftrackDropArea', True)

        self._filePath = None
        self._imageWidth = 200
        self._imageHeight = 50

        self.imageLabel = QtGui.QLabel()
        self._setDropAreaText()
        layout.addWidget(self.imageLabel, alignment=QtCore.Qt.AlignLeft)

        # TODO: Add theme support.
        removeIcon = QtGui.QIcon(
            QtGui.QPixmap(':/ftrack/image/light/trash')
        )
        self.removeButton = QtGui.QPushButton()
        self.removeButton.setVisible(False)
        self.removeButton.setFlat(True)
        self.removeButton.setIcon(removeIcon)
        self.removeButton.clicked.connect(self.removeThumbnail)
        layout.addWidget(self.removeButton, alignment=QtCore.Qt.AlignRight)

    def _getFilePathFromEvent(self, event):
        '''Get file path from *event*.

        Raises *ConnectThumbnailValidationError* if an invalid or unsupported
        file is added.
        '''
        # Validate single url
        urls = event.mimeData().urls()
        if len(urls) != 1:
            raise ConnectThumbnailValidationError(
                'Multiple files not supported.'
            )

        # Validate local file
        filePath = urls[0].toLocalFile()
        if not os.path.isfile(filePath):
            raise ConnectThumbnailValidationError('Not a valid file.')

        # Validate file extension
        fileExtension = os.path.splitext(filePath)[1][1:].lower()
        if not fileExtension in THUMBNAIL_UPLOAD_VALID_FILE_TYPES:
            raise ConnectThumbnailValidationError('Invalid file type.')

        # Validate file size
        fileSize = os.path.getsize(filePath)
        if fileSize > THUMBNAIL_UPLOAD_MAX_SIZE:
            raise ConnectThumbnailValidationError(
                'File size is above allowed maximum.'
            )

        return filePath

    def showThumbnail(self):
        '''Show current thumbnail.'''
        pixmap = QtGui.QPixmap(self._filePath).scaled(
            self._imageWidth, self._imageHeight, QtCore.Qt.KeepAspectRatio
        )
        self.imageLabel.setPixmap(pixmap)
        self.removeButton.setVisible(True)

    def _setDropAreaText(self):
        '''Set drop area label.'''
        self.imageLabel.setText('Drop a file here to add a thumbnail.')

    def removeThumbnail(self):
        '''Remove thumbnail.'''
        self._setDropAreaText()
        self._filePath = None
        self.removeButton.setVisible(False)

    def _setDropAreaState(self, state='default'):
        '''Set drop area state to *state*.

        *state* should be 'default', 'active' or 'invalid'.

        '''
        self.setProperty('ftrackDropAreaState', state)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def dragEnterEvent(self, event):
        '''Validate file and set state when entering drop area.'''
        try:
            self._getFilePathFromEvent(event)
            self._setDropAreaState('active')
            event.setDropAction(QtCore.Qt.CopyAction)
        except ConnectThumbnailValidationError:
            self._setDropAreaState('invalid')
            event.setDropAction(QtCore.Qt.IgnoreAction)
        event.accept()

    def dragLeaveEvent(self, event):
        '''Reset state when leaving drop area.'''
        self._setDropAreaState()

    def _isThumbnailReplaceConfirmed(self):
        '''Confirm replacement if a thumbnail is set.'''
        if not self._filePath:
            return True

        response = QtGui.QMessageBox.question(
            self,
            'Replace thumbnail',
            'Do you want to replace the current thumbnail?',
            (
                QtGui.QMessageBox.StandardButton.Yes |
                QtGui.QMessageBox.StandardButton.No
            )
        )
        return (response == QtGui.QMessageBox.StandardButton.Yes)

    def dropEvent(self, event):
        '''Validate and set thumbnail when a file is droppped.'''
        self._setDropAreaState()
        try:
            filePath = self._getFilePathFromEvent(event)
            if self._isThumbnailReplaceConfirmed():
                self._filePath = filePath
                self.showThumbnail()

        except ConnectThumbnailValidationError as error:
            QtGui.QMessageBox.warning(
                self, 'Invalid thumbnail', error.message
            )

    def getFilePath(self):
        '''Return image filePath for thumbnail.'''
        return self._filePath
