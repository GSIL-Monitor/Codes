# -*- coding: utf-8 -*-
__author__ = "arthur"

import os, sys
import time
from datetime import datetime

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, util, db, name_helper

#logger
loghelper.init_logger("set_endorse_media_tag", stream=True)
logger = loghelper.get_logger("set_endorse_media_tag")


DOMAINS = [
    "36kr.com",
    "pencilnews.cn",
    "tuoniao.fm",
    "lieyunwang.com",
    "cyzone.cn",
    "xfz.cn"
]


# modified by kailu, 2017-04-30
def insert_rel(conn, cid, tid):
    rel = conn.get("select * from company_tag_rel where companyId=%s and tagId=%s limit 1",
           cid, tid)
    if rel is None:
        logger.info("companyId:%s, tagId:%s", cid, tid)
        conn.insert("insert company_tag_rel(companyId,tagId,verify,createTime,confidence) "
                    "values(%s,%s,'Y',now(),0.5)",
                    cid, tid)


if __name__ == "__main__":
    while True:
        logger.info("start...")

        mongo = db.connect_mongo()
        news_list = list(mongo.article.news.find({"type": 60001,
                                                  "media_tag_processed": {"$ne": True}}, limit=1000))
        mongo.close()

        for news in news_list:

            mongo = db.connect_mongo()
            mongo.article.news.update({"_id": news["_id"]},
                                      {"$set": {"media_tag_processed":True}})
            mongo.close()

            news_id = news.get("_id")
            logger.info("Dealing news {}".format(news_id))

            news_source = news.get("source")
            if news_source is None:
                continue

            domain = news.get("domain")
            if domain is not None:
                domain.strip()
                if domain not in DOMAINS:
                    continue

            cid_source = news.get("companyId")
            cids_extended = news.get("companyIds")
            if cid_source is not None:
                cids_extended.append(cid_source)
            news_date = news.get("date")

            tag_id = 479290
            conn = db.connect_torndb()
            split_date = datetime(2017, 4, 1)
            if news_date is not None and news_date > split_date:
                cids = set([int(cid) for cid in cids_extended])
                for cid in cids:
                    insert_rel(conn, cid, tag_id)
                    logger.info("News_id {}, company {}".format(news_id, cid))
            elif cid_source is not None:
                insert_rel(conn, cid_source, tag_id)
                logger.info("News_id {}, company {}".format(news_id, cid))
            conn.close()

        if len(news_list) == 0:
            logger.info("End.")
            time.sleep(60)
