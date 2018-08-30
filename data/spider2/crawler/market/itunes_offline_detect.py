# -*- coding: utf-8 -*-
import os, sys
import datetime
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
import pymongo
from distutils.version import LooseVersion
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, db, util, url_helper, name_helper

#logger
loghelper.init_logger("itunes_offline_detect", stream=True)
logger = loghelper.get_logger("itunes_offline_detect")

APPS = []


class DetectCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, timeout=30)

    def is_crawl_success(self,url, content):
        if content.find("北京七麦科技股份有限公司") > 0:
            return True
        return False


def process(item, content):
    #logger.info(content)
    offline = None
    if content.find("<title>「」的实时排名 - ASO100</title>") >= 0:
        #应用不存在
        pass
    else:
        if content.find("[已下架]") >= 0:
            offline = True
        else:
            offline = False

    mongo = db.connect_mongo()
    if offline != item.get("offline"):
        logger.info("trackId: %s", item["trackId"])
        today = datetime.datetime.now()
        mongo.market.itunes.update_one({"_id":item["_id"]},
                                   {"$set":{"offline":offline, "offlineDetectTime":today}})
        if item.get("offline") is not None:
            record = {"offlineDetectTime": today, "offline": offline}
            mongo.market.itunes.update_one({"_id":item["_id"]},
                                {'$addToSet':{"offline_histories":record}})
        # if offline:
        #     exit()
    mongo.close()

def run():
    crawler = DetectCrawler()
    while True:
        if len(APPS) == 0:
            exit()
            return

        item = APPS.pop(0)
        #logger.info(item["trackName"])

        url = "http://aso100.com/app/rank/appid/%s/country/cn" % item["trackId"]

        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                process(item, result['content'])
                break

def start_run(concurrent_num):
    while True:
        logger.info("Itunes offline detect start...")
        d = datetime.datetime.now() - datetime.timedelta(1)
        mongo = db.connect_mongo()
        apps = list(mongo.market.itunes.find(
            {"$or":[{"offlineDetectTime": {"$lt": d}}, {"offlineDetectTime": {"$exists": False}}]},
            projection={'histories': False},
            #sort=[("_id",pymongo.DESCENDING)],
            limit=1000))
        mongo.close()
        for app in apps:
            APPS.append(app)
        threads = [gevent.spawn(run) for i in xrange(concurrent_num)]
        gevent.joinall(threads)


        logger.info("end.")

        if len(apps) == 0:
            gevent.sleep(5*60)


if __name__ == "__main__":
    start_run(20)