#! usr/bin/env python
#encoding=utf8
import redis
from datetime import datetime
ip='192.168.1.7'
r5=redis.Redis(db=5,host=ip)
r3=redis.Redis(db=3,host=ip)
size=r3.llen("use_productids")
s=datetime.now()
for key in r5.keys():
    if r5.llen(key)==size:
        pass
    else:
        print "key=%s,error"%key
e=datetime.now()
print "cost time:%s"%(e-s).seconds
print "done!"