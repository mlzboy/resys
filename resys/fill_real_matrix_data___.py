#! usr/bin/env python
#encoding=gb18030
"""
根据由fill_blank_matrix_data___.py生成的blank_matrix基础上进行填充数据
这个脚本使用了
localhost:6379:db1
10.3.11.178:6379:db2
两个库
"""
import redis
r0=redis.Redis()#分词后的数据
r1=redis.Redis(host='localhost',port=6379,db=1)#各分词的统计数据，及噪音处理
#这里的ip是临时用的
r2=redis.Redis(host='10.3.11.178',port=6379,db=2)#生成matrix data
usewords_dict=r1.hgetall("usewords")
wordpositions_dict=r1.hgetall("wordpositions")
def get_word_position(word):
    "return position in matrix,start is 1"
    if word in usewords_dict:
        return int(wordpositions_dict[word])-1
    else:
        return -1
        
for key in r0.keys():
    whole_words_list=r0.lrange(key,0,-1)
    print whole_words_list
    for word in whole_words_list:
        pos=get_word_position(word)
        if pos>-1:
            print "pos"
            print pos
            r2.lset(key,pos,1+pos)
            v=r2.lrange(key,pos,1)#从pos位置开始的一个
            print "v的类型"
            print type(v)
            print v
            if v[0]==1:
                print "插入正确"
            k=r1.hget("positionwords",pos+1)
            if k==word:
                print "good"
                break