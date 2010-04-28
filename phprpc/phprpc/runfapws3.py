#! usr/bin/env python
#encoding=utf8
import os
import os.path
import fapws._evwsgi as evwsgi
from fapws import base
import sys
sys.setcheckinterval(100000) # since we don't use threads, internal checks are no more required

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
        evwsgi.start(self.host, self.port)
        evwsgi.set_base_module(base)
        
        #def app(environ, start_response):
        #    environ['wsgi.multiprocess'] = False
        #    return wsgi_app(environ, start_response)
    
        evwsgi.wsgi_cb(('',self.app))
        #evwsgi.set_debug(1)#开启调试
        evwsgi.set_debug(0)        
        print "libev ABI version:%i.%i" % evwsgi.libev_version()
        evwsgi.run()
