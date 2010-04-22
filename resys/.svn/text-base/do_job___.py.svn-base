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
from dreque import DrequeWorker

r4=redis.Redis(host='10.3.11.178',db=4)
r6=redis.Redis(host='10.3.11.178',db=6)#储存执行结果
start=datetime.now()
#r6.flushdb()
def sim(p1,p2):
    "余弦相似度"
    p1_mo=sqrt(sum([x**2 for x in p1]))
    p2_mo=sqrt(sum([x**2 for x in p2]))
    p1p2_dianji=0
    for i in xrange(len(p1)):
        p1p2_dianji+=p1[i]*p2[i] 
    try:
        return p1p2_dianji/(p1_mo*p2_mo)
    except:
        return 0.0

def calc(key1,key2):
    list1=[float(e) for e in r4.lrange(key1,0,-1)]
    list2=[float(e) for e in r4.lrange(key2,0,-1)]
    #print "============="
    v=sim(list1,list2)
    print v
    r6.set(key1+":"+key2,v)
    #print type(r6.get(key1+":"+key2))

worker = DrequeWorker(["queue"], ("10.3.11.178",6379),db=5)
worker.work()