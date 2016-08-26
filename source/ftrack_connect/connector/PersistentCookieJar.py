# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from QtExt import QtNetwork, QtCore


class PersistentCookieJar(QtNetwork.QNetworkCookieJar):
    '''Persistent CookieJar.'''

    def save(self):
        '''Save all cookies to settings.'''
        cookieList = self.allCookies()
        data = QtCore.QByteArray()

        for cookie in cookieList:
            if not cookie.isSessionCookie():
                data.append(cookie.toRawForm())
                data.append('\n')
        settings = QtCore.QSettings('ftrack', 'launchpad')

        settings.setValue('Cookies', data)

    def load(self):
        '''Load all cookies fro settings.'''
        settings = QtCore.QSettings('ftrack', 'launchpad')
        data = settings.value('Cookies')
        self.setAllCookies(QtNetwork.QNetworkCookie.parseCookies(data))
