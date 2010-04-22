#! usr/bin/env python
#encoding=utf8
"""
brief:
将r1中的用于准备生成工作队列的queue set type，复制一份存在clone_queue中
因为这里r1_salve是从库，新增的会被旧的主库结构覆盖，所以把们我clone_queue暂时先储存到r1_中
"""
from __future__ import division#must occur at the beginning of the file
from math import sqrt,acos,log
import redis
from dreque import Dreque
from datetime import datetime
from lib import redishelper

r1_slave=redis.Redis(port=6380,db=1)
r1_independent=redis.Redis(port=6382,db=1)
start=datetime.now()
#print r1_slave.llen('queue')
#import sys
#sys.exit(0)
if r1_slave.llen("queue")>0:
    print "queue is not empty,began clone..."
    r1_independent.delete("clone_queue")
    list=r1_slave.lrange("queue",0,-1)
    redishelper.make_list(r1_independent,"clone_queue",list)
end=datetime.now()
print "cost time:%ss"%(end-start).seconds
