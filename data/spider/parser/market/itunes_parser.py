# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
from pymongo import MongoClient
import pymongo
import datetime, time
import re
import pytz

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import config
import util
import proxy_pool

#logger
loghelper.init_logger("itunes_parser", stream=True)
logger = loghelper.get_logger("itunes_parser")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)

itunes_collection = mongo.crawler_v2.market_itunes

if __name__ == "__main__":
    logger.info("Start...")
    rexExp = re.compile(r"[一-龥]+")
    apps = itunes_collection.find({"name":rexExp, "parsed":{"$ne":True}})
    logger.info("cnt: %s" % apps.count())
    for app in apps:
        html = app.get("html")
        if html is None:
            continue
        logger.info(app["url"])

        if app.get("html_parsed") is not None:
            if app.get("parsed") is None:
                itunes_collection.update_one({"_id":app["_id"]},{'$set':{'parsed':True}})
                #break
            continue

        urls  = []
        d = pq(html)
        links = d('div.app-links').find('a.see-all')
        for i in links:
            l = pq(i).attr('href')
            urls.append(l)
        logger.info(urls)
        str = d('span')("[itemprop='datePublished']").text()
        if str is None or str == "":
            datePublished = None
        else:
            datePublished = datetime.datetime.strptime(str,"%Y年%m月%d日")
        logger.info(datePublished)
        html_parsed = {
            "datePublished":datePublished,
            "urls":urls
        }

        itunes_collection.update_one({"_id":app["_id"]},{'$set':{'html_parsed':html_parsed, 'parsed':True}})
        # break