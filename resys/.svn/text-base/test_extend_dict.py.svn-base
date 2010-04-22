#! usr/bin/env python
#encoding=utf8

class myDict(dict):
     
     def __init__(self):
          dict.__init__(self)
          self.db={}
          
     def __setitem__(self,key,val):
          self.db[key]=val
     
     def __getitem__(self,key):
          if self.db.has_key(key):
               return self.db[key]
               
my_dict = myDict()
my_dict['test'] = 'test'
print my_dict
print my_dict.db