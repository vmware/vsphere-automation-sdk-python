'''
This is a lightweight webserver
****Not recommended in a production setting****

Before you run the oauth samples, this server needs to be up.
Make sure to start it before trying out the samples
Or start it as a daemon process

We define listeners for two endpoints,

1. /getcode -> Endpoint to fetch the 'code' and 'state' variable
                It is a GET request
                Once the response is returned,
                    the variables need to be reassigned with ''
                or None, to avoid inconsistent values

2. /authcode -> Redirect endpoint which will be called by the CSP server
                It is a GET request
                code and state are the request params
                e.g., /authcode?code=xxxx&state=xxxxx

In case, you want to change the names of these endpoints in your client,
make sure to change in the below server code as well

'''

try:
    # these imports are specific to Python 2.x
    from BaseHTTPServer import BaseHTTPRequestHandler
    import SocketServer
    from urlparse import urlparse
except ImportError:
    # these imports are specific to Python 3.x
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse

import argparse
import socket
import json

PORT = ''
AUTHCODE = '/authcode'

code = state = ''

hostname = socket.gethostname()
IPAddr = "127.0.0.1"


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    '''
    This class defines the handlers for the incoming GET requests
    '''

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global code, state, AUTHCODE
        print(self.path)

        '''
        defining multiple GET endpoints is not very elegant,
        the very reason why you shouldn't use this in a production setting!
        below are the listeners for /getcode and /authcode
        '''
        if self.path == '/getcode':
            self._set_headers()
            print('call to getcode')
            print(code)
            print(state)
            if code != '' and state != '':
                '''
                the response is defined to be in this format
                code:xxxx:state:xxxx
                the client sample assumes the response to be in this format,
                any change to the response format,
                will need changes in the client code response parser
                '''
                res = "code:" + code + ":state:" + state

                self.wfile.write(res.encode('utf-8'))

            # code and state variables need to be reset
            code = state = ''

        elif self.path.startswith(AUTHCODE, 0):
            print("call to authcode")
            global IPAddr, PORT
            redirect_url = "http://" + IPAddr + ":" + str(PORT) + "/authcode"
            print("Redirect URL: " + redirect_url)
            self._set_headers()
            query = urlparse(self.path).query
            # CSP always sends request in this format
            # /authcode?code=xxxx&state=xxxxx
            query = query.split('&')
            param_code = query[0].split('=')
            code = param_code[1]

            param_state = query[1].split('=')
            state = param_state[1]
            print("code: ", code)
            print("state: ", state)
            self.wfile.write(b'Code and state variables are set,\
                        you may now close the browser tab')

        else:
            pass


def parse_args():
    parser = argparse.ArgumentParser(description='Input port and pathname')
    # port number by default will be 8080
    parser.add_argument(
        '--port',
        dest='port',
        default=8086,
        help='webserver port')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    PORT = int(args.port)
    try:
        httpd = SocketServer.TCPServer(("", PORT), SimpleHTTPRequestHandler)
    except Exception as e:
        httpd = HTTPServer(("", PORT), SimpleHTTPRequestHandler)
    httpd.serve_forever()
