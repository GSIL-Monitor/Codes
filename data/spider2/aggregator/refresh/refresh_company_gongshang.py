# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("refresh_company_gongshang", stream=True)
logger = loghelper.get_logger("refresh_company_gongshang")

def refresh_gongshang(companyId):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", companyId)
    corporate = conn.get("select * from corporate where id=%s", company["corporateId"])

    if corporate["fullName"] is not None and corporate["fullName"].strip() != "":
        mongo = db.connect_mongo()
        collection_name = mongo.info.gongshang_name
        # collection_name.update_one({"name": corporate["fullName"]}, {'$set': {"lastCheckTime": None}})
        name = corporate["fullName"]
        gname = collection_name.find_one({"name": name})
        if gname is None:
            collection_name.insert({"name": name, "type": 3, "lastCheckTime": None,
                                    "corporateIds": [int(corporate["id"])]})
        else:
            collection_name.update_one({"name": name}, {'$set': {"lastCheckTime": None}})
        mongo.close()
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

                if t["subStatus"].has_key("gongshang") is True:

                    logger.info("refresh company gongshang done: %s", t["companyId"])

                else:
                    logger.info("refresh company gongshang start: %s", t["companyId"])
                    refresh_gongshang(t["companyId"])
                    collection.update_one({"_id": t["_id"]}, {"$set": {"subStatus.gongshang": 1}})

            else:
                logger.info("refresh company gongshang start: %s", t["companyId"])
                refresh_gongshang(t["companyId"])
                collection.update_one({"_id": t["_id"]}, {"$set": {"subStatus.gongshang": 1}})

        conn.close()
        mongo.close()
        time.sleep(30)

