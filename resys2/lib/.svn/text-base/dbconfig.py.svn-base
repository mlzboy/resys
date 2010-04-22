#!/usr/bin/env python
# -*- coding:utf8 -*-
#注意使用trusted有问题
#设置全局的变量
import pymssql

server = r'192.168.0.75'  
user = 'maolingzhi'  
password = 'abc@12345'  
database = 'SCM'
trusted=False#有点问题

server = r'10.3.10.90'  
user = 'abc'  
password = 'abc'  
database = 'DMDM'
trusted=False#有点问题

def connectdb_invoke_callback_and_return_recordset(istrust,server, user, password, database, sql,callback):  
    isErr=False
    try:
        if not istrust:
            db = pymssql.connect(host = server,  
                        database = database,  
                        user = user,  
                        password = password,  
                        login_timeout = 10)
        else:
            db=pymssql.connect(host=server, trusted=True) 
            
        cur = db.cursor()  
        cur.execute(sql)
        return callback(cur)
    except Exception, e:
        print e
        isErr=True
        return isErr  
    finally:  
        try: 
            db.commit()
            db.close()  
        except: pass
    
def select(sql=None):
    if sql is None:
        return None
    def callback(cur):
        row=cur.fetchall()
        return row
    return connectdb_invoke_callback_and_return_recordset(trusted,server, user, password, database, sql,callback)

def execute(sql=None):
    """
    用来操作insert,update
    """
    if sql is None:
        return None
    def callback(cur):
        return cur.rowcount
    return connectdb_invoke_callback_and_return_recordset(trusted,server, user, password, database, sql,callback)

if __name__=="__main__":
    sql="select top 10 * from product;"
    rows=select(sql)
    print len(rows)
