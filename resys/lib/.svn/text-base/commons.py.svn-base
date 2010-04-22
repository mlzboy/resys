#! /usr/bin/env python
#coding=utf-8
def save2file(list,filename):
    """
    将内容保存到文本中
    """
    import codecs
    fp = codecs.open( filename, "w" )
    fp.write(codecs.BOM_UTF8)
    for content in list:
#        fp.write((content or "")+"\r\n")
        fp.write(content or "")
    fp.close

def getcwd():
    "F:\dm_app\tag2\lib"
    import sys
    import os
    pwd = sys.path[0]
    if os.path.isfile(pwd):
        pwd = os.path.dirname(pwd)
    return pwd

def getpwd():
    "F:\dm_app\tag2"
    cwd=getcwd()
    a=cwd.split("\\")
    if(len(a)<=1):
        #print "hha"
        a=cwd.split("/")
        return "/".join(a[:-1])    
    else:
        return "\\".join(a[:-1])

if __name__=="__main__":
    print getpwd()