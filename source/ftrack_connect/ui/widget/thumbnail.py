
import os
import urllib2
from PySide import QtGui, QtCore


class Thumbnail(QtGui.QLabel):
    '''Widget to load thumbnails from ftrack server.'''

    def __init__(self, parent=None):
        super(Thumbnail, self).__init__(parent)

        self.thumbnailCache = {}
        self.setFrameStyle(QtGui.QFrame.StyledPanel)
        self.setAlignment(QtCore.Qt.AlignCenter)

        self.placholderThumbnail = (os.environ['FTRACK_SERVER']
                                    + '/img/thumbnail2.png')

    def loadFromUrl(self, url):
        '''Load thumbnail from *url* and display it.'''
        self.setText('')
        if url is None:
            url = self.placholderThumbnail
        pixmap = self._pixmapFromUrl(url)
        scaledPixmap = pixmap.scaledToWidth(
            self.width(),
            mode=QtCore.Qt.SmoothTransformation
        )
        self.setPixmap(scaledPixmap)

    def _getFileFromUrl(self, url):
        '''Return thumbnail file from *url*.'''
        ftrackProxy = os.getenv('FTRACK_PROXY', '')
        ftrackServer = os.getenv('FTRACK_SERVER', '')
        if ftrackProxy != '':
            if ftrackServer.startswith('https'):
                httpHandle = 'https'
            else:
                httpHandle = 'http'

            proxy = urllib2.ProxyHandler({httpHandle: ftrackProxy})
            opener = urllib2.build_opener(proxy)
            response = opener.open(url)
            html = response.read()
        else:
            response = urllib2.urlopen(url)
            html = response.read()

        return html

    def _pixmapFromUrl(self, url):
        '''Retrieve *url* and return data as a pixmap.'''
        pixmap = self.thumbnailCache.get(url)
        if pixmap is None:
            data = self._getFileFromUrl(url)
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(data)
            self.thumbnailCache[url] = pixmap

        # Handle null pixmaps. E.g. JPG on Windows.
        if pixmap.isNull():
            pixmap = self.thumbnailCache.get(self.placholderThumbnail, pixmap)

        return pixmap
