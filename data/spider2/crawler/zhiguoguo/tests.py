# -*- coding: utf8 -*-
# Create your tests here.
import requests
import urllib
import pprint
import json
import sys,os

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db,util,url_helper,download, desc_helper

company = '上海汇翼信息科技有限公司'
# company = '柳州欧维姆机械股份'
cc = urllib.quote(company)
print cc

APPKEY = "9ebf51b8e23b419c371e5ebf58d49c71"
SECKEY = "c63970b3666de504d406f92875d31a4e"

urlToken = "http://211.154.163.148:51000/DataPlatformService/GetToken?appkey=%s&seckey=%s&type=JSON" % (APPKEY, SECKEY)

token = None
r = requests.get(urlToken)

print r.text

if r.status_code == 200:
    try:
        content = json.loads(r.text)
        if content.has_key("result"):
            token = content["result"]["token"]
    except Exception, e:
        print e

print token

urlIcon = "http://211.154.163.148:51000/DataPlatformService/GetTradeMark?token=%s&pageSize=10&currentPage=0&keyWord=%s" \
          % (token, cc)
print urlIcon

r1 = requests.get(urlIcon)

print (json.dumps(json.loads(r1.text), ensure_ascii=False, cls=util.CJsonEncoder))

print "\n\n\n"

urlCopy = "http://211.154.163.148:51000/DataPlatformService/GetCopyRight?token=%s&pageSize=10&currentPage=0&keyWord=%s" \
          % (token, cc)
# urlCopy = "http://211.154.163.148:51000/DataPlatformService/GetCopyRight?keyWord=柳州欧维姆机械股份"
print urlCopy
r2 = requests.get(urlCopy)

print r2.text