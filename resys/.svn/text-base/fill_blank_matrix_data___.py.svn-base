#! bin/usr/bev python
#encoding=utf8
"生成空的blank matrix"
import redis
from datetime import datetime
start=datetime.now()
r0=redis.Redis()#分词后的数据
r1=redis.Redis(host='localhost',port=6379,db=1)#各分词的统计数据，及噪音处理
r2=redis.Redis(host='localhost',port=6379,db=2)#生成matrix data
r2.flushdb()
linelen=r1.hlen("usewords")
print "column nums:%s"%linelen
print type(linelen)
#填充0,0的个数由usewords的个数决定，key为各个产品的id,从r0中来

def make_list(db,key,value_list):
    "在db这个数据库中向键为key的list type填充value_list这个list中的所有值"
    for i in value_list:
        db.rpush(key,i)

def gen_zero_list(n):
    return [0 for x in xrange(0,n)]

zero_list=gen_zero_list(linelen)
for key in r0.keys():
    make_list(r2,key,zero_list)

print "r2 dbsize:%s"%r2.dbsize()

end=datetime.now()
print "cost time:%s"%(end-start).seconds