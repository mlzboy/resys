#! /usr/bin/env python
#coding=utf-8
import chardet
a="123123123"
print a
print type(a)
print chardet.detect(a)
a=unicode(a,"ascii")
print type(a)
print a.encode("utf8")
print chardet.detect(a.encode("utf8"))
