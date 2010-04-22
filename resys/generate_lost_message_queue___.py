#! usr/bin/env python
#encoding=utf8
"""
brief:
在执行完check_lost_tasks___.py后会将找回的丢失任务再插入到r1的queue中
这个脚本的作用是再将这些丢失的任务生成dreque的消息任务
"""
from __future__ import division#must occur at the beginning of the file
from math import sqrt,acos,log
import redis
from dreque import Dreque
from datetime import datetime

r1=redis.Redis(host='10.3.11.178',db=1)
r4=redis.Redis(host='10.3.11.178',db=4)#计算完成tf/idf后的矩阵
r6=redis.Redis(host='10.3.11.178',db=6)#储存执行结果
dreque = Dreque(("10.3.11.178",6379),db=5)#储存任务队列
#TODO:how to know dreque current has left tasks in it's queue,in therory,it should be 0
#print dreque.redis.dbsize()
start=datetime.now()

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
    print "============="
    v=sim(list1,list2)
    print v
    r6.set(key1+":"+key2,v)
    print type(r6.get(key1+":"+key2))


while(r1.llen("queue")>0):
    v=r1.lpop("queue")
    args=v.split(":")
    dreque.enqueue("queue", calc,args[0],args[1])

end=datetime.now()
print "cost time:%ss"%(end-start).seconds