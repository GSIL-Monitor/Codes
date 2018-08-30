# -*- coding: utf-8 -*-
import os, sys
import datetime
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

#logger
loghelper.init_logger("patch_recommend", stream=True)
logger = loghelper.get_logger("patch_recommend")

if __name__ == "__main__":
    #清除错误的recommend website
    logger.info("Start...")
    start = 0
    while True:
        conn = db.connect_torndb()
        companies = list(conn.query("select * from company where (active is null or active='Y') "
                                    "order by id limit %s, 1000", start))
        if len(companies) == 0:
            break
        for company in companies:
            company_id = company["id"]
            recommend = conn.get("select * from artifact where companyId=%s and recommend='Y' "
                                 "and (active is null or active='Y') limit 1", company_id)
            if recommend and recommend["type"] == 4010:
                mongo = db.connect_mongo()
                website = mongo.info.website.find_one({"url":recommend["link"]})
                mongo.close()
                if website is None or website["httpcode"] != 200:
                    logger.info("code: %s , link: %s",company["code"], recommend["link"])
                    conn.update("update artifact set recommend=null where id=%s", recommend["id"])
                    #exit()
        start += 1000
        #exit()
        conn.close()
    logger.info("End.")