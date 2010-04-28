#!usr/bin/env python
#encoding=utf8
a='hha'
class A():
    
    def __init__(self):
        a="bb"
        self.url="www"
        
    @staticmethod
    def test():
        print "bbas"
        print a
        
    print a
    
    
    def test2(cls):
        print a
    
    test2=classmethod(test2)
    
    def s(self,v):
        self.url=v
    
    def g(self):
        return self.url
    
    url=property(fget=g,fset=s)
    
    @property
    def hhh(self):
        return "aaaaaaaaaaaaaaaaaaaa"
    
    @property
    def hhh(self,v):
        self.url=v
        
if __name__=='__main__':
    A.test()
    A.test2()
    aaaa=A()
    print aaaa.url
    print aaaa.hhh
    aaaa.hhh="zzzzzzzzzzz"
    print aaaa.url