# -*- coding: utf-8 -*-
import os, sys
import time
from pymongo import MongoClient
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import db
import loghelper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))

#logger
loghelper.init_logger("news_migrate", stream=True)
logger = loghelper.get_logger("news_migrate")

#mongo
mongo = db.connect_mongo()
collection = mongo.article.news

#mysql
conn = None

def migrate():
    conn = db.connect_torndb_crawler()
    for i in range(1,101):
        table_name = "news%s" % i
        logger.info(table_name)
        all_news = conn.query("select * from " + table_name + " where migrate=0 order by id")

        for news in all_news:
            logger.info(news["title"])
            oldNewsId = "%s_%s" % (table_name, news["id"])
            news1 = collection.find_one({"oldNewsId":oldNewsId})
            if news1 is None:
                news1 = {
                    "companyId":news["companyId"],
                    "date":news["date"],
                    "title":news["title"],
                    "link":news["link"],
                    "confidence":news["confidence"],
                    "verify":news["verify"],
                    "active":news['active'],
                    "createTime":news["createTime"],
                    "oldNewsId": oldNewsId
                }
                content_table_name = "news_content%s" % i
                contents = conn.query("select * from " + content_table_name + " where newsId=%s order by id", news["id"])
                contents1 = []
                for content in contents:
                    #logger.info(content["content"])
                    content = {
                        "rank":content["rank"],
                        "content":content["content"],
                        "image":content["image"]
                    }
                    contents1.append(content)
                news1["contents"] = contents1
                #logger.info(news1)
                collection.insert(news1)

                #break

            conn.execute("update " + table_name + " set migrate=1 where id=%s", news["id"])
        #break
    conn.close()

if __name__ == "__main__":
    while True:
        migrate()
        time.sleep(60)