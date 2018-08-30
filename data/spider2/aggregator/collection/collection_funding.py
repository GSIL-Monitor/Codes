# -*- coding: utf-8 -*-
import os, sys
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("collection_funding", stream=True)
logger = loghelper.get_logger("collection_funding")

collectionId = 157

def process():
    logger.info("Process collection funding")
    conn = db.connect_torndb()
    fundings = conn.query("select * from funding where (active is null or active='Y') and fundingDate <= now() and fundingDate > date_sub(now(),interval 5 day)")
    for f in fundings:
        rel = conn.get("select * from collection_company_rel where (active is null or active='Y') and collectionId=%s and companyId=%s", collectionId, f["companyId"])
        if rel is None:
            conn.insert("insert collection_company_rel(collectionId,companyId,verify,active,createTime,modifyTime) \
                        values(%s,%s,'Y','Y',%s,now())",
                        collectionId, f["companyId"], f["fundingDate"])
        else:
            if f["fundingDate"] > rel["createTime"]:
                conn.update("update collection_company_rel set createTime=%s, modifyTime=now() where id=%s", f["fundingDate"], rel["id"])

    collection_funding = conn.get("select * from collection where id=%s", collectionId)
    r = conn.get("select count(*) as cnt from collection_company_rel where (active is null or active='Y') and collectionId=%s and modifyTime >=%s",
                 collectionId, collection_funding["modifyTime"])
    if r["cnt"] > 0:
        conn.update("update collection set mark='Y', modifyTime=now() where id=%s", collectionId)

    conn.close()

    logger.info("End process collection funding")


def select_one_company(corporate_id):
    if corporate_id is None:
        return None
    conn = db.connect_torndb()
    company = conn.get("select * from company where corporateId=%s and (active is null or active='Y') order by id limit 1", corporate_id)
    conn.close()
    return company


# 按发布日期
def process1():
    logger.info("Process collection funding")
    conn = db.connect_torndb()
    fundings = conn.query("select * from funding where (active is null or active='Y') and publishDate <= now() and publishDate > date_sub(now(),interval 5 day)")
    for f in fundings:
        logger.info("corporateId: %s, fundingId: %s", f["corporateId"], f["id"])
        company = select_one_company(f["corporateId"])
        if company is None:
            continue
        rel = conn.get("select * from collection_company_rel where (active is null or active='Y') and collectionId=%s and companyId=%s",
                       collectionId, company["id"])
        if rel is None:
            conn.insert("insert collection_company_rel(collectionId,companyId,verify,active,createTime,modifyTime) \
                        values(%s,%s,'Y','Y',%s,now())",
                        collectionId, company["id"], f["publishDate"])
        else:
            if f["publishDate"] > rel["createTime"]:
                conn.update("update collection_company_rel set createTime=%s, modifyTime=now() where id=%s", f["publishDate"], rel["id"])

    collection_funding = conn.get("select * from collection where id=%s", collectionId)
    r = conn.get("select count(*) as cnt from collection_company_rel where (active is null or active='Y') and collectionId=%s and modifyTime >=%s",
                 collectionId, collection_funding["modifyTime"])
    if r["cnt"] > 0:
        conn.update("update collection set mark='Y', modifyTime=now() where id=%s", collectionId)

    conn.close()

    logger.info("End process collection funding")

if __name__ == '__main__':
    process1()
