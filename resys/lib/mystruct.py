#! usr/bin/env python
#encoding=utf8
"""
brief:
this scipt help you build a sorted dict,it is implement by list
暂且搁置，有空来实现
"""
class mystruct():
    "hybird with dict & list"
    def __init__(self):
        self.list=[]
        
    def add(self,key,value):
        self.list.append((key,[value]))
        
    def has_key(self,key):
        for elem in self.list:
            if key==elem[0]:
                return True
        return False
    
    def update(self,key,value):
        for elem in self.list:
            if key==elem[0]:
                elem[1].append(value)
                return True
        return False
    
    def getlist(self):
        return self.list
    
    def getvalues(self):
        return [elem[1] for elem in self.list]

if __name__=='__main__':
    my=mystruct()
    my.add("aa",(1,2,3))
    my.add('bb',(2,3,4))
    if my.has_key("aa"):
        my.update("aa",(4,5,6))
    else:
        my.add("aaa",(1,2,3))
    list=my.getlist()
    for elem in list:
        print elem
    for elem in my.getvalues():
        print elem
    
    
    
    
    