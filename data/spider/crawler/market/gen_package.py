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
loghelper.init_logger("gen_package", stream=True)
logger = loghelper.get_logger("gen_package")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)

baidu_collection = mongo.crawler_v2.market_baidu
m360_collection = mongo.crawler_v2.market_360
other_collection = mongo.crawler_v2.market_other

def gen(app):
    if app.get("html_parsed") is None:
        return
    package = app.get("html_parsed")["package"].strip()
    if other_collection.find_one({"package":package}) is None:
        other_collection.insert_one({"package":package})
        logger.info(package)

if __name__ == "__main__":
    logger.info("Start...")

    apps = baidu_collection.find({})
    for app in apps:
        gen(app)
        #break

    apps = m360_collection.find({})
    for app in apps:
        gen(app)
        #break
