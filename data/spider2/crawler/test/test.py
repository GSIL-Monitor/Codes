# -*- coding: utf-8 -*-
import urllib2


url = "https://itunes.apple.com/cn/lookup?id=1054909549"
ua_header = {"User-Agent":"Mozzila/5.0(compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;"}
request = urllib2.Request(url,headers=ua_header)
response = urllib2.urlopen(request)
html = response.read()
print html