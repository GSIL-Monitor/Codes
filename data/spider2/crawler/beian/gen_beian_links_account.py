# -*- coding: utf-8 -*-
import os, sys
import datetime
import random
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import urllib, urllib2
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, config, util

#logger
loghelper.init_logger("gen_beian_links_account", stream=True)
logger = loghelper.get_logger("gen_beian_links_account")



if __name__ == "__main__":
    for i in range(204,210):
        opener = urllib2.build_opener()
        username = "ann%s" % i
        data = {
            "username":username,
            "password": "ann123456",
            "confirmpassword": "ann123456",
            "opaction":"reg",
            "qq":"",
            "isqqopen":"1",
            "email":"%s@mailinator.com" % username
        }

        data = urllib.urlencode(data)
        logger.info(data)
        headers = {
            "Referer": "http://my.links.cn/reg.asp"
        }
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
        headers['User-Agent'] = user_agent

        try:
            request= urllib2.Request("http://my.links.cn/regpost.asp", data, headers)
            r = opener.open(request, timeout=60)
            try:
                content = util.html_encode(r.read())
                #logger.info(content)
            except Exception,e:
                traceback.print_exc()
        except Exception,e:
            traceback.print_exc()

