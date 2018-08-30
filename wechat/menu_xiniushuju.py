#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import urllib2,json

# 烯牛数据 - 订阅号
sAppID = "wx9aa7c074c4463a45"
sAppSecret = "e1fc76e6eae66587e0df8c3fc0ffe837"

reload(sys)
sys.setdefaultencoding( "utf-8" )

if __name__ == "__main__":
	url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (sAppID,sAppSecret)
	jsonStr = urllib2.urlopen(url).read()
	print jsonStr
	data = json.loads(jsonStr)
	access_token = data["access_token"]
	#print "access_token=%s" % access_token

	url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % access_token
	menuStr = """
{
	"button":[
	{
		"type":"miniprogram",
		"name":"机构用户",
		"url":"http://m.xiniudata.com",
       	"appid":"wx97ef209cc107ba45",
       	"pagepath":"pages/entry"
	},
	{
		"name":"个人用户",
		"sub_button":[
		{
			"type":"view",
			"name":"系统登录",
			"url":"http://m.xiniudata.com"
		},
		{
			"type":"miniprogram",
			"name":"创投播报",
			"url":"http://m.xiniudata.com",
	       	"appid":"wxfb8740586a0d4601",
	       	"pagepath":"pages/index/index"
		}
		]
	},
	{
		"name":"关于烯牛",
		"sub_button":[
		{
			"type":"view",
			"name":"铅笔道报道",
			"url":"http://www.pencilnews.cn/p/12465.html"
		},
		{
			"type":"view",
			"name":"36kr报道",
			"url":"http://36kr.com/p/5082200.html"
		},
		{
			"type":"view",
			"name":"猎云网报道",
			"url":"http://www.lieyunwang.com/archives/249383"
		},
		{
			"type":"view",
			"name":"下载App",
			"url":"https://itunes.apple.com/cn/app/id1246012153?mt=8"
		},
		{
			"type":"click",
			"name":"投资人交流",
			"key":"investor_communication"
		}
		]
	}
	]
}
	"""
	req = urllib2.Request(url, data=menuStr)
	resp = urllib2.urlopen(req)
	print resp.read()