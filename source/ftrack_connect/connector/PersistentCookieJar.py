# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from PySide import QtNetwork, QtCore


class PersistentCookieJar(QtNetwork.QNetworkCookieJar):

    def save(self):
        cookieList = self.allCookies()
        data = QtCore.QByteArray()

        for cookie in cookieList:
            if not cookie.isSessionCookie():
                data.append(cookie.toRawForm())
                data.append('\n')
        settings = QtCore.QSettings('ftrack', 'launchpad')

        settings.setValue("Cookies", data)

    def load(self):
        settings = QtCore.QSettings('ftrack', 'launchpad')
        data = settings.value("Cookies")
        self.setAllCookies(QtNetwork.QNetworkCookie.parseCookies(data))
