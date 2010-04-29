#!usr/bin/env python
#encoding=utf8
"""
offline process similarity

"""
from lib.sqlserver import SqlServer
from lib.mystruct import mystruct
from lib.odict import OrderedDict as dict
import lib.filehelper as filehelper
from datetime import datetime
import redis
import random
r1=redis.Redis(port=6379,db=1)
r3=redis.Redis(host='192.168.1.7',db=3)

db=SqlServer("192.168.1.180","abc","abc","DMDM2")
db2=SqlServer("192.168.0.92","maolingzhi","zhoubt","SCM")


def getcategoryname(categoryid):
    sql="select categoryname from new_category where categorycode=%s"%categoryid
    rows=db2.select(sql)
    if len(rows)>0:
        return rows[0][0]
    else:
        return "-1"
    
    

def getonlineproductids():
    "query db get offline productids"
    if r1.exists("onlineproductids"):
        return eval(r1.get("onlineproductids"))
    sql="select productcode from product where isoff=0"
    rows=db2.select(sql)
    productids=[]
    for i in rows:
        productids.append(i[0])
    #print len(productids)
    r1.set("onlineproductids",productids)
    return productids

def getrecommendproductids():
    recommendproductids=r3.lrange("productids",0,-1)
    return recommendproductids

def getofflineproductids():
    if r1.exists("offlineproductids"):
        return eval(r1.get("offlineproductids"))
    r=set(getrecommendproductids())-set(getonlineproductids())
    r1.set("offlineproductids",r)
    return r

def getoneneighborproductid(productid):
    """
    from sim lowest category find one random product
    """
    low=getlowestproductcategories(productid)[0]
    #sql="select p.productcode from product p left join clothes c on p.productcode=c.productcode where c.categorycode='%s' and p.isoff=1"%low
    #rows=db2.select(sql)
    #list=[]
    #for i in rows:
    #    list.append(i[0])
    list=r1.lrange(low,0,-1)
    return getrandomelements(list,1)[0]
        
def getoriginalrecommend(productid):
    "get all similarities order by sequence about p1"
    
    sql="select p1,p2,sim from similarities where p1='%s' or p2='%s' order by sim desc"%(productid,productid)
    #print sql
    rows=db.select(sql)
    #print len(rows)
    if len(rows)==0:
        productid=getoneneighborproductid(productid)
    offlineproductids=getofflineproductids()
    print type(offlineproductids)
    print "-------------------))))))))))))))"
    #print len(offlineproductids)
    forbidencategories=getforbidencategories(productid)
    print "88"*20
    print forbidencategories
    hasproductserialcodes=[]
    d=dict()
    for i in rows:
        p1,p2,sim=i[0],i[1],i[2]
        #print type(p1),type(p2),type(sim)
        
        if p1==productid:
            k=p2
        else:
            k=p1
        print getproductallcategoriesbyproductid(k)
        productserialcode=getproductserialcode(k)
        if k not in offlineproductids and \
           len(set(getproductallcategoriesbyproductid(k))&set(forbidencategories))==0 and \
           (productserialcode not in hasproductserialcodes):#gethighestproductcategory(k) not in forbidencategories:
            d[k]=sim
            hasproductserialcodes.append(productserialcode)
    #print type(d)
    #for k,v in d.iteritems():
    #    print k,v
    #if productid in d:
    #    print "error"
    #else:
    #    print "right"
    
    #print d.keys()[-10:]
    print "-"*100
    print len(d)
    return d

def getproductallcategorynames(p1):
    "use the function getcategoryname to fetch all product category names"
    return _getcategories(p1)

def _getcategories(p1):
    "产品从大到小的分类"
    if r1.hexists("productcategories",p1):
        return r1.hget("productcategories",p1)#it's value is a string
        
    sql="SELECT dbo.getcategoryname(categorycode) as category FROM dbo.Product WHERE ProductCode='%s'"%p1
    rows=db2.select(sql)
    if len(rows)==0:
        return "-1"
    else:
        r1.hset("productcategories",p1,rows[0][0])
        return rows[0][0]

def getproductallcategoriesbyproductid(p1):
    if r1.hexists("all",p1):
        return eval(r1.hget("all",p1))
    lowest_category_id=getlowestproductcategories(p1)[0]
    r=getproductallcategories(lowest_category_id)
    r1.hset("all",p1,r)
    return r
    
def getproductallcategories(lowest_category_id):
    "usr backend category system"
    sql="""
declare @cartegoryid int;
select @cartegoryid=%s;
DECLARE @CategoryName VARCHAR(100);SET @CategoryName='';

WITH DirectReports(ParentCategoryCode, CategoryCode,CategoryName,EmployeeLevel) AS 
(
    SELECT ParentCategoryCode,CategoryCode,CategoryName,0 AS EmployeeLevel
    FROM New_category(NOLOCK)
    WHERE CategoryCode=@cartegoryid
    
    UNION ALL   

    SELECT T1.ParentCategoryCode, T1.CategoryCode,T1.CategoryName,EmployeeLevel+1
    FROM New_category(NOLOCK)  T1
    INNER JOIN DirectReports T2 ON T1.CategoryCode=T2.ParentCategoryCode
)
SELECT @CategoryName=@CategoryName+','+ cast(CategoryCode as varchar(10))
FROM DirectReports ORDER BY EmployeeLevel DESC;

IF (len(@CategoryName) < 1)
begin
    select 'none'
end
else begin
	select SUBSTRING(@CategoryName,2,LEN(@CategoryName)-1)
end
"""
    if lowest_category_id.strip().lower()=="none":
        print "transfter lowest category_id is none return ['none'] directly"
        return ['none']
    #print p1
    sql=sql%lowest_category_id
    rows=db2.select(sql)
    print lowest_category_id,type(lowest_category_id)
    #print rows[0][0]
    result=rows[0][0]#.strip().lower()
    if result=="none":
        return [str(lowest_category_id)]
    else:
        return result.split(",")
        
def getlowestproductcategories(p1):
    "get this product lowsest categories as a list"
    if r1.hexists("all",p1):
        return [eval(r1.hget("all",p1))[-1]]
    #if r1.hexists("low",p1):
    #    return eval(r1.hget("low",p1))
    
    print "---------------%s"%p1
    sql="select distinct c.categorycode from product p inner join clothes c on p.productcode=c.productcode where p.productcode='%s' and c.categorycode is not null"%p1
    print sql
    rows=db2.select(sql)
    print type(rows)
    
    if rows==None or len(rows)==0:
        low=['none']
    else:
        categoryid=rows[0][0]
        low=[str(categoryid)]
    #return [getproductallcategories(p1)[-1]]
    r1.hset("low",p1,low)
    return low
    
def gethighestproductcategory(p1):
    "get topest product belongs categoryid"
    if r1.hexists("high",p1):
        return r1.hget("high",p1)
    #print type(p1)
    #print p1
    lowest_category_id=getlowestproductcategories(p1)[0]#CAUTION:the lowest category ids may have mutiple
    #print "lowest_category_id:%s"%lowest_category_id
    high=getproductallcategories(lowest_category_id)
    if len(high)>0:
        high=high[0]
    else:
        high=lowest_category_id#when high return [],process this special situation
    r1.hset("high",p1,high)
    return high

def _setrediscache():
    "set highest and lowest category id to redis cache"
    #sql="select p.productcode,c.categorycode,p.productname,dbo.getcategoryname(c.categorycode) as categoryname,p.isoff from product p left join clothes c on p.productcode=c.productcode"
    sql="""
SELECT DISTINCT p.ProductCode, c.CategoryCode, p.ProductName, dbo.GetCategoryName(c.CategoryCode) AS categoryname, p.IsOff
FROM         dbo.Clothes AS c RIGHT OUTER JOIN
                      dbo.Product AS p ON p.ProductCode = c.ProductCode
"""
    rows=db2.select(sql)
    print len(rows)
    #low=dict()
    #high=dict()
    #names=dict()
    for i in rows:
        #the second variant categorycode is one of product's lowest category id,
        #the third variant categoryname is list all this product's category name from big to small
        productcode,categorycode,productname,categorynames,isoff=i[0],i[1],i[2],i[3],i[4]
        r1.hset("productnames",productcode,productname)
        r1.hset("productcategories",productcode,categorynames)
        all=getproductallcategoriesbyproductid(productcode)
        r1.hset("all",productcode,all)
        r1.hset("low",productcode,[all[-1]])#[str(categorycode)])
        r1.hset("high",productcode,all[0])#gethighestproductcategory(productcode))
        if isoff==0:
            r1.rpush(categorycode,productcode)#caution:when product isoff info changed or new product add this need update
        
    print "fill redis cache finished"
    
#def getrandomelements2(list,n):
#    """
#        get n random elements from list
#        if n>len(list) then return all elements
#        all return elements will not have repeat
#        e.g.
#            print getrandomelements([1,2,3],2)==>[2,1]
#            
#    """
#    ll=len(list)
#    if ll<=n:
#        return list
#    count=0
#    result=[]
#    productserialcodes=[]
#    total=0
#    while count<n or total>100000:
#        total+=1
#        new=random.randint(0,ll-1)
#        productserialcode=getproductserialcode(list[new])
#        if (new not in result) and (productserialcode not in productserialcodes):
#            count+=1
#            result.append(new)
#            productserialcodes.append(productserialcode)
#            
#    return [list[i] for i in result]
    
def getrandomelements(list,n):
    """
        get n random elements from list
        if n>len(list) then return all elements
        all return elements will not have repeat
        e.g.
            print getrandomelements([1,2,3],2)==>[2,1]
            
    """
    ll=len(list)
    if ll<=n:
        return list
    count=0
    result=[]
    while count<n:
        new=random.randint(0,ll-1)
        if new not in result:
            count+=1
            result.append(new)
    return [list[i] for i in result]
        
def getproductname(p1):
    "产品的名称"
    if r1.hexists("productnames",p1):
        return r1.hget("productnames",p1)
        
    sql="SELECT productname FROM dbo.Product WHERE ProductCode='%s'"%p1
    rows=db2.select(sql)
    if len(rows)==0:
        return "-1"
    else:
        r1.hset("productnames",p1,rows[0][0])
        return rows[0][0]
    
ref_count=0
ref_result=[]
def get20recordsfromtop60percentdata(p1):
    global ref_count,ref_result
    ref_count=0
    ref_result=[]
    dicts=getoriginalrecommend(p1)#CAUTION:you can't use dict as variant
    ll=len(dicts)
    print "7"*100
    print ll
    #ll=100
    #5 10 15 20 25 30 35 40 45 50 55 60
    rate1=[5,3,3,2,2,2,2,1,1,1,1,1]#equal 20
    #print "rate1 len:%s"%len(rate1)
    rate2=[ 0.02*i for i in xrange(1,len(rate1)+1)]
    #print "rate2 len:%s"%len(rate2)
    #print rate2
    #ll=80
    areas=[int(elem*ll) for elem in rate2]
    #areas.insert(0,0)
    #print areas
    productids=dicts.keys()
    #print "-------------->%s"%len(productids)
    productids=productids[:ll]
    def _do(x,y,):
        global ref_count,ref_result
        #print ref_count
        #print x,y
        r=getrandomelements(productids[x:y],rate1[ref_count])
        #print r
        ref_result.extend(r)
        #print "=="
        ref_count+=1
        return y
    reduce(_do,areas,0)
    #getrandomelements(productids,)
    #print ref_result
    #print len(ref_result)
    return ref_result
    
def getforbidencategories(p1):
    highest_category_id=gethighestproductcategory(p1)
    dicts={'101':['139','186']}
    #	nanzhuan                           shiwa
    dicts={'101':['186','321','139','136','360']}
    if dicts.has_key(highest_category_id):
        return dicts[highest_category_id]
    else:
        return []
    
def load2redis():
    #coll=getonlineproductids()|getrecommendproductids()
    #for productid in coll:
    #    _setrediscache(productid)
    _setproductserialcode2redis()
    _setrediscache()
    
def clearredis():
    r1.flushdb()
    #r1.delete("productnames")
    #r1.delete("low")
    #r1.delete("high")
    
def getproductdetail(p1):
    ""
    lowest_category_id=getlowestproductcategories(p1)[0]
    high=gethighestproductcategory(p1)
    all=getproductallcategoriesbyproductid(p1)
    productname=getproductname(p1)
    categories=getproductallcategorynames(p1)
    print "lowest_category_id:%s"%lowest_category_id
    print "hgih:%s"%high
    print "all:%s"%all
    print "categories:%s"%categories.decode("gb18030").encode("utf8")
    print "productname:%s"%productname.decode("gb18030").encode("utf8")

    
def getalllowestcategoryids():
    sql="select distinct categorycode from clothes where categorycode is not null"
    rows=db2.select(sql)
    categoryids=[]
    for i in rows:
        if str(i[0]).lower()<>"none":
            categoryids.append(i[0])
    print categoryids
    return categoryids

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
    #print sql
    rows=db2.select(sql)
    if len(rows)==0:
        return "-1"
    else:
        return rows[0][0]        
    
if __name__=='__main__':
    s=datetime.now()
    #getlowestproductcategories('0001173')
    #print getproductname("412131B").decode("gb18030").encode("utf8")
    #r=getoriginalrecommend('0002699')
    #print r["412131B"]
    #import sys
    #sys.exit(0)
    #print getcategoryname('136').decode("gb18030").encode("utf8")
    #import sys
    #sys.exit(0)
    #_setproductserialcode2redis()
    #import sys
    #sys.exit(0)
    #lowest_category_id='58'
    #print getproductallcategories(lowest_category_id)
    #for categorycode in getalllowestcategoryids():
    #    print categorycode
    #    print getproductallcategories(categorycode)
    #getproductallcategories('None')
    #getproductallcategories('none')
    #getproductallcategories(None)
    #clearredis()
    #load2redis()
    #import sys
    #sys.exit(0)

    #print getproductallcategorynames("0001847").decode("gb18030").encode("utf8")
    #import sys
    #sys.exit(0)
    #lowest_category_id=getlowestproductcategories("0001206")[0]
    #print "lowest:%s"%lowest_category_id
    #print getproductallcategories(lowest_category_id)
    #print "high:%s"%gethighestproductcategory('0001206')
    #getproductdetail("0001847")
    #getproductdetail("0004396")
    #import sys
    #sys.exit(0)
    #0001847
    productid='0002699'
    r=getoriginalrecommend(productid)
    #getoriginalrecommend('0000108')
    #import sys
    #sys.exit(0)
    
    #print getproductallcategories("103")
    
    result=get20recordsfromtop60percentdata(productid)
    #print getrandomelements([1,2,3],2)
    for productid in result:
	try:
	    print getproductname(productid).decode("gb18030").encode("utf8"),r[productid],productid
	except:
	    print "error",productid
    #print "========"
    #print result
    #print len(result)
    #print set(getonlineproductids())&set(result)
    #print "--------"
    #print len(set(getonlineproductids())&set(getrecommendproductids()))
    e=datetime.now()
    print "cost time :%s"%(e-s).seconds
    
    
    
    