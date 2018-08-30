# -*- coding: utf-8 -*-
import sys, os, time, datetime
import json
import requests

import urllib, urllib2

param = {
    "userid": 'HZ91i1a',
}
userid = 'HZ91i1a'
userkey = 'nbgHUmTH'
import hmac
import hashlib

param = sorted(param.items(), key=lambda d: d[0])
paramStr = ''
for i in param:
    paramStr += i[0] + str(i[1])

print paramStr

token = hmac.new(userkey, paramStr + userid, hashlib.sha1).hexdigest()

print token
header = {
    'Authorization': token,
}

res = requests.post('http://open.elecredit.com/getentid/', data=param, headers=header)
print  res.text
# data = urllib.urlencode(data)
# print data
# req = urllib2.Request('http://open.elecredit.com/getentid/', data)
#   #enable cookie
# opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
# response = opener.open(req)
# print response.read()

#
# param ={
#     "userid": "HZ91i1a",
#     "entid": "VST3wFB3Ye",
#     "version": "A1"
# }
# param = sorted(param.items(), key=lambda d: d[0])
# paramStr = ''
# for i in param:
#     paramStr += i[0] + str(i[1])
#
# print paramStr
#
# token = hmac.new(userkey, paramStr + userid, hashlib.sha1).hexdigest()
# data = {
#     'Authorization': token
# }
# res = requests.post('http://open.elecredit.com/elsaic/', data=data)
# print  res.text