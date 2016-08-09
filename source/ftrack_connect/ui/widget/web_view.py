# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from Qt import QtGui, QtWebKitWidgets, QtCore, QtWidgets

# TODO: Investigate why this import exists and remove it.
try:
    import hiero.core
except ImportError:
    pass

import ftrack

from ftrack_connect.connector import PersistentCookieJar, HelpFunctions


class Ui_WebView(object):
    '''Webview UI.'''

    def setupUi(self, WebView):
        '''Setup UI for *WebView*.'''
        WebView.setObjectName('WebView')
        WebView.resize(688, 555)
        self.horizontalLayout = QtWidgets.QHBoxLayout(WebView)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName('horizontalLayout')
        self.WebViewView = QtWebKitWidgets.QWebView(WebView)
        font = QtGui.QFont()
        font.setFamily('Anonymous Pro')
        self.WebViewView.setFont(font)
        self.WebViewView.setUrl(QtCore.QUrl('about:blank'))
        self.WebViewView.setObjectName('WebViewView')
        self.horizontalLayout.addWidget(self.WebViewView)

        self.retranslateUi(WebView)
        QtCore.QMetaObject.connectSlotsByName(WebView)

    def retranslateUi(self, WebView):
        '''Translate text for *WebView*.'''
        WebView.setWindowTitle(
            QtGui.QApplication.translate(
                'WebView', 'Form', None, QtWidgets.QApplication.UnicodeUTF8
            )
        )


class WebPage(QtWebKitWidgets.QWebPage):
    '''WebPage widget.'''

    def javaScriptConsoleMessage(self, msg, line, source):
        '''Print javascript console message.'''
        print '%s line %d: %s' % (source, line, msg)


# TODO: Remove this widget and refactor Maya plugin to use WebView.
class WebViewWidget(QtWidgets.QWidget):
    '''Webview widget class.'''

    def __init__(self, parent, task=None):
        '''Instansiate web view widget.'''
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_WebView()
        self.ui.setupUi(self)

        self.webPage = WebPage()
        self.persCookieJar = PersistentCookieJar(self)
        self.persCookieJar.load()

        proxy = HelpFunctions.getFtrackQNetworkProxy()
        if proxy:
            self.webPage.networkAccessManager().setProxy(proxy)

        self.ui.WebViewView.setPage(self.webPage)

    def sslErrorHandler(self, reply, errorList):
        '''Handle ssl error.'''
        reply.ignoreSslErrors()

    def setUrl(self, url):
        '''Set web view url to *url*.'''
        self.ui.WebViewView.load(QtCore.QUrl(url))


class WebView(QtWidgets.QFrame):
    '''Display information about selected entity.'''

    def __init__(self, parent=None, url=None):
        '''Initialise WebView with *parent* and *url*'''
        super(WebView, self).__init__(parent)
        self.setMinimumHeight(400)
        self.setSizePolicy(
            QtGui.QSizePolicy(
                QtGui.QSizePolicy.Expanding,
                QtGui.QSizePolicy.Expanding
            )
        )

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self._webView = QtWebKitWidgets.QWebView()
        layout.addWidget(self._webView)

        self.set_url(url)

    def set_url(self, url):
        '''Load *url* and display result in web view.'''
        self._webView.load(QtCore.QUrl(url))

    def get_url(self):
        '''Return current url.'''
        url = self._webView.url().toString()
        if url in ('about:blank', ):
            return None

        return url