#! usr/bin/env python
#encoding=utf8
"""
生成矩阵，productid在矩阵中的顺序储存在r3中
用于将在r2的用户浏览过的产品进行记录到r3的productids中，看总共有多少产品
use_productids--->list
productids---->zset
onlineproductids----->zset
将上面productids生成的一些有错误的id,主要是数字小于7通过db中的架上数据来做交集，
当前结果是架上有1869个数据，而数据中拥有1130的数据
"""
from datetime import datetime
from lib.sqlserver import SqlServer
import redis
s=datetime.now()
ip='192.168.1.7'
r2=redis.Redis(db=2,host=ip)#username集
r3=redis.Redis(db=3,host=ip)#存放配置
db=SqlServer("192.168.0.92","maolingzhi","zhoubt","SCM")
def onlineproductids():
    "获取在架上的产品id集"
    sql="select productcode from product where isoff=0"
    rows=db.select(sql)
    for i in rows:
        r3.zadd("onlineproductids",i[0],0)
    print r3.zcard("onlineproductids")
    return r3.zrange("onlineproductids",0,-1)



print "totoal users:%s"%r2.dbsize()
usernames=r2.keys()
#for username in usernames:
#    dict=r2.hgetall(username)
#    for productid in dict.keys():
#        r3.zadd("productids",productid,0)
print "total products:%s"%r3.zcard("productids")
rough_productids=r3.zrange("productids",0,-1)



db_productids=onlineproductids()

intersation=list(set(rough_productids)&set(db_productids))
print len(intersation)


for productid in intersation:
    r3.lpush("use_productids",productid)#这里意外使用了lpush,按理应该使用rpush
print "================="
print r3.llen("use_productids")
#import sys
#sys.exit(0)


e=datetime.now()
print "cost time:%s"%(e-s).seconds

