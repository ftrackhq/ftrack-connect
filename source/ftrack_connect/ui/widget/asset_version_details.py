
import os

from PySide import QtCore, QtGui

import ftrack
from ftrack_connect.connector import HelpFunctions


class AssetVersionDetailsWidget(QtGui.QWidget):
    
    def __init__(self, parent=None, connector=None):
        '''Initialise widget.'''
        super(AssetVersionDetailsWidget, self).__init__(parent)
        
        if not connector:
            raise ValueError('Please provide a connector object for %s' % self.__class__.__name__)

        self.connector = connector

        self.headers = (
            'Asset', 'Author', 'Version', 'Date', 'Comment'
        )
        self.placholderThumbnail = (os.environ['FTRACK_SERVER']
                                    + '/img/thumbnail2.png')
        # TODO: Implement better caching system
        self.thumbnailCache = {}
        
        self.build()
        self.postBuild()
        
    def build(self):
        '''Build widgets and layout.'''
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        self.thumbnailWidget = QtGui.QLabel()
        self.thumbnailWidget.setFrameStyle(QtGui.QFrame.StyledPanel)
        self.thumbnailWidget.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnailWidget.setFixedWidth(240)
        
        self.layout().addWidget(self.thumbnailWidget)
        
        self.propertyTableWidget = QtGui.QTableWidget()
        self.propertyTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.propertyTableWidget.setSelectionMode(
            QtGui.QAbstractItemView.NoSelection
        )
        
        self.propertyTableWidget.setRowCount(len(self.headers))
        self.propertyTableWidget.setVerticalHeaderLabels(self.headers)

        self.propertyTableWidget.setColumnCount(1)
        horizontalHeader = self.propertyTableWidget.horizontalHeader()
        horizontalHeader.hide()
        horizontalHeader.setResizeMode(QtGui.QHeaderView.Stretch)

        verticalHeader = self.propertyTableWidget.verticalHeader()
        verticalHeader.setResizeMode(QtGui.QHeaderView.ResizeToContents)

        # Fix missing horizontal scrollbar when only single column
        self.propertyTableWidget.setHorizontalScrollMode(
            QtGui.QAbstractItemView.ScrollPerPixel
        )

        for index in range(len(self.headers)):
            self.propertyTableWidget.setItem(
                index, 0, QtGui.QTableWidgetItem('')
            )

        self.layout().addWidget(self.propertyTableWidget)

    def postBuild(self):
        '''Perform post build operations.'''
        self.propertyTableWidget.horizontalHeader().sectionResized.connect(
            self.propertyTableWidget.resizeRowsToContents
        )
        
        self.connector.executeInThread(
            self._updateThumbnail, [self.thumbnailWidget, self.placholderThumbnail])
        
    def setAssetVersion(self, assetVersionId):
        '''Set the asset version to display details for.'''
        assetVersion = ftrack.AssetVersion(assetVersionId)
        asset = assetVersion.getAsset()
        
        header = self.headers.index
        
        item = self.propertyTableWidget.item(header('Asset'), 0)
        item.setText(asset.getName())
        
        item = self.propertyTableWidget.item(header('Author'), 0)
        item.setText(assetVersion.getUser().getName())
        
        item = self.propertyTableWidget.item(header('Version'), 0)
        item.setText(str(assetVersion.getVersion()))
        
        item = self.propertyTableWidget.item(header('Date'), 0)
        item.setText(assetVersion.getDate().strftime('%c'))
        
        item = self.propertyTableWidget.item(header('Comment'), 0)
        item.setText(assetVersion.getComment())
        
        thumbnail = assetVersion.getThumbnail()
        if thumbnail is None:
            thumbnail = self.placholderThumbnail
        
        self.connector.executeInThread(
            self._updateThumbnail, [self.thumbnailWidget, thumbnail]
        )
        
    def _updateThumbnail(self, arg):
        '''Update thumbnail for *label* with image at *url*.'''
        label = arg[0]
        url = arg[1]
        label.setText('')
        pixmap = self._pixmapFromUrl(url)
        scaledPixmap = pixmap.scaledToWidth(
            label.width(),
            mode=QtCore.Qt.SmoothTransformation
        )
        label.setPixmap(scaledPixmap)
        
    def _pixmapFromUrl(self, url):
        '''Retrieve *url* and return data as a pixmap.'''
        pixmap = self.thumbnailCache.get(url)
        if pixmap is None:
            data = HelpFunctions.getFileFromUrl(url)
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(data)
            self.thumbnailCache[url] = pixmap
        
        # Handle null pixmaps. E.g. JPG on Windows.
        if pixmap.isNull():
            pixmap = self.thumbnailCache.get(self.placholderThumbnail, pixmap)
            
        return pixmap
