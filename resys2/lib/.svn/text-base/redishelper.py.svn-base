#! usr/bin/env python
#encoding=utf8
def make_list(rx, key, list):
    """
    作用：向redis中批量储存set类型的数据
    rx是连接的数据库rx=redis.Redis()
    key是要储存的数据库
    list是要储存的值的list集合
    """
    for elem in list:
        rx.rpush(key, elem)