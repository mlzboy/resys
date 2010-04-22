#! usr/bin/env python
#encoding=utf8
"""
brief:
生成矩阵中两两计算的任务队列
"""
from __future__ import division#must occur at the beginning of the file
from math import sqrt,acos,log
import redis
from dreque import Dreque
from datetime import datetime
print "start..."
r0=redis.Redis(port=6380)
r1=redis.Redis(port=6380,db=1)
#r0=redis.Redis()
#r1=redis.Redis(db=1)
start=datetime.now()
r1.delete("queue")
print "删除queue"
r1.delete("clone_queue")
print "删除clone_queue"
count=0

def _do(x,y):
    global count
    count+=1
    #r1.rpush("queue",(x,y))
    #这里对储存队列的方式进行了变更20100331
    r1.rpush("queue","%s:%s"%(x,y))
    return x

keys=r0.keys()
for i in xrange(0,len(keys)):
    reduce(_do,keys[i:])

end=datetime.now()
print count
print "cost time:%ss"%(end-start).seconds
print "done!"