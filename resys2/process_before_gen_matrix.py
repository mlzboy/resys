#! usr/bin/env python
#encoding=utf8
"""
将use_productids中的productid,生成一个productid->idx的hash结构productids_idx
"""
import redis
ip='192.168.1.7'
r3=redis.Redis(db=3,host=ip)
productids=r3.lrange("use_productids",0,-1)
for idx,productid in enumerate(productids):
    print idx,productid
    r3.hset("productids_idx",productid,idx)
print 'done!'