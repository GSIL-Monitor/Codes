# -*- coding: utf-8 -*-
import os, sys
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config
import db

#logger
loghelper.init_logger("domain_2_beian", stream=True)
logger = loghelper.get_logger("domain_2_beian")

#mongo
mongo = db.connect_mongo()
collection = mongo.trend.android

if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    conn_crawler = db.connect_torndb_crawler()
    for i in range(1,101):
    #for i in range(95,101):
        logger.info("android" + str(i))
        start = 0
        #sql = "select * from android" + str(i) + " where date>date_sub(now(),interval 30 day) order by id limit %s, 10000"
        sql = "select * from android" + str(i) + " order by id limit %s, 10000"
        while True:
            items = conn_crawler.query(sql, start)
            if len(items) == 0:
                break
            for item in items:
                artifactId = item["artifactId"]
                artifact = conn.get("select * from artifact where id=%s", artifactId)
                if artifact is None:
                    logger.info("artifactId=%s not Found!", artifactId)
                    continue
                apkname = artifact["domain"]
                if apkname is None or apkname.strip() == "":
                    logger.info("artifactId=%s no apkname!", artifactId)
                    continue
                apkname = apkname.strip().lower()
                #logger.info("%s %s %s", apkname, item["type"], item["date"])
                trend = collection.find_one({"appmarket":item["type"], "apkname":apkname, "date":item["date"]})
                if trend is None:
                    item.pop("id")
                    item.pop("companyId")
                    item.pop("artifactId")
                    appmarket = item.pop("type")
                    item["appmarket"] = appmarket
                    item["apkname"] = apkname
                    collection.insert(item)

                #exit()
            start += 10000

    conn_crawler.close()
    conn.close()

    logger.info("End.")