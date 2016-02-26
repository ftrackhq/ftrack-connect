# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import BaseHTTPServer
import urlparse
import webbrowser
import functools

from PySide import QtCore


class LoginServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    '''Login server handler.'''

    def __init__(self, login_callback, *args, **kw):
        '''Initialise handler.'''
        self.login_callback = login_callback
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kw)

    def do_GET(self):
        '''Override to handle requests ourselves.'''
        parsed_path = urlparse.urlparse(self.path)
        query = parsed_path.query

        api_user = None
        api_key = None
        if 'api_user' and 'api_key' in query:
            login_credentials = urlparse.parse_qs(query)
            api_user = login_credentials['api_user'][0]
            api_key = login_credentials['api_key'][0]
            message = """
                <html>
                <body>
                  <center>
                  <div style="margin:auto; margin-top:30px; max-width:350px">
                    <p>Sign in to ftrack connect was successful.</p>
                    <p style="color:#aaaaaa">You signed in with 
                    username {0} and can now close this window.</p>
                </div>
                  </center>
                </body>
                </html>
            """.format(api_user)
        else:
            message = 'Empty page.'

        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)

        if login_credentials:
            self.login_callback(
                api_user,
                api_key
            )


class LoginServerThread(QtCore.QThread):
    '''Login server thread.'''

    # Login signal.
    loginSignal = QtCore.Signal(object, object, object)

    def start(self, url):
        '''Start thread.'''
        self.url = url
        super(LoginServerThread, self).start()

    def _handle_login(self, api_user, api_key):
        '''Login to server with *api_user* and *api_key*.'''
        self.loginSignal.emit(self.url, api_user, api_key)

    def run(self):
        '''Listen for events.'''
        self._server = BaseHTTPServer.HTTPServer(
            ('localhost', 0),
            functools.partial(
                LoginServerHandler, self._handle_login
            )
        )
        webbrowser.open_new_tab(
            '{0}/user/api_credentials?redirect_url=http://localhost:{1}'.format(
                self.url, self._server.server_port
            )
        )
        self._server.handle_request()
