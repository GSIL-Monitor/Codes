# -*- coding: utf-8 -*-
import os, sys
import datetime
import time

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("openapi_funding", stream=True)
logger = loghelper.get_logger("openapi_funding")


def add_new_created_fundings():
    today = datetime.datetime.now().date()
    date1 = today + datetime.timedelta(days=-30)
    date2 = today + datetime.timedelta(days=-365*2)
    logger.info("today: %s, date1: %s, date2: %s", today, date1, date2)

    conn = db.connect_torndb()
    fundings = conn.query("select * "
                            "from funding " 
                            "where companyId is not null and " 
                            "createTime>=%s and "
                            "("
                            "(publishDate is not null and publishDate>=%s) "
                            "or "
                            "(publishDate is null and fundingDate>=%s)"
                            ")",
                          today, date1, date2)
    conn.close()

    mongo = db.connect_mongo()
    for funding in fundings:
        if funding["active"] == 'N':
            mongo.company.funding.remove({"fundingId": funding["id"]})
            continue
        item = mongo.company.funding.find_one({"fundingId": funding["id"]})
        if item is None:
            logger.info("new created funding. id: %s, companyId: %s", funding["id"], funding["companyId"])

            funding_date = None
            if funding["fundingDate"] is not None:
                funding_date = funding["fundingDate"] - datetime.timedelta(hours=8)
            funding_publishdate = None
            if funding["publishDate"] is not None:
                funding_publishdate = funding["publishDate"] - datetime.timedelta(hours=8)

            locationId = 0
            if funding["corporateId"] is not None:
                conn = db.connect_torndb()
                corporate = conn.get("select * from corporate where id=%s", funding["corporateId"])
                conn.close()
                if corporate is not None and corporate["locationId"] is not None:
                    locationId = int(corporate["locationId"])

            mongo.company.funding.insert(
                {
                    "fundingId": int(funding["id"]),
                    "companyId": int(funding["companyId"]),
                    "createTime": datetime.datetime.utcnow(),
                    "fundingCreateTime": funding["createTime"] - datetime.timedelta(hours=8),
                    "fundingDate": funding_date,
                    "fundingPublishDate": funding_publishdate,
                    "companyFullyVerify": 'N',
                    "companyFullyVerifyDetectTime": None,
                    "locationId": locationId
                }
            )
    mongo.close()


def check_verify_status():
    mongo = db.connect_mongo()
    items = mongo.company.funding.find({"companyFullyVerify":"N"})
    for item in items:
        conn = db.connect_torndb()
        flag = check_company_fully_verify(conn, item["companyId"])
        conn.close()
        if flag is True:
            logger.info("Fully verified. companyId: %s", item["companyId"])
            company_id = item["companyId"]
            corporate = conn.get("select cp.* from corporate cp join company c on c.corporateId=cp.id where c.id=%s", company_id)
            locationId = 0
            if corporate is not None and corporate["locationId"] is not None:
                locationId = int(corporate["locationId"])

            mongo.company.funding.update({"_id": item["_id"]},
                                         {"$set":{
                                             "companyFullyVerify":"Y",
                                             "companyFullyVerifyDetectTime": datetime.datetime.utcnow(),
                                             "locationId": locationId
                                         }})
        else:
            logger.info("Not fully verified. companyId: %s", item["companyId"])
    mongo.close()


def check_company_fully_verify(conn, company_id):
    # basic info
    company = conn.get("select * from company where id=%s", company_id)
    if company["verify"] is None or (company["active"] != 'Y' and company["active"] is not None):
        logger.info("companyId: %s, basic info not verified!", company_id)
        return False

    # fundings
    fundings = conn.query("select * from funding where corporateId=%s and (active is null or active='Y')",
                          company["corporateId"])
    for funding in fundings:
        if funding["verify"] is None:
            logger.info("companyId: %s, funding not verified! fundingId: %s", company_id, funding["id"])
            return False

    # tags
    # rels = conn.query("select r.* from company_tag_rel r join tag t on r.tagId=t.id "
    #                   "where r.companyId=%s and "
    #                   "(r.active is null or r.active='Y') and "
    #                   "(t.active is null or t.active='Y') and "
    #                   "t.type in (11012,11013,11011,11050,11051,11052)",
    #                   company_id)
    # for rel in rels:
    #     if rel["verify"] is None:
    #         logger.info("companyId: %s, company_tag_rel not verified! company_tag_rel id: %s", company_id, rel["id"])
    #         return False

    # members
    rels = conn.query("select * from company_member_rel where companyId=%s and (active is null or active='Y') and type=5010",
                         company_id)
    for rel in rels:
        if rel["verify"] is None:
            logger.info("companyId: %s, company_member_rel not verified! company_member_rel id: %s", company_id, rel["id"])
            return False

    # recruitment
    rels = conn.query("select * from company_recruitment_rel where companyId=%s and (active is null or active='Y')",
                         company_id)
    for rel in rels:
        if rel["verify"] is None:
            logger.info("companyId: %s, company_recruitment_rel not verified! company_recruitment_rel id: %s", company_id,
                        rel["id"])
            return False

    # artifact
    rels = conn.query("select * from artifact where companyId=%s and (active is null or active='Y')",
                      company_id)
    for rel in rels:
        if rel["verify"] is None:
            logger.info("companyId: %s, artifact not verified! artifact id: %s",
                        company_id,
                        rel["id"])
            return False

    return True


def main():
    add_new_created_fundings()
    check_verify_status()


def patch():
    mongo = db.connect_mongo()
    conn = db.connect_torndb()
    items = mongo.company.funding.find({})
    for item in items:
        locationId = None
        funding_id = item["fundingId"]
        funding = conn.get("select * from funding where id=%s", funding_id)
        if funding["corporateId"] is not None:
            conn = db.connect_torndb()
            corporate = conn.get("select * from corporate where id=%s", funding["corporateId"])
            conn.close()
            if corporate is not None:
                locationId = int(corporate["locationId"])
        mongo.company.funding.update({"_id": item["_id"]}, {"$set":{"locationId": locationId}})


if __name__ == '__main__':
    # patch()
    while True:
        main()
        time.sleep(60)