#! bin/usr/env python
#encoding=utf8
"""
brief:
在使用do_job___.py完成计算任务后，检查因意外中止而丢失的任务，
并使丢使的结果储存到r1的queue任务队列中
"""
import redis
import sys
from lib import redishelper
from datetime import datetime
r1_remote=redis.Redis(host='10.3.11.178',db=1)
r6_remote=redis.Redis(host='10.3.11.178',db=6)
r1_independent=redis.Redis(port=6382,db=1)
queue_len=r1_remote.llen("queue")
start=datetime.now()
#print type(queue_len)
if(queue_len>0):
    print "任务队列里还有数据，不进行丢失任务的检测"
    sys.exit(0)
if(r6_remote.dbsize()==r1_independent.llen("clone_queue")):
    print "当前要比对r6数据库中储存的完成任务的个数和clone queue相等，因此不进行检测"
    sys.exit(0)
finished_tasks=set(r6_remote.keys())
total_tasks=set(r1_independent.lrange("clone_queue",0,-1))
lost_tasks=total_tasks.difference(finished_tasks)
redishelper.make_list(r1_remote,"queue",lost_tasks)
end=datetime.now()
print "找到%s个丢失的任务并已插入queue队列"%len(lost_tasks)
print "cost time:%ss"%(end-start).seconds
print "done!"


