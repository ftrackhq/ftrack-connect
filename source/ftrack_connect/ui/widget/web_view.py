# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from PySide import QtCore, QtGui, QtWebKit

from ftrack_connect.connector import PersistentCookieJar, HelpFunctions


class Ui_WebView(object):
    '''Webview UI.'''

    def setupUi(self, WebView):
        '''Setup UI for *WebView*.'''
        WebView.setObjectName('WebView')
        WebView.resize(688, 555)
        self.horizontalLayout = QtGui.QHBoxLayout(WebView)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName('horizontalLayout')
        self.WebViewView = QtWebKit.QWebView(WebView)
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
                'WebView', 'Form', None, QtGui.QApplication.UnicodeUTF8
            )
        )


class WebPage(QtWebKit.QWebPage):
    '''WebPage widget.'''

    def javaScriptConsoleMessage(self, msg, line, source):
        '''Print javascript console message.'''
        print '%s line %d: %s' % (source, line, msg)


class WebViewWidget(QtGui.QWidget):
    '''Webview widget class.'''

    def __init__(self, parent, task=None):
        '''Instansiate web view widget.'''
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_WebView()
        self.ui.setupUi(self)

        self.webPage = WebPage()
        self.persCookieJar = PersistentCookieJar.PersistentCookieJar(self)
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
