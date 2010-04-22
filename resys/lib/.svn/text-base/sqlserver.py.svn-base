#! usr/bin/env python
#encoding=utf8
import pymssql
class SqlServer():
    "sqlserver数据库操作类"
    
    def __init__(self,server,user,password,database,trusted=False):
        self.server=server
        self.user=user
        self.password=password
        self.database=database
        self.trusted=trusted
        
    def connectdb_invoke_callback_and_return_recordset(self,istrust,server, user, password, database, sql,callback):  
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
        
    def select(self,sql=None):
        if sql is None:
            return None
        def callback(cur):
            row=cur.fetchall()
            return row
        return self.connectdb_invoke_callback_and_return_recordset(self.trusted,self.server, self.user, self.password, self.database, sql,callback)
    
    def execute(self,sql=None):
        """
        用来操作insert,update
        """
        if sql is None:
            return None
        def callback(cur):
            return cur.rowcount
        return self.connectdb_invoke_callback_and_return_recordset(self.trusted,self.server, self.user, self.password, self.database, sql,callback)

if __name__=="__main__":
    db=SqlServer("10.3.10.90","abc","abc","DMDM")
    sql="select top 10 * from similarities;"
    rows=db.select(sql)
    print len(rows)
    sql="update similarities set p1='11' where p1='------------------'"
    print db.execute(sql)