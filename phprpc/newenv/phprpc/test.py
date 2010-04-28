#! usr/bin/env python
#encoding=utf8
#from phprpc import PHPRPC_Server # 引入 PHPRPC Server
import sys
import runfapws3
from runfapws3 import MY_PHPRPC_Server as PHPRPC_Server
import datetime

def helloworld():
    return 'helloworld'

def hi(name):
    return 'hi %s' % name

def recommend(productid,topn,userid):
    print productid,type(productid)
    print topn,type(topn)
    print userid,type(topn)
    return ['p1','p2','p3']

server = PHPRPC_Server(port=int(sys.argv[1] if len(sys.argv) > 1 else 80))
server.add(helloworld)
server.add('hi')
server.add(hi, 'hello')
server.add(recommend)
server.add(datetime.datetime.now)
server.debug = False#True
server.start()