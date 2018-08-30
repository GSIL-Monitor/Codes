# -*- coding: utf-8 -*-
import os, sys
import datetime
from bson import ObjectId
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_funding_companyid", stream=True)
logger = loghelper.get_logger("patch_funding_companyid")

'''
select distinct corporateId from funding where (active is null or active='Y') and 
corporateId in ( select corporateId from (select corporateId, count(*) cnt from company where active is null or active='Y' group by corporateId having cnt>1) a);
'''

conn = db.connect_torndb()
mongo = db.connect_mongo()

def get_company_ids(corporate_id):
    company_ids = []
    items = conn.query("select id from company where corporateId=%s", corporate_id)
    for item in items:
        company_ids.append(item["id"])
    return company_ids


def guess_company_id(funding):
    items = conn.query("select id from company where (active is null or active='Y') and corporateId=%s order by id",
                       funding["corporateId"])
    if len(items) == 0:
        items = conn.query("select id from company where (active is null or active!='N') and corporateId=%s order by id",
                           funding["corporateId"])

    if len(items) == 0:
        items = conn.query("select id from company where corporateId=%s order by id",
                           funding["corporateId"])

    if len(items) == 1:
        return items[0]["id"]

    news_id = funding["newsId"]
    company_id = guess_by_news(news_id, items)
    if company_id is not None:
        return company_id

    logger.info("get the first one! fundingId=%s, corporateId=%s", funding["id"], funding["corporateId"])
    return items[0]["id"]


def guess_by_news(news_id,items):
    if news_id is None or news_id.strip()=="":
        return None
    news = mongo.article.news.find_one({"_id": ObjectId(news_id)})
    if news is None:
        return None

    guess_company_ids = []
    company_ids = []
    for item in items:
        company_ids.append(item["id"])

    news_company_ids = news["companyIds"]
    for company_id in news_company_ids:
        if company_id in company_ids:
            guess_company_ids.append(company_id)
    if len(guess_company_ids) == 0:
        return None
    elif len(guess_company_ids) == 1:
        return guess_company_ids[0]
    else:
        logger.info("more than one company attached with the news %s", news_id)
        return None


def main():
    no_company_funding_cnt = 0
    # fundings = conn.query("select * from funding where (active is null or active='Y' or active='P') and companyId is null order by id desc")
    fundings = conn.query("select * from funding where companyId is null order by id desc")
    for funding in fundings:
        corporate_id = funding["corporateId"]
        company_ids = get_company_ids(corporate_id)
        if len(company_ids) == 0:
            logger.info("no company! fundingId=%s, corporateId=%s", funding["id"], corporate_id)
            no_company_funding_cnt += 1
            continue
        elif len(company_ids) == 1:
            company_id = company_ids[0]
        else:
            company_id = guess_company_id(funding)

        conn.update("update funding set companyId=%s where id=%s", company_id, funding["id"])

    logger.info("no_company_funding_cnt=%s", no_company_funding_cnt)


def verify():
    fundings = conn.query("select * from funding where active is null or active !='N' order by id desc")
    for funding in fundings:
        company_id = funding["companyId"]
        corporate_id = funding["corporateId"]
        if company_id is None:
            logger.info("companyId is None. fundingId=%s", funding["id"])
            continue
        company = conn.get("select * from company where id=%s", company_id)
        if company is None:
            logger.info("company not exist. fundingId=%s", funding["id"])
            continue
        if company["corporateId"] != corporate_id:
            logger.info("company corporate not the same. fundingId=%s", funding["id"])


if __name__ == "__main__":
    main()
    # verify()