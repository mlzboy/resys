#! usr/bin/env python
#encoding=utf8
"""
brief:
从localhost:6380:db2从库克隆数据至lcoalhost:6379:db3主库
"""
import redis
from datetime import datetime
start=datetime.now()
r2=redis.Redis(port=6380,db=2)
r3=redis.Redis(db=3)
def make_list(rx, key, list):
    for elem in list:
        rx.rpush(key, elem)
        
for key in r2.keys():
    list=r2.lrange(key,0,-1)
    make_list(r3,key,list)

end=datetime.now()
print "cost time:%ss"%(end-start).seconds
print "done!"