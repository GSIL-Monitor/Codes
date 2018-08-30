# -*- coding: utf-8 -*-
import os, sys
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config
import db
import name_helper

#logger
loghelper.init_logger("domain_2_beian", stream=True)
logger = loghelper.get_logger("domain_2_beian")

#mongo
mongo = db.connect_mongo()
collection = mongo.trend.itunes

if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    conn_crawler = db.connect_torndb_crawler()
    for i in range(1,101):
        logger.info("ios" + str(i))
        start = 0
        #sql = "select * from ios" + str(i) + " where date>date_sub(now(),interval 30 day) order by id limit %s, 10000"
        sql = "select * from ios" + str(i) + " order by id limit %s, 10000"
        while True:
            items = list(conn_crawler.query(sql, start))
            if len(items) == 0:
                break
            for item in items:
                artifactId = item["artifactId"]
                artifact = conn.get("select * from artifact where id=%s", artifactId)
                if artifact is None:
                    logger.info("artifactId=%s not Found!", artifactId)
                    continue
                trackId = artifact["domain"]
                if trackId is None or trackId.strip() == "":
                    logger.info("artifactId=%s no trackId!", artifactId)
                    continue
                trackId = int(trackId)
                #logger.info("trackId=%s", trackId)

                trend = collection.find_one({"trackId":trackId, "date":item["date"]})
                if trend is None:
                    item.pop("id")
                    item.pop("companyId")
                    item.pop("artifactId")
                    item["trackId"] = trackId
                    collection.insert(item)

                #break
            start += 10000

    conn_crawler.close()
    conn.close()

    logger.info("End.")