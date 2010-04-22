#!/usr/bin/env python
#-*- coding:gb2312 -*-
import ictclas
print ictclas.ict_init("./")
s = "我们都是好孩子，异想天开的孩子。written by 爱思客"
count = ictclas.process_str_ret_word_count(s)
print "Count:%s"%(count)
li = ictclas.process_str_ret_list(s)
print "-"*8
for i in li:
	print i.start, i.length, i.ipos, i.spos, i.word_id, i.word_type, i.weight, s[i.start:(i.start+i.length)]
print "-"*8
kw = ictclas.keyword(len(li))
for i in kw:
	print i.start, i.length, i.ipos, i.spos, i.word_id, i.word_type, i.weight, s[i.start:(i.start+i.length)]

print "-"*8
print "set pos map:%s"%(ictclas.POSMAP.ICT_SECOND)
print "after add user word"
ictclas.add_user_word("爱思客	n")
ictclas.set_pos_map(ictclas.POSMAP.ICT_SECOND)
li = ictclas.process_str_ret_list(s)
fingerprint = ictclas.fingerprint()
print "fingerprint:%s"%(fingerprint)
kw = ictclas.keyword(len(li))
for i in kw:
	print i.start, i.length, i.ipos, i.spos, i.word_id, i.word_type, i.weight, s[i.start:(i.start+i.length)]

print ictclas.ict_exit()

