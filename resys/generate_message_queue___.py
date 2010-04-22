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

r1=redis.Redis(db=1)
r4=redis.Redis(db=4)#计算完成tf/idf后的矩阵
r6=redis.Redis(db=6)#储存执行结果
dreque = Dreque(("localhost",6379),db=5)#储存任务队列
dreque.redis.flushdb()
r6.flushdb()
#print "done!"
#import sys
#sys.exit(0)
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

#result=r1.lrange("queue",0,0)
#print eval(result[0])
while(r1.llen("queue")>0):
    v=r1.lpop("queue")
    #v=r1.lrange("queue",0,0)[0]
    #args=eval(v)
    #由于20100331更改了prepare_message_queue___.py生成的任务形式，由(x,y)变为x:y，因此改变解析任务的方法如下：
    args=v.split(":")
    dreque.enqueue("queue", calc,args[0],args[1])
    #break

end=datetime.now()
print "cost time:%ss"%(end-start).seconds

#from dreque import DrequeWorker
#worker = DrequeWorker(["queue"], ("localhost",6379),db=5)
#worker.work()
