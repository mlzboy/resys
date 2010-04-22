#! usr/bin/env python
#encoding=utf8
"""
brief:
export caculate similarity from redis memory to csv
prepare next step for preparing import to sqlserver
"""
import redis
from lib import filehelper
from datetime import datetime
start=datetime.now()
r6=redis.Redis(host="10.3.11.178",db=6)
print "total have %s recoreds"%r6.dbsize()
keys=r6.keys()
lines=[]
for key in keys:
    p1,p2=key.split(":")
    result=r6.get(key)
    lines.append("%s,%s,%s\r\n"%(p1,p2,result))

filehelper.savefile("result.csv",lines)
end=datetime.now()
print "cost time:%ss"%(end-start).seconds
print "done!"
