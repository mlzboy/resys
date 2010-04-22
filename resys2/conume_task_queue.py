#! usr/bin/env python
#encoding=utf8
"""
brief:
this script's purpose is use fork advatange to concurrency execute dreque task Queue
"""
import redis
import time
from multiprocessing import Process
from dreque import DrequeWorker
from dreque import Dreque
from datetime import datetime

ip='192.168.1.7'
r2=redis.Redis(db=2,host=ip)
r3=redis.Redis(db=3,host=ip)
r5=redis.Redis(db=5,host=ip)
#r5.flushdb()
dreque = Dreque((ip,6379),db=6)#储存任务队列
r6=dreque.redis


def gen_zero_list(n):
    return [1 for x in xrange(0,n)]
    
def make_list(db,key,value_list):
    "在db这个数据库中向键为key的list type填充value_list这个list中的所有值"
    pipe=db.pipeline()
    for i in value_list:
        pipe.rpush(key,i)
    pipe.execute()
        
def rank(clicks):
    "根据点击次数来确定其评分"
    if clicks<1:
        result=1
    if clicks==1:
        result=clicks*1.15
    if clicks==2:
        result=clicks*1.2
    if clicks==3:
        result=clicks*1.15
    if clicks>3:
        result=clicks*1.05
    if result>4.5:
        result=4.5
    return result
        
        
linelen=r3.llen("use_productids")
zero_list=gen_zero_list(linelen)
userids=r3.lrange("use_userid_idx",0,-1)
userid2usernames=r3.hgetall("userid2usernames")
username2userids=r3.hgetall("username2userids")
productid2ids=r3.hgetall("productids_idx")


#for userid in userids:
def task(userid):
    "一行矩阵"
    if r5.exists(userid):
        print "由于userid=%s在r5中,不进行处理了"%userid.encode("utf8")
        return
    username=userid2usernames[userid]
    user_productid_visists=r2.hgetall(username)
    new_zero_list=zero_list[::]
    for productid,clicks in user_productid_visists.iteritems():
        if productid in productid2ids:
            productid_idx=int(productid2ids[productid])
            new_zero_list[productid_idx]=rank(int(clicks))
    #print new_zero_list
    make_list(r5,userid,new_zero_list)
    print "完成%s的处理了"%userid.encode("utf8")





def worker():
    #import logging
    #logging.getLogger("dreque.worker").setLevel(logging.CRITICAL)
    w = DrequeWorker(["queue"], (ip,6379),db=6)
    w.work(0.01)#队列轮询间隔的时间，默认是5s

if __name__=="__main__":
    s=datetime.now()

    for i in xrange(0,100):
        worker_child = Process(target=worker, args=())
        #results.append(worker_child)
        worker_child.start()
        time.sleep(0.1)
    
    print "done!"
    
    #w = DrequeWorker(["queue"], (ip,6379),db=6)
    #w.work(0.1)
    
    #list=[1,2,3,4]
    #make_list(r5,"a",list)
    #print r5.lrange("a",0,-1)
    e=datetime.now()
    print "cost time:%s"%(e-s).seconds
    
