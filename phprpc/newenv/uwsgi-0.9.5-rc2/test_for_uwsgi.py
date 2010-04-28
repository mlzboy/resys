#!/home/mlzboy/bijia/resys/phprpc/newenv/uwsgi-0.9.5-rc2/uwsgi
#encoding=utf8
import uwsgi
import sys
from runuwsgi import MY_PHPRPC_Server as PHPRPC_Server
import datetime

def helloworld():
    return 'helloworld'

def hi(name):
    return 'hi %s' % name

def recommend(productid,topn,userid):
    print productid,type(productid)
    print topn,type(topn)
    print userid,type(userid)
    return ['p1','p2','p3']

server = PHPRPC_Server(port=int(sys.argv[1] if len(sys.argv) > 1 else 80))
server.add(helloworld)
#server.add('hi')
server.add(hi, 'hello')
server.add(recommend)
server.add(datetime.datetime.now)
server.debug = False#True
app1=server.start()

application=app1