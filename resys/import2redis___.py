#! usr/bin/env python
#encoding=gb18030
"""
将数据导入到本地的redis,ver=1.3.7
"""
import re
import os
import redis
import ictclas2009.ictclas as ictclas
import ictclas2009.pyict as pyict
import chardet
from datetime import datetime
#参数设置
r=redis.Redis()
r.flushdb()
path="exportdata/original"
debug=False
pyict.ict_init()
execcount=0
start=datetime.now()

for parent,dirnames,filenames in os.walk(path):
    for filename in filenames:
        main,ext=os.path.splitext(filename)
        if(ext==".txt"):
            execcount+=1
            print "execcount-------------------------------------------------=%s"%execcount
            p=os.path.join(parent,filename)
            content=open(p).read()
            print content.decode('utf8').encode("gb18030")
            print type(content)
            print chardet.detect(content)
            content=content.decode('utf8').encode("gb18030")
            print "===================="
            count = ictclas.process_str_ret_word_count(content)
            #print "Count:%s"%(count)
            li = ictclas.process_str_ret_list(content)
            #print "-"*8
            #for i in li:
                #print i.start, i.length, i.ipos, i.spos, i.word_id, i.word_type, i.weight, content[i.start:(i.start+i.length)]
            print "-"*8
            kw = ictclas.keyword(len(li))
            for i in kw:
                print i.start, i.length, i.ipos, i.spos, i.word_id, i.word_type, i.weight, content[i.start:(i.start+i.length)]
            print "-"*8
            print "set pos map:%s"%(ictclas.POSMAP.ICT_SECOND)
            if debug==True and execcount>30:
                break;
            def checkspos(s):
                z=re.match('.*?[axtn].*?',s)
                if z:
                    return True
                else:
                    return False
            print "@"*20
            for i in kw:
                if i.length>2 and checkspos(i.spos)==True:
                    v=content[i.start:(i.start+i.length)]
                    print v
                    r.rpush(main,v)
end=datetime.now()
print "total txt files:%s"%execcount
print "cost time:%ss"%(end-start).seconds
                
            