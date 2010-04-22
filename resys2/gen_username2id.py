#! usr/bin/env python
#encoding=utf8
"""
将dba给的username的id生成匹配的username->id的hash放在r3中
这个脚本乃用到了之前save_username2txt.py的结果username.txt
"""
import redis
ip='192.168.1.7'
r3=redis.Redis(db=3,host=ip)
#print r3.keys()
r3.delete("username2userids")
username2id={}
f = open("userid.txt","r") 
for line in f.readlines():
    userid,username=line.strip().split(",")
    username2id[username]=userid
f.close()
r3.hmset("username2userids",username2id)
print r3.hlen("username2userids")
