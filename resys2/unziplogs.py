#!usr/bin/env python
#encoding=utf8
import os
import re
from lib import filehelper
from datetime import datetime
import redis
ip="192.168.1.7"
ip="localhost"
r1=redis.Redis(host=ip,db=1)#以sessionid为key
r2=redis.Redis(host=ip,db=2)#以username为key
r3=redis.Redis(host=ip,db=3)#暂无用

r1.flushdb()
r2.flushdb()
#r3.flushdb()
"""
brief:
this script try to batch extract compressed logs to specifieced location
"""
original_compressed_logs_src="/home/mlzboy/logs"#确保该文件只有
destination="/home/mlzboy/logs_process"
temp="/home/mlzboy/logs_temp"

def cleartemp():
    if not filehelper.hasfolder(temp):
        filehelper.createfolders(temp)
    filehelper.clearfolder(temp)

def cleardestination():
    if not filehelper.hasfolder(destination):
        filehelper.createfolders(destination)
    filehelper.clearfolder(destination)
    
#def clearoriginal():
#    filehelper.clearfolder(original_compressed_logs_src)

cleartemp()
cleardestination()

#1)列出所有original_compressed_logs_src下的zip压缩文件
def _sorted(filenames):
    "针对有2010-04-01.new.zip的情况，如果有这样形式的文件，让它紧随2010-04-01之后进行处理"
    def condition(subject):
        if re.search(r"\d{4}-\d{1,2}-\d{1,2}.zip", subject):
            return True
        else:
            return False
    base_list=filter(condition,filenames)
    extend_list=base_list[::]
    count=0
    for idx,elem in enumerate(base_list):
        extend_filename=elem[:-4]+".new.zip"
        if extend_filename in filenames:
            extend_list.insert(idx+count+1,extend_filename)
            count+=1
    return extend_list
            
            
def _logparser(path):
    lines=open(path,"r").readlines()
    print "*"*100
    print len(lines)
    #print datetime.now()
    #print datetime.strptime("2010-04-01 00:04:57.277","%Y-%m-%d %H:%M:%S.%f")
    #count=0
    for subject in lines:
        #reobj = re.compile(r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{1,3}).{4,}?.*?(?P<ip>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})\s*(?P<name>.*?)\s(?P<sessionid>.*?)\s.*?\s(?P<link>.*?)\s")
        #if reobj.search(subject):
        #    count+=1
            #撰写逻辑将数据线往redis里存放
            #本次抽取的数据为已登录的用户的数据，对个别意义不大的数据，排除在计算的范围外（比如，团购账号）
            #1)检查数据库里是否有此sessionid的数据，
            #如果name为匿名则继续往后插入，
            #如果name不为匿名，则将前面此sessionid是匿名都变为该name
            #将用户访问页面的产品单独插入一个productids的集合储存
            #对于登录的用户也使用一个usernames来储存，
            #动态生成产品和user的矩阵
            
    #print count
        for match in re.finditer(r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{1,3}).{4,}?.*?(?P<ip>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})\s*(?P<name>.*?)\s(?P<sessionid>.*?)\s.*?\s(?P<link>.*?)\s", subject):
            # match start: match.start()
            # match end (exclusive): match.end()
            # matched text: match.group()
            time=datetime.strptime(match.group("time"),"%Y-%m-%d %H:%M:%S.%f")
            ip=match.group("ip")
            name=match.group("name")
            sessionid=match.group("sessionid")
            link=match.group("link")
            #get productid from link
            match = re.search(r"http://www.vancl.com/styles/styledetail/.*(?P<productid>\d{7,}).*.mvc", link)
            if match:
                    productid= match.group("productid")
            else:
                match = re.search(r"http://www.vancl.com/styles/DoProductView/(?P<productid>\d{7,}).*.mvc", subject)
                if match:
                    productid = match.group("productid")
                else:
                    productid = None


            if productid is None:
                pass
            elif name=="anonymous":
                if r1.hexists(sessionid,productid):
                    r1.hincrby(sessionid,productid)
                else:
                    r1.hset(sessionid,productid,1)
                #r1.hset(sessionid,)
            else:
                #查找r1中sessionid为此的集，如果有将这个集合移动到r2,同时加新的记录
                if not r2.exists(name):
                    if r1.exists(sessionid):
                        r1.move(sessionid,2)
                        r2.rename(sessionid,name)
                else:
                    if r1.exists(sessionid):
                        r1_dict=r1.hgetall(sessionid)
                        r2_dict=r2.hgetall(name)
                        for k,v in r1_dict.iteritems():
                            if k in r2_dict:
                                r2_dict[k]=int(r2_dict[k])+int(v)
                            else:
                                r2_dict[k]=int(v)
                        r2.hmset(name,r2_dict)
                #加入这条新的记录
                if r2.hexists(name,productid):
                    r2.hincrby(name,productid)
                else:
                    r2.hset(name,productid,1)



s=datetime.now()
for parent,dirnames,filenames in os.walk(original_compressed_logs_src):
    print filenames
    filenames=_sorted(filenames)
    print filenames
    #break
    for filename in filenames:
        print filename
        single_zipfile_path=os.path.join(parent,filename)
        #将单个的文件解压缩到destination变量的目录下
        import zipfile  
        z = zipfile.ZipFile(single_zipfile_path, 'r')
        base_list=[]
        for f in z.namelist():
            if "new" not in f:
                base_list.append(f)
        if len(base_list)>1:
            base_list=sorted(base_list)
        print base_list#理好顺序的zip文件列表(每隔五分钟)
        for elem in base_list:
            z.extract(elem, destination)
            #对解压出的文件进行处理
            #对刚解压出的5分钟的日志压缩文件再解压
            five_log_path=os.path.join(destination,elem)
            zz=zipfile.ZipFile(five_log_path,'r')
            print "====================="
            print zz.namelist()
            zz.extractall(path=temp)
            for file in zz.namelist():
                _logparser(os.path.join(temp,file))
            zz.close()
            cleartemp()
            filehelper.delfile(five_log_path)
            
            
        z.close()
        #import sys
        #sys.exit(0)

e=datetime.now()
print "cost time:%s"%(e-s).seconds
