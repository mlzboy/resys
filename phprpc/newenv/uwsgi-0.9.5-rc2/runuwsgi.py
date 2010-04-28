#!usr/bin/env python
#encoding=utf8
from phprpc import PHPRPC_WSGIApplication

class MY_PHPRPC_Server(object):
    def __init__(self, host = '0.0.0.0', port = 80, app = None):
        self.host = host
        self.port = port
        if app == None:
            self.app = PHPRPC_WSGIApplication()
        else:
            self.app = app

    def add(self, method, aliasname = None):
        self.app.add(method, aliasname)

    def charset():
        def fget(self):
            return self.app.charset
        def fset(self, value):
            self.app.charset = value
        return locals()
    charset = property(**charset())

    def debug():
        def fget(self):
            return self.app.debug
        def fset(self, value):
            self.app.debug = value
        return locals()
    debug = property(**debug())

    #def start(self):
    #    print "Serving on port %s:%s..." % (self.host, self.port)
    #    from wsgiref.simple_server import make_server
    #    httpd = make_server(self.host, self.port, self.app)
    #    try:
    #        httpd.serve_forever()
    #    except KeyboardInterrupt:
    #        exit()
            
    def start(self):
        return self.app
