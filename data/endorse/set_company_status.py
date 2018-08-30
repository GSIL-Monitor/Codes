# -*- coding: utf-8 -*-
import os, sys
import time
from datetime import datetime
from datetime import timedelta

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, name_helper

#logger
loghelper.init_logger("set_company_status", stream=True)
logger = loghelper.get_logger("set_company_status")


def process_fa():
    logger.info("start process fa")
    month3 = datetime.now() - timedelta(days=90)

    conn = db.connect_torndb()
    cs = conn.query("select distinct companyId from company_fa")
    for item in cs:
        company_id = item["companyId"]
        if company_id is None:
            continue
        company = conn.get("select * from company where id=%s", company_id)
        if company is None:
            continue

        c = conn.get("select * from company_fa f join dictionary d on f.source=d.value "
                     "where d.subTypeValue=1301 and (active is null or active='Y') and "
                     "companyId=%s order by publishDate desc limit 1", company_id)
        if c is None:
            continue

        had_funding = False
        funding = conn.get("select * from funding where (active is null or active='Y') and "
                           "corporateId=%s order by fundingDate desc limit 1", company["corporateId"])
        if funding and funding["fundingDate"] is not None and funding["fundingDate"] >= c["publishDate"]:
            had_funding = True

        if c["publishDate"] > month3 and c["endDate"] is None and had_funding is False:
            if company["companyStatus"] != 2015:
                logger.info("company: id=%s, code=%s, name=%s is funding", company_id, company["code"], company["name"])
                conn.update("update company set companyStatus=2015 where id=%s", company_id)
        else:
            if company["companyStatus"] == 2015:
                logger.info("company: id=%s, code=%s, name=%s finished funding", company_id, company["code"], company["name"])
                conn.update("update company set companyStatus=2010 where id=%s", company_id)

    conn.close()
    logger.info("end process fa")


def process_collection(collection_id):
    logger.info("start process collection %s", collection_id)
    month3 = datetime.now() - timedelta(days=90)

    conn = db.connect_torndb()
    cs = conn.query("select c.* from collection_company_rel r join company c on r.companyId=c.id where r.collectionId=%s", collection_id)
    collection = conn.get("select * from collection where id=%s", collection_id)
    for c in cs:
        company_id = c["id"]

        had_funding = False
        funding = conn.get("select * from funding where (active is null or active='Y') and "
                           "corporateId=%s order by fundingDate desc limit 1", c["corporateId"])
        if funding and funding["fundingDate"] is not None and funding["fundingDate"] >= collection["createTime"]:
            had_funding = True

        if collection["createTime"] > month3 and had_funding is False:
            if c["companyStatus"] != 2015:
                logger.info("company: id=%s, code=%s, name=%s is funding", company_id, c["code"], c["name"])
                conn.update("update company set companyStatus=2015 where id=%s", company_id)
        else:
            if c["companyStatus"] == 2015:
                logger.info("company: id=%s, code=%s, name=%s finished funding", company_id, c["code"], c["name"])
                conn.update("update company set companyStatus=2010 where id=%s", company_id)
    conn.close()
    logger.info("end process collection %s", collection_id)


if __name__ == "__main__":
    # conn = db.connect_torndb()
    # conn.execute("update company set companyStatus=2010 where companyStatus=2015")
    # conn.close()
    while True:
        logger.info("Start...")
        process_fa()
        # process_collection(974)  # gobi vc day
        logger.info("End.")
        time.sleep(3600*2) #2 hours