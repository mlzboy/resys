# !usr/bin/env python
#encoding=gb18030
"""
统计在redis中的各文档中词的次数到key为wordcounts的hash中
"""
import redis
r0=redis.Redis()
r1=redis.Redis(host='localhost',port=6379,db=1)
r1.delete("wordcounts")
r1.delete('usewords')
r1.delete('wordpositions')
r1.delete('positionwords')
print type(r0.keys())
for key in r0.keys():
    doc=r0.lrange(key,0,-1)#a product's whole keywords collection
    for keyword in doc:
        if r1.hexists("wordcounts",keyword):
            count=r1.hget("wordcounts",keyword)
            #print "===="
            #print type(count)
            #print count
            r1.hset("wordcounts",keyword,int(count)+1)
        else:
            r1.hset("wordcounts",keyword,1)

print r1.hlen("wordcounts")
print "-"*20
words_dict=r1.hgetall("wordcounts")
#循环输出
result=[]
for keyword,times in words_dict.iteritems():
    line="%s,%s"%(keyword,times)
    print line
    result.append(line+"\n")
#将结果存成csv    
f=open("wordcounts.csv","w")#生成的是最原始的
f.write("".join(result))
f.close()
#将次数为1的清除不用，剩下的存放到usewords
for keyword,times in words_dict.iteritems():
    #print type(times)#为str
    if int(times)>1:
        r1.hset("usewords",keyword,times)
print "wordscount len:%s"%r1.hlen("wordcounts")
print "usewords len:%s"%r1.hlen("usewords")
#为usewords中的keyword生成在Matrix中的position,存放在wordpositions
usewords_len=r1.hlen("usewords")
usewords_dict=r1.hgetall("usewords")
usewords_count=0
for keyword,times in usewords_dict.iteritems():
    usewords_count+=1
    r1.hset("wordpositions",keyword,usewords_count)
print "wordpositions len:%s"%r1.hlen("wordpositions")
#positionwords,key为position,value为word，和wordpositions倒过来,就是进行了反转
wordpositions_dict=r1.hgetall("wordpositions")
for keyword,position in wordpositions_dict.iteritems():
    r1.hset("positionwords",position,keyword)
print "positionwords len:%s"%r1.hlen("positionwords")



