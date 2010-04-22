#! /usr/bin/env python
#coding=utf-8
#import sys
#print sys.path
#from pymmseg import mmseg
#mmseg.dict_load_defaults()
import chardet
import redis
r=redis.Redis(host='10.3.11.178',port=6379,db=1)
#r['foo']='bar'
#print r.get('foo')
#print r.type("foo")
#r.rpush("aa","cc")
#print r.type("aa")
#print r.lindex('aa',0)
#print r.rpush("aa","dd")
#print r.lindex('aa',1)
#print "-------------"
#print len(r.lrange('aa',0,-1))
#print r.lrange('aa',0,-1)
print r.lrange('00000001',0,0)
a=r.lrange('00000001',0,0)[0]
print a
print len(r.keys())
#algor = mmseg.Algorithm(a)
#for tok in algor:
#    print "--"
#    print chardet.detect(tok.text)
#    print '%s [%d..%d]' % (tok.text, tok.start, tok.end)

