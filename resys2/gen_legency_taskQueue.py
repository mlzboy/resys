#! usr/bin/env python
#encoding=utf8
"""
比对一下在有哪些任务丢失的，并将这些任务再次提交
"""
import redis
ip='192.168.1.7'
r3=redis.Redis(db=3,host=ip)
r5=redis.Redis(db=5,host=ip)
userids=r3.lrange("use_userid_idx",0,-1)
print len(userids)
diff=list(set(userids)-set(r5.keys()))
print diff
