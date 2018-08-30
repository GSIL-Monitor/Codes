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
loghelper.init_logger("news_domain", stream=True)
logger = loghelper.get_logger("news_domain")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

if __name__ == "__main__":

    results = list(collection_news.aggregate(
        [{"$group": {"_id": "$domain", "count": {"$sum": 1}}}, {"$match": {"count":{"$gt":100}}}]))
    for result in results:
        #logger.info("News source %s, total number: %s", result["_id"], result["count"])
        conn = db.connect_torndb()
        name = conn.get("select * from news_domain where domain=%s", result["_id"])
        conn.close()

        if name is None:
            logger.info("News source: %s, total number: %s", result["_id"], result["count"])
            pass
        else:
            # logger.info("News source %s, total number: %s", result["_id"], result["count"])
            pass
