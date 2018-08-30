# -*- coding: utf-8 -*-
import os, sys, datetime
from lxml import html
from pyquery import PyQuery as pq
import urllib
import time
import json

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db,util,url_helper, desc_helper

#logger
loghelper.init_logger("crawler_geekpark_news", stream=True)
logger = loghelper.get_logger("crawler_geekpark_news")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

def get_contents(id):
    ress = collection_news.find_one({"_id": id})
    if ress is not None:
        contents = ""
        for content in ress['contents']:
            if content["content"].strip() != "":
                contents = contents + content["content"]
        return contents
    else:
        return None

if __name__ == "__main__":
    #acts = list(collection_news.find({"type":{"$in":[60001,60002, 60003]}}))
    acts = list(collection_news.find({"source":{"$in":[13809,13810]}, "date": {"$gt":datetime.datetime.strptime("2016-08-27","%Y-%m-%d")}}))
    update = False
    for act in acts:
        logger.info("title %s", act["title"])
        logger.info("title: %s, date: %s, type: %s", act["title"], act["date"], act["type"])
        update =True
        if update:
            date = act["date"] - datetime.timedelta(hours=8)
            collection_news.update_one({"_id": act["_id"]}, {"$set": {"date": date}})
            if act["type"] == 60002 :
                beginDate = act["beginDate"] - datetime.timedelta(hours=8)
                endDate = act["endDate"] - datetime.timedelta(hours=8)
                collection_news.update_one({"_id": act["_id"]}, {"$set": {"beginDate": beginDate, "endDate": endDate}})
        #exit()






    # title = "技术分享沙龙 | 知云善用，让移动研发更快速简单"
    # contents = get_contents(title)
    # logger.info(contents)
    # a = simhash.Simhash(simhash.get_features(contents))
    # logger.info(a.value)
    # title = "线下技术分享 | 知云善用，让移动研发更快速简单"
    # contents = get_contents(title)
    # logger.info(contents)
    # b = simhash.Simhash(simhash.get_features(contents))
    # logger.info(b.value)
    # logger.info(a.distance(b))

        #exit()
