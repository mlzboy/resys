#! usr/bin/env python
#encoding=utf8
"""
对于有购买的用户，将它的指定商品的评分标为5
"""
import redis
from datetime import datetime
s=datetime.now()
ip='192.168.1.7'
#ip='localhost'
r3=redis.Redis(host=ip,db=3)
r4=redis.Redis(host=ip,db=4)
r5=redis.Redis(host=ip,db=5)
p5=r5.pipeline()
productid2idxs=r3.hgetall("productids_idx")
count=0
for userid in r4.keys():
    shopping_productids=r4.lrange(userid,0,-1)
    for productid in shopping_productids:
        idx=int(productid2idxs[productid])
        p5.lset(userid,idx,5)
        count+=1
    #break

p5.execute()
e=datetime.now()
print "total set counts:%s"%count


print "cost time:%s"%(e-s).seconds
print "done!"