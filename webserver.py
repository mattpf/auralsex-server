import BaseHTTPServer
import SocketServer
import threading
import urlparse
from cgi import parse_qs

class ASHTTPServer(BaseHTTPServer.HTTPServer, SocketServer.ThreadingMixIn):
    def shutdown(self):
        try:
            self.socket.close()
        except:
            pass

class ASHTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = 'AuralSex/0.1'
    protocol_version = 'HTTP/1.0'
    
    def output(self, body, content_type='text/plain', response_code=200):
        self.send_response(response_code)
        self.send_header("Content-Length", len(body))
        self.send_header("Content-Type", content_type)
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def not_found(self):
        self.output("Unknown method: %s" % urlparse.urlparse(self.path)[2], response_code=404)

    def do_something(self, method):
        parts = urlparse.urlparse(self.path)
        self.path = parts[2]
        self.query = parse_qs(parts[4])
        
        method(self)
    
    def do_GET(self):
        path = urlparse.urlparse(self.path)[2]
        if path in get_handlers:
            self.do_something(get_handlers[path])
        else:
            self.not_found()
    
    def do_POST(self):
        path = urlparse.urlparse(self.path)[2]
        if path in post_handlers:
            self.do_something(post_handlers[path])
        else:
            self.not_found()
    
post_handlers = {}
get_handlers = {}

def set_post_handler(path, method):
    post_handlers[path] = method

def set_get_handler(path, method):
    get_handlers[path] = method

def serve():
    httpd = ASHTTPServer(('', 8000), ASHTTPHandler)
    httpd.serve_forever()
