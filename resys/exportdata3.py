#! /usr/bin/env python
#coding=utf-8
"""
从数据库中导出数据，一条一个文本文件
文件名以产品的productcode为主名称，
先不放描述文件，
对描述文件使用C#的版的中科院分词程序进行单独处理
之后再和这上程序生成的文件进行合并
目前是有1775条有效记录
"""
from lib.dbconfig import *
from lib.commons import save2file
storepath="exportdata/original"
sql="SELECT productcode,productname,intro,dbo.getcategoryname(categorycode) as category FROM  Product p where isoff=0"


rows=select(sql)
print type(rows)
print len(rows)
count=0
import chardet
import time
import redis
r=redis.Redis(host='10.3.11.178',port=6379,db=1)
for productcode,productname,intro,category in rows:
    #save2file([productcode,productname,intro,category],storepath+"/"+str(productcode)+".txt")
    count+=1
    if count>1000000:
        break
##    productcode=str(productcode).strip().decode("utf8")
##    print productcode
##    s=unicode(productcode,"utf8").decode("utf8")
##    print s
##    print type(s)
##    print chardet.detect(s)
#    productname=str(productname).strip()
#    print "==="
#    print productcode
##    time.sleep(1)
##    print chardet.detect(productcode)
#    print chardet.detect(productname)
#    print chardet.detect(category)
#    print chardet.detect(intro or "")
#
#    if intro is None:
##        print type(text)
##        print type(intro)
#        text=productname.strip()+","+category.strip()
#    else:
#        text=productname.strip()+","+category.strip()+","+intro.strip()
#    print text   
##    save2file(text.decode("gb2312").encode("utf8"),storepath+"/"+str(productcode)+".txt")
#    save2file(text,storepath+"/"+str(productcode)+".txt")
    def preprocess(v):
        if v is None:
            return None
        result=str(v).strip()
        if len(result)<>0:
            return result
        else:
            return None
    
    _=preprocess
    productcode=_(productcode)
    productname=_(productname)
    intro=_(intro)
    category=_(intro)
    r.rpush(productcode,productname)
    r.rpush(productcode,intro)
    r.rpush(productcode,category)
    
    