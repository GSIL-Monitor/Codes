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
import loghelper,extract,db,util,url_helper, desc_helper, simhash

#logger
loghelper.init_logger("activity_simhash", stream=True)
logger = loghelper.get_logger("activity_simhash")

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

def get_simhash_value(contents):
    main =""
    for content in contents:
        if content["content"].strip() != "":
            main = main + content["content"]
    a = simhash.Simhash(simhash.get_features(main))
    logger.info("*****%s", a.value)
    return str(a.value)

def check_same_act(act):
    v = long(act["simhashValue"])
    acts1 = list(collection_news.find({"type": 60002, "beginDate": act["beginDate"], "endDate": act["endDate"], "city": act["city"]}))
    for act1 in acts1:
        if act1.has_key("simhashValue") is False or act["simhashValue"] is None:
            continue
        logger.info("same title: %s", act["title"])
        v1 = long(act1["simhashValue"])
        dis = simhash.Simhash(v).distance(simhash.Simhash(v1))
        if dis < 6:
            logger.info("Same act!!! %s, %s, %s, %s, %s", dis, act["title"], act1["title"], act["link"], act1["link"])
            return True
    return False


if __name__ == "__main__":
    acts = list(collection_news.find({"type":60002, "title":"微链投递“直通车”，助力高效融资！（9月份超值福利）"}))
    aa = 0
    for act in acts:
        if act.has_key("simhashValue") is False or act["simhashValue"] is None:
            contents = get_contents(act["_id"])
            #logger.info(contents)
            if contents is not None:
                a = simhash.Simhash(simhash.get_features(contents))
                logger.info("*****%s, value: %s", act["title"], a.value)
                v = a.value
                collection_news.update_one({"_id": act["_id"]}, {"$set": {"simhashValue": str(a.value)}})
            else:
                logger.info("No content for title: %s", act["title"])
                continue
        else:
            #continue
            v = long(act["simhashValue"])
            acts1 = list(collection_news.find({"type": 60002, "beginDate": act["beginDate"], "endDate": act["endDate"], "city": act["city"]}))
            for act1 in acts1:
                # logger.info(len(acts1))
                if act1["_id"] == act["_id"] or act1.has_key("simhashValue") is False or act["simhashValue"] is None:
                    continue
                if act1["beginDate"] == act["beginDate"] and act1["endDate"] == act["endDate"]:
                    v1 = long(act1["simhashValue"])

                    dis = simhash.Simhash(v).distance(simhash.Simhash(v1))
                    #logger.info(dis)
                    if dis < 60:
                        logger.info("%s, %s, %s, %s, %s, %s, %s", dis, act["title"], act1["title"], act["link"], act1["link"], act["_id"], act1["_id"])
                        #collection_news.delete_one({"_id": act["_id"]})
                        aa += 1
    logger.info(aa)


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
