#!usr/bin/env python
#encoding=utf8
"""
brief:
use cron to apply this scrip,polling sqlserver online product in a fixed time
this script i want to no other third parity package depenlency
"""
import redis
from lib.sqlserver import SqlServer
db=SqlServer("192.168.1.180","abc","abc","DMDM2")
db2=SqlServer("192.168.0.92","maolingzhi","zhoubt","SCM")
ip='192.168.1.7'
r1=redis.Redis(host=ip,db=1)

def getonlineproductids():
    "query db get online productids"
    #if r2.exists("onlineproductids"):
    #    return eval(r2.get("onlineproductids"))
    sql="select productcode from product where isoff=0"
    rows=db2.select(sql)
    productids=[]
    for i in rows:
        productids.append(i[0])
    #print len(productids)
    r1.set("onlineproductids",productids)
    return productids

def getrecommendproductids():
    """
    user view & buy productids,total 2008
    """
    #recommendproductids=r3.lrange("productids",0,-1)
    sql="select * from dm_recommendproducts"
    return recommendproductids