# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
from pymongo import MongoClient
import pymongo
import datetime, time


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import config
import util

#logger
loghelper.init_logger("baidu_parser", stream=True)
logger = loghelper.get_logger("baidu_parser")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)

baidu_collection = mongo.crawler_v2.market_baidu
other_collection = mongo.crawler_v2.market_other

if __name__ == "__main__":
    logger.info("Start...")

    apps = baidu_collection.find({"parsed":{"$ne":True}})
    #apps = baidu_collection.find({})
    for app in apps:
        if app.get("html_parsed") is not None:
            if app.get("parsed") is None:
                baidu_collection.update_one({"_id":app["_id"]},{'$set':{'parsed':True}})
                #break
            continue

        content = app.get("content")
        if content is None:
            continue
        logger.info(app["url"])

        d = pq(content)
        cate = d('div.nav> span >a').eq(0).text()
        data = d('div.area-download> a')
        type = data.attr("data_type")
        detail_type = data.attr("data_detail_type")
        name = data.attr("data_name")
        package = data.attr("data_package").strip()
        versionname = data.attr("data_versionname")
        icon = data.attr("data_icon")
        size = data.attr("data_size")
        logger.info("%s, %s, %s, %s, %s" % (cate, type, detail_type, name, package))

        # screenshot
        screenshots = []
        imgs = d('img.imagefix')
        #logger.info(imgs)
        for img in imgs:
            url = pq(img).attr("src")
            #logger.info(url)
            screenshots.append(url)

        # content
        desc = d('p.content').text()
        #logger.info(desc)

        html_parsed = {
            "cate": cate,
            "type": type,
            "detail_type": detail_type,
            "name": name,
            "package": package,
            "versionname": versionname,
            "icon": icon,
            "size": size,
            "screenshots": screenshots,
            "desc":desc
        }

        baidu_collection.update_one({"_id":app["_id"]},{'$set':{'html_parsed':html_parsed, 'parsed':True}})
        if other_collection.find_one({"package":package}) is None:
            other_collection.insert_one({"package":package})

        # break