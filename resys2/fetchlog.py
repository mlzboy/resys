#! usr/bin/env python
#encoding=utf8
"""
brief:
this script purpose is try to fetch info from log text
"""
from datetime import datetime
import re
import redis
r1=redis.Redis(host="192.168.1.7",db=1)
r2=redis.Redis(host="192.168.1.7",db=2)
r3=redis.Redis(host="192.168.1.7",db=3)


path="/home/mlzboy/weblog/20100401/E:/weblog/E:/weblog"
name="2010-04-01_00.00.log.import.finished"
fullname=path+"//"+name
lines=open(fullname,"r").readlines()
print len(lines)
print datetime.now()
print datetime.strptime("2010-04-01 00:04:57.277","%Y-%m-%d %H:%M:%S.%f")
#f=open("hahahaha.txt","w")
#for line in lines:
#    list=line.split()
#    for elem in list:
#        print elem
#        f.write(elem+"\n")
#    if len(list)<>25:
#        print "error,not equal 25",len(list)
#        break
#f.close
count=0
for subject in lines:
    reobj = re.compile(r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{1,3}).{4,}?.*?(?P<ip>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})\s*(?P<name>.*?)\s(?P<sessionid>.*?)\s.*?\s(?P<link>.*?)\s")
    if reobj.search(subject):
        count+=1

print count

#撰写逻辑将数据线往redis里存放
#本次抽取的数据为已登录的用户的数据，对个别意义不大的数据，排除在计算的范围外（比如，团购账号）
#1)检查数据库里是否有此sessionid的数据，
#如果name为匿名则继续往后插入，
#如果name不为匿名，则将前面此sessionid是匿名都变为该name
#将用户访问页面的产品单独插入一个productids的集合储存
#对于登录的用户也使用一个usernames来储存，
#动态生成产品和user的矩阵




