#! usr/bin/env python
#encoding=utf8
"""
this script is purpose is prepare for matrix's userid's index
"""
import redis
ip='192.168.1.7'
r3=redis.Redis(db=3,host=ip)
dict=r3.hgetall("username2userids")
new_dict={}
for k,v in dict.iteritems():
    new_dict[v]=k
r3.hmset("userid2usernames",new_dict)

print "done!"
    