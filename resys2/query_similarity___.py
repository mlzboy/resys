#! usr/bin/env python
#encoding=gb18030
"""
brief:
query specifice product's similarity top n products
"""
from lib.sqlserver import SqlServer
from lib.mystruct import mystruct
import lib.filehelper as filehelper
from datetime import datetime
import redis

r1=redis.Redis(port=6379,db=1)

db=SqlServer("10.3.10.90","abc","abc","DMDM2")
db2=SqlServer("192.168.0.92","maolingzhi","zhoubt","SCM")
def myrecommend(p1):
    ""
def _setproductid8to72redis():
    "put all 8bit productid and 7bit productid with a hash struct in redis as a cache"
    sql="SELECT ClothesCode AS p8,ProductCode AS p7 FROM dbo.Clothes"
    rows=db2.select(sql)
    dict={}
    for i in rows:
        dict[i[0]]=i[1]
    r1.hmset("p8top7",dict)
    print "finishe load p8top7 to redis memory"

def getproductid8to7(p1):
    """
    the matrix use user 8bit productid as matrix's column,
    and we reuse this script from resys for adapter this script,
    we change the 8 bit productid to 7 productid
    """
    if r1.hexists("p8top7",p1):
        return r1.hget("p8top7",p1)
    sql="SELECT ClothesCode AS p8,ProductCode AS p7 FROM dbo.Clothes WHERE dbo.Clothes.ClothesCode='%s'"%p1
    rows=db2.select(sql)
    return rows[0][1]

def _setproductserialcode2redis():
    sql="SELECT productcode,ProductSerialCode FROM dbo.Product"
    rows=db2.select(sql)
    for i in rows:
        r1.hset("productserialcodes",i[0],i[1])
    print "finishe load productserialcode to redis memory"

def getproductserialcode(p1):
    "获取同款"
    if r1.hexists("productserialcodes",p1):
        return r1.hget("productserialcodes",p1)
        
    sql="SELECT ProductSerialCode FROM dbo.Product WHERE ProductCode='%s'"%p1
    print sql
    rows=db2.select(sql)
    if len(rows)==0:
        return "-1"
    else:
        return rows[0][0]
    
    
def smarttop10(p1):
    "有意思的推荐"
    start=datetime.now()
    rows=top200(p1)
    original_productserialcode=getproductserialcode(p1)
    original_categories=getcategories(p1)
    original_productname=getproductname(p1)
    original_color=getproductcolor(p1)
    results=[]
    recommend_group=mystruct()
    for i in rows:
        sim=i[2]
        if i[0]<>p1:
            recommend_productcode=i[0]
        else:
            recommend_productcode=i[1]
        recommend_productserialcode=getproductserialcode(recommend_productcode)
        recommend_categories=getcategories(recommend_productcode)
        recommend_productname=getproductname(recommend_productcode)
        recommend_color=getproductcolor(recommend_productcode)

        if original_productserialcode<>recommend_productserialcode:
            v=(recommend_productcode,recommend_productname,recommend_categories,sim,recommend_color,recommend_productserialcode)
            if recommend_group.has_key(recommend_productserialcode):
                recommend_group.update(recommend_productserialcode,v)
            else:
                recommend_group.add(recommend_productserialcode,v)
            #results.append("%s,%s,%s,%s\r\n"%(recommend_productcode,recommend_productname,recommend_categories,sim))
        
    for elem in recommend_group.getvalues():
        results.append("%s,%s,%s,%s,%s,%s\r\n"%elem[0])
    filehelper.savefile("recommand.csv",results)
    end=datetime.now()
    print "cost time:%ss"%(end-start).seconds
        
def top200(p1):
    sql="select top 500 p1,p2,sim from similarities where p1='%s' or p2='%s' order by sim desc"%(p1,p1)
    #print sql
    rows=db.select(sql)
    return rows

def cleardb():
    "清除数据库中的表similarites"
    db.execute("delete from similarities")
    
def recordcount():
    "统计数据行数"
    sql="select count(*) from similarities"
    rows=db.select(sql)
    return rows[0][0]

def _setcategories2redis():
    sql="SELECT productcode,dbo.getcategoryname(categorycode) as category FROM dbo.Product"
    rows=db2.select(sql)
    for i in rows:
        r1.hset("productcategories",i[0],i[1])
    print "finishe load productcategories to redis memory"  

def getcategories(p1):
    "产品从大到小的分类"
    if r1.hexists("productcategories",p1):
        return r1.hget("productcategories",p1)
        
    sql="SELECT dbo.getcategoryname(categorycode) as category FROM dbo.Product WHERE ProductCode='%s'"%p1
    rows=db2.select(sql)
    if len(rows)==0:
        return "-1"
    else:
        return rows[0][0]
    
def _setproductname2redis():
    sql="SELECT productcode,productname FROM dbo.Product"
    rows=db2.select(sql)
    for i in rows:
        r1.hset("productnames",i[0],i[1])
    print "finished load productname to redis memory"     

def getproductname(p1):
    "产品的名称"
    if r1.hexists("productnames",p1):
        return r1.hget("productnames",p1)
        
    sql="SELECT productname FROM dbo.Product WHERE ProductCode='%s'"%p1
    rows=db2.select(sql)
    if len(rows)==0:
        return "-1"
    else:
        return rows[0][0]
    
def _setproductcolor2redis():
    sql="SELECT productcode,isnull(Redundancy5,'') FROM product"
    #print sql
    rows=db2.select(sql)
    for i in rows:
        r1.hset("productcolors",i[0],i[1])
    print "finished load productcolor to redis memory"

def getproductcolor(p1):
    "获取产品颜色"
    if r1.hexists("productcolors",p1):
        return r1.hget("productcolors",p1)
        
    sql="SELECT isnull(Redundancy5,'') FROM product WHERE ProductCode='%s'"%p1
    print sql
    rows=db2.select(sql)
    #print len(rows)
    if len(rows)==0:
        return "-1"
    else:
        return rows[0][0]
    
def load2redis():
    _setproductcolor2redis()
    _setproductname2redis()
    _setcategories2redis()
    _setproductserialcode2redis()
    _setproductid8to72redis()

def clearredis():
    r1.delete("productserialcodes")
    r1.delete("productcategories")
    r1.delete("productnames")
    r1.delete("productcolors")
    r1.delete("p8top7")
    
#results=top200('0003542')


if __name__=="__main__":
    s=datetime.now()
    #cleardb()
    #print recordcount()
    #results=top200('0001847')
    #getproductcolor('0001847')
    
    #clearredis()
    #load2redis()
    
    smarttop10('0001847')
    e=datetime.now()
    print "cost time:%s"%(e-s).seconds
    