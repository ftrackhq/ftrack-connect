from PySide import QtCore, QtGui, QtWebKit

from ftrack_connect.connector import PersistentCookieJar, HelpFunctions

class Ui_WebView(object):
    def setupUi(self, WebView):
        WebView.setObjectName("WebView")
        WebView.resize(688, 555)
        self.horizontalLayout = QtGui.QHBoxLayout(WebView)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.WebViewView = QtWebKit.QWebView(WebView)
        font = QtGui.QFont()
        font.setFamily("Anonymous Pro")
        self.WebViewView.setFont(font)
        self.WebViewView.setUrl(QtCore.QUrl("http://feber.se/"))
        self.WebViewView.setObjectName("WebViewView")
        self.horizontalLayout.addWidget(self.WebViewView)

        self.retranslateUi(WebView)
        QtCore.QMetaObject.connectSlotsByName(WebView)

    def retranslateUi(self, WebView):
        WebView.setWindowTitle(QtGui.QApplication.translate("WebView", "Form", None, QtGui.QApplication.UnicodeUTF8))


class WebPage(QtWebKit.QWebPage):
    def javaScriptConsoleMessage(self, msg, line, source):
        print '%s line %d: %s' % (source, line, msg)


class WebViewWidget(QtGui.QWidget):
    def __init__(self, parent, task=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_WebView()
        self.ui.setupUi(self)

        self.webPage = WebPage()
        self.persCookieJar = PersistentCookieJar.PersistentCookieJar(self)
        self.persCookieJar.load()

        # self.webPage.networkAccessManager().setCookieJar(self.persCookieJar)
        proxy = HelpFunctions.getFtrackQNetworkProxy()
        if proxy:
            self.webPage.networkAccessManager().setProxy(proxy)

        self.ui.WebViewView.setPage(self.webPage)

    def sslErrorHandler(self, reply, errorList):
        reply.ignoreSslErrors()
        print ("SSL error ignored")

    def setUrl(self, url):
        self.ui.WebViewView.load(QtCore.QUrl(url))
