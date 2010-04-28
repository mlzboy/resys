#! /home/mlzboy/bijia/uwsgi/uwsgi
import uwsgi
import bottle
from bottle import route, request, response, view, send_file, run
from phprpc import PHPRPC_Client
from bottle import PasteServer, FlupServer, FapwsServer, CherryPyServer

bottle.debug(False)
#print client.recommend('a',9,'b')
@route('/hi/:name')
@view('result')
def hi(name):
    #client = PHPRPC_Client('http://127.0.0.1/')
    #r=client.hi(name)
    r="hello --->%s"%name
    return dict(result=r)
#http://127.0.0.1:8080/recommend/productid/ep123123/topn/6/userid/323412us
@route('/recommend/productid/:productid/topn/:topn/userid/:userid')
@view("recommend.tpl")
def recommend(productid,topn,userid):
    client = PHPRPC_Client('http://127.0.0.1/')
    rr=client.recommend(productid,int(topn),userid)
    print rr
    r=dict(a=1,b=2)
    for k in rr:
        print k,rr[k]
    return dict(result=rr)
    


#run(host='localhost',port=8080)
#bottle.run(host='127.0.0.1',port=8080,server=FapwsServer,reloader=True) # Example
#myapp = bottle.default_app()

application=bottle.app()
    
    