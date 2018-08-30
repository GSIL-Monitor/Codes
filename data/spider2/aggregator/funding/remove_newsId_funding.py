# -*- coding: utf-8 -*-
#删除无金额和投资人的记录
import os, sys
import time
from bson.objectid import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("remove_empty_funding", stream=True)
logger = loghelper.get_logger("remove_empty_funding")


if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    fs = conn.query("select * from funding where (active is null or active='Y') and newsId is not null order by id")
    num = 0
    right = 0
    false = 0
    notsure = 0
    notid = 0
    for f in fs:
        num += 1
        if len(f["newsId"]) != 24:
            logger.info("FundingId:%s, news_id:%s, createUser:%s", f["id"], f["newsId"], f["createUser"])
            notid += 1
            conn.update("update funding set newsId=null where id=%s", f["id"])
            continue
        collection_news = mongo.article.news
        collection_funding = mongo.raw.funding
        item = collection_news.find_one({"_id": ObjectId(str(f["newsId"]))})
        if item is not None:
            right += 1
            continue
        item2 = collection_funding.find_one({"_id": ObjectId(str(f["newsId"]))})
        if item2 is not None:
            false += 1
            logger.info("raw funding id:%s", item2["_id"])
            if len(item2["news_id"]) > 0:
                news_id = item2["news_id"][0]
                conn.update("update funding set newsId=%s where id=%s", news_id, f["id"])
            else:
                conn.update("update funding set newsId=null where id=%s", f["id"])
            continue

        notsure += 1


    mongo.close()
    conn.close()
    logger.info("num: %s/%s/%s/%s/%s", num, right, false, notsure, notid)
    logger.info("End.")