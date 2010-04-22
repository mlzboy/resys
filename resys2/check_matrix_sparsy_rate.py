#! usr/bin/env python
#encoding=utf8
"""
this script's function is check matrix's sparsy rate
"""
import redis
from datetime import datetime
s=datetime.now()
ip='192.168.1.7'
r5=redis.Redis(db=5,host=ip)
count=0
totals=r5.keys()
for key in totals:
    list=r5.lrange(key,0,-1)
    #print list
    aa=len(filter(lambda x:x<>"1",list))
    if aa>2:
        print aa,key
    count+=aa
print count
print count/(1130*len(totals))
e=datetime.now()
print 'cost time:%s'%(e-s).seconds

