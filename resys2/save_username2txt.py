#! usr/bin/env python
#encoding=utf8
"""
this script need write permission

"""
import redis
from lib import filehelper
r3=redis.Redis(host="192.168.1.7",db=2)
filehelper.savefile("username.txt","\n".join(r3.keys()))
print len(r3.keys())
print "done"
