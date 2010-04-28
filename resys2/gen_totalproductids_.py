#! usr/bin/env python
#encoding=utf8
"""
这个脚本的目的同gen_totalproductids.py但是实现上变更了：
1）不在去考虑和现在数据库上的架上的产品做交集了
2）使用从网站下订单的用户和在r2中出现的用户做交集做为粗用户集，并在此基础上，过滤掉一批，浏览纪录少于4个的用户，作为最终用户集
3）将最终用户集中看过，下过单的productid构建一个集合来储存
=====
1)2)3)来确定userids和productids

4）根据评分函数，将用户的浏览纪录进行评分，并在此基础上，对于用户购买过的商品进行再评价，还是使用hash结构在r9
这里的评价，直接进行归一化处理
=====
在计算item相似性之前，将评价准备好
5）生成两两计算的任务集（先手工实现6再回后做这一步 还是使用r6
6）使用pipeline来生成直接运算，对于每一列，使用一次后进行一下cache,避免运算，可以计算一下，这两种方法哪种耗时r10
在比较相似时，对于一个有评价，另一个没有评价的项也加入标识，使用一定的算法，在计算之前给上这个值，暂时就给1最终应该是0.2
7) 将每个产品的最近邻进行缓存储存r11
8)写一个实时预测的函数传入userid,根据用户己往购买过的类别，及相应的搭配规则到到几个类别下找相似度最高的返回
=====
choice what way to deploy the whole application
try to use the mongodb as the backend engine
think the fullstack solution carefully
try to build apache server,web framework,soap,fullstack open source soluation
use nginix replace apache and use scgi or fast-cgi to as python interprive
process match rules
test deploy pression and whole package of things
you only have 3 days
you need very carefully
say holidays to boss luan

productid--->find belongs which category
find category match rule
find top 5 recommend is contains one of this category rule,
if didn't random select one

this approach need use sql & cache

i decide use fullstack open source soluation to archive this project

使用dreque的速度还是太慢，一个一个任务传递有关系，看能不能一百个任务一个包来执行派发，
对于cache的部分考虑在本地建一个同步的部分来加速，任务派发的点也可以多点，使用redis的主从，
再不行，可以考虑使用celery
                               


使用item-based作为主要结果，以规则搭配为辅
为了使用规则搭配，使用几个set及来处理

生成矩阵，productid在矩阵中的顺序储存在r3中
用于将在r2的用户浏览过的产品进行记录到r3的productids中，看总共有多少产品
use_productids--->list
productids---->zset
onlineproductids----->zset
将上面productids生成的一些有错误的id,主要是数字小于7通过db中的架上数据来做交集，
当前结果是架上有1869个数据，而数据中拥有1130的数据
"""
from __future__ import division#must occur at the beginning of the file
from math import sqrt,acos,log
from datetime import datetime
#from lib.sqlserver import SqlServer
from dreque import Dreque
from dreque import DrequeWorker
from multiprocessing import Process
import time
import redis
ip='192.168.1.7'
r2=redis.Redis(db=2,host=ip)#username集
r3=redis.Redis(db=3,host=ip)#存放配置
r4=redis.Redis(db=4,host=ip)#store user shopping productid records
r5=redis.Redis(db=5,host=ip)#store userids 's ranks,most key copy from r2
#r6存放任务队列
r6=redis.Redis(db=6,host=ip)
dreque = Dreque((ip,6379),db=6)#储存任务队列
r7=redis.Redis(db=6,host=ip)#存放cache关于，每一行productid有哪几个用户有评价分值
#db=SqlServer("192.168.0.92","maolingzhi","zhoubt","SCM")
#def onlineproductids():
#    "获取在架上的产品id集"
#    sql="select productcode from product where isoff=0"
#    rows=db.select(sql)
#    for i in rows:
#        r3.zadd("onlineproductids",i[0],0)
#    print r3.zcard("onlineproductids")
#    return r3.zrange("onlineproductids",0,-1)
#
#
#
#print "totoal users:%s"%r2.dbsize()
#usernames=r2.keys()
##for username in usernames:
##    dict=r2.hgetall(username)
##    for productid in dict.keys():
##        r3.zadd("productids",productid,0)
#print "total products:%s"%r3.zcard("productids")
#rough_productids=r3.zrange("productids",0,-1)
#
#
#
#db_productids=onlineproductids()
#
#intersation=list(set(rough_productids)&set(db_productids))
#print len(intersation)
#
#
#for productid in intersation:
#    r3.lpush("use_productids",productid)#这里意外使用了lpush,按理应该使用rpush
#print "================="
#print r3.llen("use_productids")
##import sys
##sys.exit(0)
#
#
#e=datetime.now()
#print "cost time:%s"%(e-s).seconds
def make_list(db,key,value_list):
    "在db这个数据库中向键为key的list type填充value_list这个list中的所有值"
    pipe=db.pipeline()
    for i in value_list:
        #db.rpush(key,i)
        pipe.rpush(key,i)
    pipe.execute()
        
def make_set(db,key,set_list):
    pipe=db.pipeline()
    for elem in set_list:
        #db.sadd(key,elem)
        pipe.sadd(key,elem)
    pipe.execute()
        
def getdbuseridslen():
    print r3.llen("dbuserids")

def getloguseridslen():
    print r3.llen("loguserids")
    
def getroughuseridslen():
    print r3.llen("roughuserids")

def getuseridslen():
    print r3.llen("userids")

def getdbuserids():
    """
    get user transcation userids from db using export_user_shopping_result.py's
    result from r4
    r3 use to store setting fiedls
    put result into r3,key is dbuserids
    """
    r3.delete("dbuserids")
    make_list(r3,"dbuserids",r4.keys())
    
#def gendbuserids():
#    "import from dbuserid.csv"
#    r4.flushdb()
#    pipe=r4.pipeline()
#    import codecs
#    f = codecs.open("dbuserid.csv","r","gb18030")
#    for line in f.readlines():
#        userid,productid,other=line.strip().split(",")
#        #r4.rpush(userid,productid)
#        pipe.rpush(userid,productid)
#    f.close()
#    pipe.execute()


def getloguserids():
    """
    get user visitor userids from logs using unziplog.py's result from r2
    put result into r3,key is loguserids
    """
    r3.delete("loguserids")
    make_list(r3,"loguserids",r2.keys())
    
def getroughuserids():
    "get intersation of loguserids & dbuserids as the rought userids"
    dbuserids=r3.lrange("dbuserids",0,-1)
    loguserids=r3.lrange("loguserids",0,-1)
    roughuserids=list(set(dbuserids)&set(loguserids))
    r3.delete("roughuserids")
    make_list(r3,"roughuserids",roughuserids)

def getuserids():
    """
    get final userids
    based on roughuserids select which visiter product is greate equal then 4's userid as final userids
    """
    roughuserids=r3.lrange("roughuserids",0,-1)
    userids=[]
    for userid in roughuserids:
        ll=r2.hlen(userid)
        if ll>=10 and ll<=30:
            userids.append(userid)
    r3.delete("userids")
    make_list(r3,"userids",userids)

def checkroughuserids():
    roughuserids=r3.lrange("roughuserids",0,-1)
    dict={}
    for userid in roughuserids:
        ll=str(r2.hlen(userid))
        if ll in dict:
            dict[ll]+=1
        else:
            dict[ll]=1
    for i in xrange(1,100):
        try:
            print "%s==>%s"%(i,dict[str(i)])
        except:
            pass
    c=0
    #for k,v in dict.iteritems():
    #   c+=v
    for i in xrange(10,31):
        try:
            v=dict[str(i)]
            c+=v
        except:
            pass
    print "c=%s"%c

        
    
def getproductids():
    """
    get productids from userids collections' transcation recorods and this users visistor recored
    use set as productid's container
    """
    userids=r3.lrange("userids",0,-1)
    #get trancations' productids
    container=set()
    for userid in userids:
        container=container.union(set(r4.lrange(userid,0,-1)))
        container=container.union(set(r2.hkeys(userid)))
    
    make_list(r3,"productids",container)
    
def getproductidslen():
    print r3.llen("productids")

def genusername2userids():
    import redis
    ip='192.168.1.7'
    r3=redis.Redis(db=3,host=ip)
    #print r3.keys()
    r3.delete("username2userids")
    username2id={}
    f = open("userid.txt","r") 
    for line in f.readlines():
        userid,username=line.strip().split(",")
        username2id[username]=userid
    f.close()
    r3.hmset("username2userids",username2id)
    print r3.hlen("username2userids")    

def rename_r2_username2userid():
    "change r2 username key to userid key"
    print "r2 dbsize:%s"%r2.dbsize()
    username2userids=r3.hgetall("username2userids")
    delete=0
    rename=0
    for username in r2.keys():
        if username in username2userids:
            r2.rename(username,username2userids[username])
            rename+=1
        else:
            r2.delete(username)
            delete+=1
    print "delete=%s"%delete
    print "rename=%s"%rename

def rank(clicks):
    "根据点击次数来确定其评分"
    if clicks<1:
        result=0.2
    if clicks==1:
        result=0.23
    if clicks==2:
        result=0.48
    if clicks==3:
        result=0.6
    if clicks>3:
        result=0.65
    if clicks>6:
        result=0.75
    if clicks>8:
        result=0.8
    if clicks>10:
        result=0.85
    if clicks>12:
        result=0.9
    return result

def ranking():
    r5.flushdb()
    userids=r3.lrange("userids",0,-1)
    #p5=r5.pipeline()
    for userid in userids:
        dict=r2.hgetall(userid)
        for k,v in dict.iteritems():
           dict[k]=rank(int(v))
        r5.hmset(userid,dict)
    #    p5.hmset(userid,dict)
    #p5.execute()
    
def user_brought_ranking():
    "添加用户购买记录的评价为1"
    userids=r3.lrange("userids",0,-1)
    for userid in userids:
        productids=r4.lrange(userid,0,-1)
        for productid in productids:
            r5.hset(userid,productid,1.0)

def sim(p1,p2):
    "余弦相似度"
    p1_mo=sqrt(sum([x**2 for x in p1]))
    p2_mo=sqrt(sum([x**2 for x in p2]))
    p1p2_dianji=0
    for i in xrange(len(p1)):
        p1p2_dianji+=p1[i]*p2[i] 
    try:
        return p1p2_dianji/(p1_mo*p2_mo)
    except:
        return 0.0 
            
def item_simarlity(productid1,productid2):
    "对两个产品进行item相似度计算"
    userids=r3.lrange("userids",0,-1)
    p5=r5.pipeline()
    def getuserids(productid):
        if r7.exists(productid):
            return r7.lrange(productid,0,-1)#作cache
            
        for userid in userids:
            p5.hexists(userid,productid)
        p1=p5.execute()
        #print p1
        #print len(filter(lambda x:x==True,p1))
        container=[]
        for idx,elem in enumerate(p1):
            if elem:
                container.append(userids[idx])
        #print len(container)
        #缓存结果
        make_list(r7,productid,container)
        return container
    a=getuserids(productid1)
    b=getuserids(productid2)
    #print set(a)&set(b)
    c=set(a)|set(b)
    #print c
    #print len(c)
    calc_userids=c
    def getranks(userids,productid):
        for userid in userids:
            p5.hget(userid,productid)
        p1=p5.execute()
        #print p1
        def condition(elem):
            if elem is None:
                return 0.2
            else:
                return float(elem)
        p1=map(condition,p1)
        #print p1
        return p1
        
    result=sim(getranks(c,productid1),getranks(c,productid2))
    print result
    r3.hset("sims","%s:%s"%(productid1,productid2),result)

def gen_taskqueues_backup():
    "将所有要提交的子任务，在r3的productids上作一个备份,以便于检测遗失任务"
    queue=[]
    def _do(x,y):
        queue.append("%s:%s"%(x,y))    
        return x

    keys=r3.lrange("productids",0,-1)
    print len(keys)
    for i in xrange(0,len(keys)):
        reduce(_do,keys[i:])
    print "queue len:%s"%len(queue)
    r3.delete("queue")
    make_list(r3,"queue",queue)

def taskqueue(productid1,productid2):
    dreque.enqueue("queue",item_simarlity,productid1,productid2)

def gen_taskqueues(taskqueues=None):
    "generate task queues"
    dreque.redis.flushdb()#清空原有任务队列
    def _do(x,y):
        taskqueue(x,y)
        return x
    if taskqueues is None:
        keys=r3.lrange("productids",0,-1)
        print len(keys)
        for i in xrange(0,len(keys)):
            reduce(_do,keys[i:])
    else:
        #处理遗留队列
        for task in taskqueues:
            productid1,productid2=task.split(":")
            taskqueue(productid1,productid2)



def consume_taskqueue():
    worker = DrequeWorker(["queue"], (ip,6379),db=6)
    worker.work(0.0001)#TODO:why use 0 will escape,only execute once?

def consume_mult_taskqueues(num=5):
    for i in xrange(0,num):
        worker_child = Process(target=consume_taskqueue, args=())
        worker_child.start()
        time.sleep(1)
        
def get_legency_taskqueues():
    finished_taskqueues=set(r3.hkeys("sims"))
    all_taskqueues=set(r3.lrange("queue",0,-1))
    print "finished_taskqueues:%s"%len(finished_taskqueues)
    print "all_taskqueues:%s"%len(all_taskqueues)
    lost_taskqueues=all_taskqueues.difference(finished_taskqueues)
    print "lost_taskqueues:%s"%len(lost_taskqueues)
    
def gen_legency_taskqueues():
    finished_taskqueues=set(r3.hkeys("sims"))
    all_taskqueues=set(r3.lrange("queue",0,-1))
    lost_taskqueues=all_taskqueues.difference(finished_taskqueues)
    gen_taskqueues(taskqueues=lost_taskqueues)

def clear():
    r6.flushdb()
    r7.flushdb()
    r3.delete("sims")
    print r3.llen('queue')

def savefile(filename,lines_list):
    f= open(filename,mode="w")
    f.writelines(lines_list)
    f.close()
    
def export_simlarity_result2csv():
    dict=r3.hgetall("sims")
    lines=[]
    for k,v in dict.iteritems():
        p1,p2=k.split(":")
        lines.append("%s,%s,%s\r\n"%(p1,p2,result))
    savefile("result.csv",lines)

if __name__=="__main__":
    s=datetime.now()
    #调用export_user_shopping_result.py
    #getdbuserids()
    #getdbuseridslen()
    #genusername2userids()
    #rename_r2_username2userid()
    #getloguserids()
    #getloguseridslen()
    #getroughuserids()
    #getroughuseridslen()
    #checkroughuserids()
    #getuserids()
    #getuseridslen()
    #getproductids()
    #getproductidslen()
    #above finished generate userids & productids
    
    #ranking()
    #user_brought_ranking()
    #以上完成评价及归一化处理
    #item_simarlity('0002640','0002719')
    #gen_taskqueues_backup()
    #taskqueue('0002640','0002719')
    #consume_taskqueue()
    #gen_taskqueues()
    #consume_taskqueue()
    #consume_mult_taskqueues()
    #get_legency_taskqueues()
    #get_legency_taskqueues
    #clear()
    
    #execute sequence
    #clear()
    #gen_taskqueues()
    #consume_mult_taskqueues()
    export_simlarity_result2csv()
    
    print "done!"
    e=datetime.now()
    print "cost time:%s"%(e-s).seconds
    

