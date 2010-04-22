#! usr/bin/env python
#encoding=utf8
"""
this script purpose is generate a userid-productid init matrix
生成一个初始的矩阵，包括用户的浏览评分，未包含
这个脚本生成矩阵的时间，较长，可以考虑分布执行
"""
import redis
from datetime import datetime
s=datetime.now()
ip='192.168.1.7'
r2=redis.Redis(db=2,host=ip)
r3=redis.Redis(db=3,host=ip)
r5=redis.Redis(db=5,host=ip)
r5.flushdb()
def gen_zero_list(n):
    return [1 for x in xrange(0,n)]
    
def make_list(db,key,value_list):
    "在db这个数据库中向键为key的list type填充value_list这个list中的所有值"
    for i in value_list:
        db.rpush(key,i)
        
def rank(clicks):
    "根据点击次数来确定其评分"
    if clicks<1:
        result=1
    if clicks==1:
        result=clicks*1.15
    if clicks==2:
        result=clicks*1.2
    if clicks==3:
        result=clicks*1.15
    if clicks>3:
        result=clicks*1.05
    if result>4.5:
        result=4.5
    return result
        
        
linelen=r3.llen("use_productids")
zero_list=gen_zero_list(linelen)
userids=r3.lrange("use_userid_idx",0,-1)
userid2usernames=r3.hgetall("userid2usernames")
username2userids=r3.hgetall("username2userids")
productid2ids=r3.hgetall("productids_idx")


for userid in userids:
    username=userid2usernames[userid]
    user_productid_visists=r2.hgetall(username)
    new_zero_list=zero_list[::]
    for productid,clicks in user_productid_visists.iteritems():
        if productid in productid2ids:
            productid_idx=int(productid2ids[productid])
            new_zero_list[productid_idx]=rank(int(clicks))
    #print new_zero_list
    make_list(r5,userid,new_zero_list)
e=datetime.now()
print "cost time:%s"%(e-s).seconds
print "done!"
    
