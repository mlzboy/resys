#! usr/bin/env python
#encoding=utf8
"""
根据上一步calc_idf__.py生成的idf生成成归一化矩阵
"""
from __future__ import division#must occur at the beginning of the file
from math import sqrt,acos,log
import redis
from datetime import datetime
start=datetime.now()
r0=redis.Redis()
r1=redis.Redis(db=1)
r3=redis.Redis(db=3)
r4=redis.Redis(db=4)
r4.flushdb()
positionidfs_dict=r1.hgetall('positionidfs')

def make_list(rx, key, list):
    for elem in list:
        rx.rpush(key, elem)
        
for key in r0.keys():
    list=r3.lrange(key,0,-1)
    new_list=[]
    for idx in xrange(0,len(list)):
        idf=float(positionidfs_dict[str(idx)])
        new_list.append(int(list[idx])*idf)
    #if len(new_list)==len(list):
    #    print "true"
    #    print new_list
    #    break
    make_list(r4,key,new_list)
    #print r4.lrange(key,0,-1)
    #break
    
        

end=datetime.now()
print "done!"
print "cost time:%ss"%(end-start).seconds

    
    
