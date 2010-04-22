#! usr/bin/env python
#encoding=gb18030
"""
使用positions这个sorted type生成一个r3,一行一行的验证由fill_real_matrix_data____.py填充的数据的正确性
这个脚本使用了
localhost:6379:db1
localhost:6381:db2
localhost:6380:db2
3个库
"""
import redis
from datetime import datetime
start=datetime.now()
r0=redis.Redis()#分词后的数据
r1=redis.Redis(host='localhost',port=6379,db=1)#各分词的统计数据，及噪音处理
#这里的ip是临时用的
#r2=redis.Redis(host='10.3.11.178',port=6379,db=2)#生成matrix data
r2=redis.Redis(host='127.0.0.1',port=6381,db=2)#生成matrix data
r2_=redis.Redis(port=6380,db=2)#来自slave1的使用另一种方法生成的matrix data
usewords_dict=r1.hgetall("usewords")
wordpositions_dict=r1.hgetall("wordpositions")

def get_word_position(word):
    "return position in matrix,start is 1"
    if word in usewords_dict:
        #print word
        return r1.zrank('positions',word)
    else:
        return -1

for key in r0.keys():
    whole_words_list=r0.lrange(key,0,-1)
    for word in whole_words_list:
        pos=get_word_position(word)
        if pos>-1:
            r2.lset(key,pos,1)

def issame(list1,list2):
    if len(list1)<>len(list2):
        return False
    for idx,val in enumerate(list1):
        if list1[idx]<>list1[idx]:
            return False
    return True
isErr=False        
for key in r0.keys():
    if issame(r2.lrange(key,0,-1),r2_.lrange(key,0,-1))==False:
        print "有不同，两种方法生成的不一样"
        isErr=True
        break

end=datetime.now()
if isErr:
    print "两种方式生成数据有不同"
else:
    print "OK,no problem~"
print "cost time:%ss"%(end-start).seconds