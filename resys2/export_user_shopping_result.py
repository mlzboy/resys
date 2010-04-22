#! usr/bin/env python
#encoding=utf8
"""
这个脚本的作用是从数据库中取出这两天产生购买的用户id,及这些用户购买的商品id
"""
print "haha"
import redis
from lib.sqlserver import SqlServer
from datetime import datetime
s=datetime.now()
ip='192.168.1.7'
r4=redis.Redis(db=4,host=ip)#存放用户购买的产品的id,一个用户是一个list和r2相对应
r4.flushdb()
db=SqlServer("192.168.0.92","maolingzhi","zhoubt","SCM")

def getdata():
    "获取指定天的用户下的订单的产品的id"
    sql="""
declare @begindate varchar(20),@enddate varchar(20);
set @begindate = '2010-04-01 00:00:00';
set @enddate = '2010-04-02 23:59:59';
select 
	userid,
	c.productcode,
	case FormType
		when 1 then '电话'
		when 2 then '网站'
		else '其他'
	end as formtype
from orderform o (nolock)
	left join orderdetail d (nolock) on d.formcode = o.formcode
	left join clothes c (nolock) on c.clothescode = d.productcode
where 
  	posttime >= @begindate and posttime <= @enddate AND formtype=2
group by  
	userid,
	c.productcode,
	case FormType
		when 1 then '电话'
		when 2 then '网站'
		else '其他'
	end
order by 
	userid,productcode,formtype
"""
    print sql
    rows=db.select(sql)
    pipe=r4.pipeline()
    for i in rows:
        #print i[0],i[1]
        #r4.rpush(i[0],i[1])#this approach will cost 10 times slower than use pipe way
        pipe.rpush(i[0],i[1])
    pipe.execute()

print "hhhhhh"
getdata()
e=datetime.now()
print "cost time:%s"%(e-s).seconds