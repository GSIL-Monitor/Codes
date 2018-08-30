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

if __name__ == "__main__":

    ress = list(collection_news.find({}))
    cnt=0
    aa =0
    for res in ress:
        # if res.has_key("companyIds") is True and isinstance(res["companyIds"], list):
        #
        #     newcompanyIds = [int(companyId) for companyId in res["companyIds"] if str(companyId) != ""]
        #
        #     if newcompanyIds != res["companyIds"]:
        #         logger.info("WRONG: %s|%s", res["_id"],res["companyIds"])
        #         collection_news.update_one({"_id": res["_id"]}, {"$set": {"companyIds": newcompanyIds}})
        #         cnt += 1

        if res.has_key("companyId") is True and res["companyId"] is not None and str(res["companyId"]) != "":
            if res.has_key("companyIds") is True and isinstance(res["companyIds"], list):
                if res["companyId"] not in res["companyIds"] and int(res["companyId"])>100:
                    logger.info("here missing  %s :%s in %s",res["_id"],res["companyId"], res["companyIds"])
                    cnt += 1
                    newcompanyIds = res["companyIds"]
                    newcompanyIds.append(int(res["companyId"]))
                    collection_news.update_one({"_id": res["_id"]}, {"$set": {"companyIds": newcompanyIds}})

            else:
                logger.info("here missing two: %s :%s",res["_id"],res["companyId"])
                cnt += 1
                collection_news.update_one({"_id": res["_id"]}, {"$set": {"companyIds": [int(res["companyId"])]}})
            # if newcompanyIds != res["companyIds"]:
            #     logger.info("WRONG: %s|%s", res["_id"], res["companyIds"])
            #     collection_news.update_one({"_id": res["_id"]}, {"$set": {"companyIds": newcompanyIds}})
            #     cnt += 1

        # brief = util.get_brief_from_news(res["contents"])
        #
        # logger.info("%s, %s, %s, %s", res["title"], res["source"], res["date"], brief)
        # collection_news.update_one({"_id": res["_id"]}, {"$set": {"brief": brief}})
        aa += 1


    logger.info(cnt)
    logger.info(aa)
        #exit()
