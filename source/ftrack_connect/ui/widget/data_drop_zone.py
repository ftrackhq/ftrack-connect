# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import re
import logging

from QtExt import QtCore
from QtExt import QtWidgets

import riffle.browser
import riffle.model

import clique
import clique.collection
import clique.sorted_set


def __init__(self, head, tail, padding, indexes=None):
    '''Initialise collection.
    *head* is the leading common part whilst *tail* is the trailing
    common part.
    *padding* specifies the "width" of the numerical component. An index
    will be padded with zeros to fill this width. A *padding* of zero
    implies no padding and width may be any size so long as no leading
    zeros are present.
    *indexes* can specify a set of numerical indexes to initially populate
    the collection with.
    .. note::
        After instantiation, the ``indexes`` attribute cannot be set to a
        new value using assignment::
            >>> collection.indexes = [1, 2, 3]
            AttributeError: Cannot set attribute defined as unsettable.
        Instead, manipulate it directly::
            >>> collection.indexes.clear()
            >>> collection.indexes.update([1, 2, 3])
    '''
    super(clique.collection.Collection, self).__init__()
    self.__dict__['indexes'] = clique.sorted_set.SortedSet()
    try:
        head = head.encode('utf-8')
    except UnicodeDecodeError:
        pass

    try:
        tail = tail.encode('utf-8')
    except UnicodeDecodeError:
        pass

    self._head = head
    self._tail = tail
    self.padding = padding
    self._update_expression()

    if indexes is not None:
        self.indexes.update(indexes)

clique.collection.Collection.__init__ = __init__


def data(self, index, role):
    '''Return data for *index* according to *role*.'''
    if not index.isValid():
        return None

    column = index.column()
    item = index.internalPointer()

    if role == self.ITEM_ROLE:
        return item

    elif role == QtCore.Qt.DisplayRole:

        if column == 0:
            # Convert to unicode.
            if isinstance(item.name, str):
                return item.name.decode('utf-8')

            return item.name
        elif column == 1:
            if item.size:
                return item.size
        elif column == 2:
            return item.type
        elif column == 3:
            if item.modified is not None:
                # Convert to unicode.
                return item.modified.strftime('%c').decode('utf-8')

    elif role ==  QtCore.Qt.DecorationRole:
        if column == 0:
            return self.iconFactory.icon(item)

    elif role ==  QtCore.Qt.TextAlignmentRole:
        if column == 1:
            return  QtCore.Qt.AlignRight
        else:
            return  QtCore.Qt.AlignLeft

riffle.model.Filesystem.data = data


class DataDropZone(QtWidgets.QFrame):
    '''Data drop zone widget.'''

    dataSelected = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        '''Initialise DataDropZone widget.'''
        super(DataDropZone, self).__init__(*args, **kwargs)

        self.log = logging.getLogger(__name__ + '.' + self.__class__.__name__)
        self.setAcceptDrops(True)
        self.setObjectName('ftrack-connect-publisher-browse-button')
        self.setProperty('ftrackDropZone', True)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        bottomCenterAlignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter
        topCenterAlignment = QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter

        self._label = QtWidgets.QLabel('Drop files here or')
        layout.addWidget(
            self._label,
            alignment=bottomCenterAlignment
        )

        self._browseButton = QtWidgets.QPushButton('Browse')
        self._browseButton.setToolTip('Browse for file(s).')
        layout.addWidget(
            self._browseButton, alignment=topCenterAlignment
        )

        self._setupConnections()

        homeFolder = os.path.expanduser('~')
        if os.path.isdir(homeFolder):
            self._currentLocation = homeFolder

    def _setupConnections(self):
        '''Setup connections to signals.'''
        self._browseButton.clicked.connect(self._browse)

    def _browse(self):
        '''Show browse dialog and emit dataSelected signal on file select.'''
        # Recreate browser on each browse to avoid issues where files are
        # removed and also get rid of any caching issues.
        dialog = riffle.browser.FilesystemBrowser(parent=self)
        dialog.setMinimumSize(900, 500)

        if self._currentLocation:
            dialog.setLocation(self._currentLocation)

        if dialog.exec_():
            selected = dialog.selected()
            if selected:
                item = selected[0]
                # Convert to unicode.
                if isinstance(item, str):
                    item = item.decode('utf-8')
                self.dataSelected.emit(item)

        # TODO: This is fragile and should probably be available as public
        # reload method in the Riffle project.
        self._currentLocation = dialog._locationWidget.itemData(
            dialog._locationWidget.currentIndex()
        )

        dialog.destroy()

    def _setDropZoneState(self, state='default'):
        '''Set drop zone state to *state*.

        *state* should be 'default', 'active' or 'invalid'.

        '''
        self.setProperty('ftrackDropZoneState', state)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _processMimeData(self, mimeData):
        '''Return a list of valid filepaths.'''
        validPaths = []

        if not mimeData.hasUrls():
            QtWidgets.QMessageBox.warning(
                self,
                'Invalid file',
                'Invalid file: the dropped item is not a valid file.'
            )
            return validPaths

        for path in mimeData.urls():
            localPath = path.toLocalFile()
            if os.path.isfile(localPath):
                validPaths.append(localPath)
                self.log.debug(u'Dropped file: {0}'.format(localPath))
            else:
                message = u'Invalid file: "{0}" is not a valid file.'.format(
                    localPath
                )
                if os.path.isdir(localPath):
                    message = (
                        'Folders not supported.\n\nIn the current version, '
                        'folders are not supported. This will be enabled in a '
                        'later release of ftrack connect.'
                    )
                QtWidgets.QMessageBox.warning(
                    self, 'Invalid file', message
                )

        return validPaths

    def clear(self):
        '''Clear the browser to it's initial state.'''
        # Since the dialog is re-created when opened, we don't need to clear it.
        pass

    def dragEnterEvent(self, event):
        '''Override dragEnterEvent and accept all events.'''
        event.setDropAction(QtCore.Qt.CopyAction)
        event.accept()
        self._setDropZoneState('active')

    def dragLeaveEvent(self, event):
        '''Override dragLeaveEvent and accept all events.'''
        event.accept()
        self._setDropZoneState()

    def dropEvent(self, event):
        '''Handle dropped file event.'''
        self._setDropZoneState()

        # TODO: Allow hook into the dropEvent.

        paths = self._processMimeData(
            event.mimeData()
        )

        self.log.debug(u'Paths: {0}'.format(paths))

        # Use frames pattern instead of default digits pattern to only match
        # frame sequences.
        framesPattern = clique.PATTERNS.get('frames')
        sequences, remainders = clique.assemble(
            paths,
            patterns=[
                framesPattern
            ]
        )

        self.log.debug(u'Sequences: {0}'.format(sequences))
        self.log.debug(u'Remainders: {0}'.format(remainders))

        for sequence in sequences:
            self.dataSelected.emit(sequence.format())

        for path in remainders:
            self.dataSelected.emit(path)

        event.accept()
