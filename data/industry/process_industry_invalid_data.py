# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
import traceback
from bson import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, config, db

#logger
loghelper.init_logger("industry_statistic", stream=True)
logger = loghelper.get_logger("industry_statistic")

conn = None
mongo = None


def check_invalid_company():
    logger.info("Start delete invalid industry_company...")
    mid = -1
    while True:
        ms = conn.query("select * from industry_company where id>%s order by id limit 1000", mid)
        if len(ms) == 0:
            conn.close()
            break
        for m in ms:
            mid = m["id"]
            if m["active"] == 'N':
                continue
            company = conn.get("select * from company where id=%s", m["companyId"])
            if company is None or (company["active"] != "Y" and company["active"] is not None):
                logger.info("invalid industryCompanyId: %s", mid)
                conn.update("update industry_company set active='N' where id=%s", mid)
                # exit(0)
    logger.info("End delete invalid industry_company.")


def check_invalid_news():
    logger.info("Start delete invalid industry_news...")
    mid = -1
    while True:
        ms = conn.query("select * from industry_news where id>%s order by id limit 1000", mid)
        if len(ms) == 0:
            conn.close()
            break
        for m in ms:
            mid = m["id"]
            if m["active"] == 'N':
                continue
            news = mongo.article.news.find_one({"_id": ObjectId(m["newsId"])})
            companyIds = news.get("companyIds")
            flag = industry_contain_companies_check(m["industryId"], companyIds)
            if flag is False:
                logger.info("invalid industryNewsId: %s", mid)
                conn.update("update industry_news set active='N' where id=%s", mid)
                # exit(0)
    logger.info("End delete invalid industry_news.")


def industry_contain_companies_check(industryId, companyIds):
    if companyIds is None:
        return False
    for companyId in companyIds:
        company = conn.get("select id from industry_company where "
                           "industryId=%s and "
                           "active!='N' and "
                           "companyId=%s limit 1",
                           industryId, companyId)
        if company is not None:
            return True

    return False


def main():
    logger.info("Start...")
    global conn
    global mongo
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()

    check_invalid_company()
    check_invalid_news()

    conn.close()
    mongo.close()
    logger.info("End.")


if __name__ == '__main__':
    while True:
        main()
        time.sleep(60*60)