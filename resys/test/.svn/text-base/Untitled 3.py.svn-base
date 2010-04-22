#! /usr/bin/env python
#coding=utf-8
from pymmseg import mmseg
import chardet
#print chardet.detect(text)
 
#mmseg.dict_load_defaults()
import codecs
#f=codecs.open(r"F:\dm_app\tag2\exportdata\original\0000149.txt","r","utf-8")
f=open(r"F:\dm_app\tag2\exportdata\original\00000005.txt")
text=f.read()
if text[:3] == codecs.BOM_UTF8:  
    text= text[3:]  
    print "======"
    print text
    print chardet.detect(text)
    #print text.decode("utf8").encode("gb2312")
else:
    print text
    print chardet.detect(text)

from pymmseg import mmseg
 
mmseg.dict_load_defaults()
text="0002700,动感条纹短袖POLO衫 天蓝条纹,男装-POLO-短袖POLO,    VANCL2010年全新推出时尚、清新的动感条纹短袖POLO衫，采用100%全棉针织平纹布制成，面料透气吸汗，穿着柔软舒适，非常适合春夏季穿着。纯白色的大身上采用色彩绚丽的撞色细条纹装点前胸处，透露出一丝动感与清新的视觉感受。领子则使用不易松懈的横机领；门襟采用独特的"
algor = mmseg.Algorithm(text)
for tok in algor:
    print "--"
    print chardet.detect(tok.text)
    print '%s [%d..%d]' % (tok.text.decode("utf8").encode("gbk","ignore"), tok.start, tok.end)
