# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
import traceback
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import config
import db
import extract

#logger
loghelper.init_logger("toutiao_news_parser", stream=True)
logger = loghelper.get_logger("toutiao_news_parser")

#mongo
mongo = db.connect_mongo_local()
collection = mongo.raw.news


SOURCE = 'toutiao'

def parse_news(news):
    if news == None:
        return

    try:
        html = news["content"]
        summary = news["summary"]
        title= news["title"]
        url = news["share_url"]
        logger.info(title)
        logger.info(url)

        contents = extract.extractContents(url, html)
        #for c in contents:
        #    logger.info(c["data"])
        collection.update({"_id":news["_id"]},{"$set":{"parsed":True, "parsed_contents":contents}})
    except:
        traceback.print_exc()




if __name__ == '__main__':
    while True:
        logger.info("Begin...")
        items = list(collection.find({"source":SOURCE, "parsed":{"$ne":True}}).limit(100))
        for item in items:
            parse_news(item)
            #break
        logger.info("End.")
        #break
        if len(items) == 0:
            time.sleep(60)
