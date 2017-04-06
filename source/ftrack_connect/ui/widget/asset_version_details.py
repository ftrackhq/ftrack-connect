# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os

from QtExt import QtWidgets, QtCore, QtGui

from ftrack_connect.connector import HelpFunctions
from ftrack_api import symbol


class AssetVersionDetailsWidget(QtWidgets.QWidget):
    '''Asset version details widget.'''

    def __init__(self, parent=None, connector=None):
        '''Initialise widget.'''
        super(AssetVersionDetailsWidget, self).__init__(parent)

        if not connector:
            raise ValueError(
                'Please provide a connector object for {0}'.format(
                    self.__class__.__name__
                )
            )

        self.connector = connector
        self.session = self.connector.session

        self.headers = (
            'Asset', 'Author', 'Version', 'Date', 'Comment'
        )
        self.placholderThumbnail = (
            os.environ['FTRACK_SERVER'] + '/img/thumbnail2.png'
        )
        # TODO: Implement better caching system
        self.thumbnailCache = {}

        self.build()
        self.postBuild()

    def build(self):
        '''Build widgets and layout.'''
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.thumbnailWidget = QtWidgets.QLabel()
        self.thumbnailWidget.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.thumbnailWidget.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnailWidget.setFixedWidth(240)

        self.layout().addWidget(self.thumbnailWidget)

        self.propertyTableWidget = QtWidgets.QTableWidget()
        self.propertyTableWidget.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.propertyTableWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.NoSelection
        )

        self.propertyTableWidget.setRowCount(len(self.headers))
        self.propertyTableWidget.setVerticalHeaderLabels(self.headers)

        self.propertyTableWidget.setColumnCount(1)
        horizontalHeader = self.propertyTableWidget.horizontalHeader()
        horizontalHeader.hide()
        horizontalHeader.setResizeMode(QtWidgets.QHeaderView.Stretch)

        verticalHeader = self.propertyTableWidget.verticalHeader()
        verticalHeader.setResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        # Fix missing horizontal scrollbar when only single column
        self.propertyTableWidget.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel
        )

        for index in range(len(self.headers)):
            self.propertyTableWidget.setItem(
                index, 0, QtWidgets.QTableWidgetItem('')
            )

        self.layout().addWidget(self.propertyTableWidget)

    def postBuild(self):
        '''Perform post build operations.'''
        self.propertyTableWidget.horizontalHeader().sectionResized.connect(
            self.propertyTableWidget.resizeRowsToContents
        )

        self.connector.executeInThread(
            self._updateThumbnail,
            [self.thumbnailWidget, self.placholderThumbnail]
        )

    def setAssetVersion(self, assetVersionId):
        '''Set the asset version to display details for.'''
        asset_version = self.session.query(
            'select id, asset, asset.name, user, user.username,'
            ' version, date, comment, thumbnail'
            ' from AssetVersion where id is "{0}"'.format(assetVersionId)
        ).one()

        server_location = self.session.get(
            'Location', symbol.SERVER_LOCATION_ID
        )

        header = self.headers.index

        item = self.propertyTableWidget.item(header('Asset'), 0)
        item.setText(asset_version['asset']['name'])

        item = self.propertyTableWidget.item(header('Author'), 0)
        item.setText(asset_version['user']['username'])

        item = self.propertyTableWidget.item(header('Version'), 0)
        item.setText(str(asset_version['version']))

        item = self.propertyTableWidget.item(header('Date'), 0)
        item.setText(asset_version['date'].strftime('%c'))

        item = self.propertyTableWidget.item(header('Comment'), 0)
        item.setText(asset_version['comment'])

        # Thumbnail return a FileComponent, so we need the thumbnail of this.
        thumbnail_component = asset_version['thumbnail']
        thumbnail = self.placholderThumbnail

        if thumbnail_component:
            thumbnail = server_location.get_url(thumbnail_component)

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
