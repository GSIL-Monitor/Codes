# -*- coding: utf-8 -*-
import urllib,ssl
import urllib2
import json
import cookielib
from lxml import html
from pyquery import PyQuery as pq
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class RedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        pass

    def http_error_302(self, req, fp, code, msg, headers):
        pass


handlers = []
proxy_handler = urllib2.ProxyHandler({"http" : 'http://121.232.146.252:9000'})
proxy_handler1 = urllib2.ProxyHandler({"https": 'https://182.240.35.233:808'})
handlers.append(proxy_handler)
handlers.append(proxy_handler1)


handlers.append(urllib2.ProxyHandler({"http":"http://117.143.109.139:80"}))
cookie = cookielib.CookieJar()
handlerc=urllib2.HTTPCookieProcessor(cookie)
handlers.append(handlerc)

context = ssl._create_unverified_context()
handlers.append(urllib2.HTTPSHandler(0, context))

opener = urllib2.build_opener(*handlers)
url = "http://gs.amac.org.cn/amac-infodisc/res/pof/manager/1611210851101461.html"
req = urllib2.Request(url)   #send post
response = opener.open(req)
code = response.getcode()

content = response.read()
print code
print content
d = pq(html.fromstring(content.decode("utf-8")))

# infos = d('tbody#result_table> tr')
# for tr in infos:
#     item = {}
#     d2 = pq(tr)
#     #print d2
#     tds = d2('td')
#     print len(tds)
#     if len(tds) != 4:
#         continue
#     name = pq(tds[1]).text()
#
#     print name
#     #domain = f('a').eq(0).text().strip()
#     #print domain
#
# #print infos
