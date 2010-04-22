#! usr/bin/env python
#encoding=utf8
"""
this script is want to check productid is 7 bit
还是得按用户的购买说算，不能看点击量里来筛选
"""
import redis
from datetime import datetime
s=datetime.now()
r2=redis.Redis(db=2)
print r2.dbsize()
count=0
keys=[]
dict={}
for key in r2.keys():
    ll=len(filter(lambda x:len(x)<>7,r2.hkeys(key)))
    if ll>0:
        keys.append(key)
    count+=ll
    
    k=str(r2.hlen(key))
    if k in dict:
        dict[k]=dict[k]+1
    else:
        dict[k]=1
    
e=datetime.now()
print count
print keys
#for k,v in dict.iteritems():
#    print "%s==>%s"%(k,v)
for i in xrange(1,100):
    try:
        print "%s==>%s"%(i,dict[str(i)])
    except:
        pass
print "cost time:%s"%(e-s).seconds
