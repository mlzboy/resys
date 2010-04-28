#! usr/bin/env python
#encoding=utf8
from phprpc import PHPRPC_Client
client = PHPRPC_Client('http://127.0.0.1/')
#clientProxy = client.useService()
#print client.add(1, 2) # 将显示3
#print clientProxy.add(1, 2) # 另一种呼叫方法
print client.hi("xiaomao")
print client.recommend('a',9,'b')