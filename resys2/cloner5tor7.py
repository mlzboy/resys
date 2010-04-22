#! usr/bin/env python
#encoding=utf8
"""
this job is purpose is copy r5 data and structure to r7 as a backup
"""
import redis
ip='192.168.1.7'
ip='localhost'
r5=redis.Redis(db=5,host=ip)
r7=redis.Redis(db=7,host=ip)
r7.flushdb()
print r5.dbsize()
from datetime import datetime
s=datetime.now()

def make_list(db,key,value_list):
    "在db这个数据库中向键为key的list type填充value_list这个list中的所有值"
    pipe=db.pipeline()
    for i in value_list:
        pipe.rpush(key,i)
    pipe.execute()


for key in r5.keys():
    make_list(r7,key,r5.lrange(key,0,-1))
e=datetime.now()
print "done!"
print "cost time:%s"%(e-s).seconds