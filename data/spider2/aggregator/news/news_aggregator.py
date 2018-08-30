# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import traceback
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../nlp/score'))
import loghelper,url_helper
import config, db
from relatedness import RelatednessScorer
rs = RelatednessScorer()

#logger
loghelper.init_logger("news_aggregator", stream=True)
logger = loghelper.get_logger("news_aggregator")

#mongo
mongo_local = db.connect_mongo_local()
collection = mongo_local.raw.news

mongo = db.connect_mongo()
dest = mongo.article.news

def merge_news(news):
    if news is None:
        return False

    try:
        contents = news["parsed_contents"]
        title =  news["title"]
        name = news['search_name']
        companyId = news['company_id']
        url = news["url"]
        flag, domain = url_helper.get_domain(url)
        logger.info("companyId=%s, name=%s", companyId, name)
        logger.info("url: %s, title: %s", url, title)

        content = ""
        for c in contents:
            if c["type"] == "text":
                content += c["data"]
        #logger.info(content)
        if len(content) < 20:
            flag = False
            confidence = 0
        else:
            flag, confidence = rs.compare(companyId, name=name, title=title, content=content, link=url)
            #logger.info("flag=%s",flag)
        logger.info("flag: %s, confidence: %s", flag, confidence)
        #logger.info(type(flag))

        if flag:
            item = dest.find_one({"companyId":companyId, "title":news["title"]})
            if item is None:
                dnews = {
                    "companyId":companyId,
                    "date":datetime.datetime.fromtimestamp(news["publish_time"]-8*3600),
                    "title":news["title"],
                    "link":news["url"],
                    "domain":domain,
                    "createTime":news["create_time"]
                }

                dcontents = []
                rank = 1
                for c in contents:
                    if c["type"] == "text":
                        dc = {
                                "rank":rank,
                                "content":c["data"],
                                "image":"",
                                "image_src":"",
                            }
                    else:
                        dc = {
                                "rank":rank,
                                "content":"",
                                "image":"",
                                "image_src":c["data"],
                            }
                    dcontents.append(dc)
                    rank += 1
                dnews["contents"] = dcontents
                dest.insert(dnews)
        data = {"aggregated":True, "compare_flag":flag, "compare_confidence":confidence}
        #logger.info(data)
        collection.update({"_id":news["_id"]},{"$set":data})
    except:
        traceback.print_exc()
        return False

    return flag

if __name__ == '__main__':
    while True:
        logger.info("Begin...")
        #items = list(collection.find({"parsed":True, "aggregated":{"$ne":True}}).sort("_id", pymongo.DESCENDING))
        items = list(collection.find({"parsed":True, "aggregated":{"$ne":True}}).limit(100))
        for item in items:
            flag = merge_news(item)
            #if flag:
            #    break
            #break
        logger.info("End.")
        #break
        if len(items) == 0:
            time.sleep(60)
