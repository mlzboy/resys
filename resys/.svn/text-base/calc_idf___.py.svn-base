#! usr/bin/env python
#encoding=utf8
"""
计算idf
"""
from __future__ import division#must occur at the beginning of the file
from math import sqrt,acos,log
import redis
from datetime import datetime
start=datetime.now()
r0=redis.Redis()
r1=redis.Redis(port=6379,db=1)
r3=redis.Redis(port=6379,db=3)
r1.delete("positionidfs")
usewords_dict=r1.hgetall('usewords')
positions=r1.zrange('positions',0,-1)
#通过matrix中column的index查找positions中对应的keyword再到usewords_dict中查到对应的该keyword的global usetimes
column_counts=len(usewords_dict)
product_counts=r0.dbsize()
print type(product_counts)
print "product_count:%s"%product_counts
print "column_counts:%s"%column_counts

def idf(column_idx):
    keyword=positions[column_idx]
    times=int(usewords_dict[keyword])
    return log(product_counts/times)
    
for idx in xrange(0,column_counts):
    r1.hset("positionidfs",idx,idf(idx))
    
positionidfs_dict=r1.hgetall('positionidfs')
if len(positionidfs_dict)==column_counts:
    print "right"
    #for k,v in positionidfs_dict.iteritems():
    #    print k,v
    #    print type(k),type(v)
else:
    print "error!"
end=datetime.now()
print "cost time:%ss"%(end-start).seconds

    
    
