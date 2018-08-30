# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
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
if __name__ == "__main__":
    while True:
        logger.info("start...")
        mongo = db.connect_mongo()
        news_list = list(mongo.article.news.find({"media_tag_processed": {"$ne": True}}, limit=1000))
        mongo.close()
        for news in news_list:
            if news.get("source") is not None and news.get("companyId") is not None:
                domain = news.get("domain")
                if domain is not None:
                    domain = domain.strip()
                    if domain in DOMAINS:
                        company_id = news.get("companyId")
                        tag_id = 479290
                        conn = db.connect_torndb()
                        rel = conn.get("select * from company_tag_rel where companyId=%s and tagId=%s limit 1",
                               company_id, tag_id)
                        if rel is None:
                            logger.info("companyId:%s, tagId:%s", company_id, tag_id)
                            conn.insert("insert company_tag_rel(companyId,tagId,verify,createTime,confidence) "
                                        "values(%s,%s,'Y',now(),0.5)",
                                        company_id, tag_id)
                            # exit()
                        conn.close()
            mongo = db.connect_mongo()
            mongo.article.news.update({"_id":news["_id"]},{"$set":{"media_tag_processed":True}})
            mongo.close()

        if len(news_list) == 0:
            logger.info("End.")
            time.sleep(60)