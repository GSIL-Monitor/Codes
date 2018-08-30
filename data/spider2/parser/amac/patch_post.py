# -*- coding: utf-8 -*-
import os, sys, datetime
from lxml import html
from pyquery import PyQuery as pq
import urllib
import time
import json

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db,util,url_helper, desc_helper

#logger
loghelper.init_logger("crawler_geekpark_news", stream=True)
logger = loghelper.get_logger("crawler_geekpark_news")

#mongo

mongo = db.connect_mongo()
collection = mongo.amac.fund

if __name__ == "__main__":

    ress = list(collection.find({}))
    cnt=0
    aa =0
    for res in ress:
        if res.has_key("lastUpdateDate") is False or res["lastUpdateDate"] is None:
            collection.update_one({"_id": res["_id"]}, {"$set": {"lastUpdateDate": res["lastUdpateDate"]}})
            cnt += 1

        # brief = util.get_brief_from_news(res["contents"])
        #
        # logger.info("%s, %s, %s, %s", res["title"], res["source"], res["date"], brief)
        # collection_news.update_one({"_id": res["_id"]}, {"$set": {"brief": brief}})
        aa += 1


    logger.info(cnt)
    logger.info(aa)
        #exit()
