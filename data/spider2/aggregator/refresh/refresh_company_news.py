# -*- coding: utf-8 -*-
import os, sys, datetime
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/news'))
import baidu_news



#logger
loghelper.init_logger("refresh_news", stream=True)
logger = loghelper.get_logger("refresh_news")

def refresh_news(companyId):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", companyId)
    # corporate = conn.get("select * from corporate where id=%s", company["corporateId"])

    if company["name"] is not None and company["name"].strip() != "":
        baidu_news.start_run("incr", [{"column": "foucs", "max": 2}], company["name"], companyId)
    conn.close()
    pass


if __name__ == '__main__':

    logger.info("python refresh_news")
    while True:
        conn = db.connect_torndb()
        mongo = db.connect_mongo()
        collection_raw = mongo.raw.projectdata
        collection = mongo.task.company_refresh

        tasks = list(collection.find({"status":0, "extendType":0}))
        for t in tasks:
            if t.has_key("subStatus") is True:

                if t["subStatus"].has_key("news") is True:

                    logger.info("refresh company news done: %s", t["companyId"])

                else:
                    logger.info("refresh company news start: %s", t["companyId"])
                    refresh_news(t["companyId"])
                    collection.update_one({"_id": t["_id"]}, {"$set": {"subStatus.news": 1}})

            else:
                logger.info("refresh company news start: %s", t["companyId"])
                refresh_news(t["companyId"])
                collection.update_one({"_id": t["_id"]}, {"$set": {"subStatus.news": 1}})

        tasks2 = list(collection.find({"status": 0, "extendType": 2}))
        for t in tasks2:
            logger.info("refresh company news start: %s", t["companyId"])
            refresh_news(t["companyId"])
            collection.update_one({"_id": t["_id"]}, {"$set": {"status": 1,
                                                               "finishTime": datetime.datetime.now() - datetime.timedelta(
                                                                   hours=8)}})

        conn.close()
        mongo.close()
        time.sleep(30)

