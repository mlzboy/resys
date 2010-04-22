#! usr/bin/env python
#encoding=utf8
"""
this script is purpose is prepare for matrix's userid's index
"""
import redis
ip='192.168.1.7'
r3=redis.Redis(db=3,host=ip)
list=r3.hvals("username2userids")
for userid in lists:
    r3.lpush("use_userid_idx",userid)
print "done!"
    