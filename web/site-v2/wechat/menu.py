#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import urllib2,json
sAppID = "wxa3ce89070799e1be"
sAppSecret = "4d7b395b28810f03b572fe61fc6d961d"

reload(sys)
sys.setdefaultencoding( "utf-8" )

if __name__ == "__main__": 
	url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (sAppID,sAppSecret)
	jsonStr = urllib2.urlopen(url).read()
	#print jsonStr
	data = json.loads(jsonStr)
	access_token = data["access_token"]
	print "access_token=%s" % access_token

	url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % access_token
	menuStr = """
		{
			"button":[
				{
					"type":"click",
					"name":"绑定账户",
					"key":"bind"
				},
				{
					"type":"view",
					"name":"如何收藏",
					"url":"http://wx1.gobivc.com/static/help.html"
				}
			]
		}
	"""
	req = urllib2.Request(url, data=menuStr)
	resp = urllib2.urlopen(req)
	print resp.read()