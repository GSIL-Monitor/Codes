# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/company/itjuzi'))
import itjuzi_company_3_search

# sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/company/kr36'))
# import kr36_company_2_search

#logger
loghelper.init_logger("refresh_source_company", stream=True)
logger = loghelper.get_logger("refresh_source_company")

# #Mark for user info efficient
# companycrawler = kr36_company_2_search.kr36Crawler()
# listcrawler = kr36_company_2_search.ListCrawler()

def refresh_company(companyId):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", companyId)
    corporate = conn.get("select * from corporate where id=%s", company["corporateId"])
    scs_itjuzi = conn.query("select * from source_company where source=13030 and companyId=%s and "
                            "(active is null or active='Y')", companyId)
    # scs_kr36 = conn.query("select * from source_company where source=13022 and companyId=%s and "
    #                       "(active is null or active='Y')", companyId)

    if len(scs_itjuzi) == 0:
        if company["name"] is not None and company["name"].strip() != "":
            itjuzi_company_3_search.start_run(company["name"], None)
        if corporate["fullName"] is not None and corporate["fullName"].strip() != "":
            itjuzi_company_3_search.start_run(corporate["fullName"], None)
    else:
        for sc_itjuzi in scs_itjuzi:
            if sc_itjuzi["sourceId"] is not None and sc_itjuzi["sourceId"].strip() != "":
                itjuzi_company_3_search.start_run(company["name"], sc_itjuzi["sourceId"])

    # if len(scs_kr36) == 0:
    #     if company["name"] is not None and company["name"].strip() != "":
    #         kr36_company_2_search.start_run(company["name"], None, listcrawler,companycrawler)
    #     if corporate["fullName"] is not None and corporate["fullName"].strip() != "":
    #         kr36_company_2_search.start_run(corporate["fullName"], None, listcrawler,companycrawler)
    # else:
    #     for sc_kr36 in scs_kr36:
    #         if sc_kr36["sourceId"] is not None and sc_kr36["sourceId"].strip() != "":
    #             kr36_company_2_search.start_run(company["name"], sc_kr36["sourceId"], listcrawler,companycrawler)

    conn.close()
    pass


if __name__ == '__main__':

    logger.info("python refresh_source_company")
    while True:
        conn = db.connect_torndb()
        mongo = db.connect_mongo()
        collection_raw = mongo.raw.projectdata
        collection = mongo.task.company_refresh

        tasks = list(collection.find({"status":0, "extendType":0}))
        for t in tasks:
            if t.has_key("subStatus") is True:

                if t["subStatus"].has_key("itjuzi") is True:

                    logger.info("refresh source company done %s", t["companyId"])

                elif t["subStatus"].has_key("rawCrawler") is True:

                    rawCompanies = list(collection_raw.find(
                        {"source": {'$in': [13030]}, "type": 36001, "processed": {"$ne": True}}))
                    rawCompanies2 = conn.query("select * from source_company where processStatus in (0,1) and "
                                               "source in (13030) and (active is null or active='Y')")

                    if len(rawCompanies) == 0 and len(rawCompanies2) == 0:
                        collection.update_one({"_id": t["_id"]},
                                              {"$set": {"subStatus.itjuzi": 1}})
                        logger.info("refresh source company done %s", t["companyId"])
                    else:
                        logger.info("refresh source company wait parser: %s", t["companyId"])

                else:
                    logger.info("refresh source company start: %s", t["companyId"])
                    refresh_company(t["companyId"])
                    collection.update_one({"_id": t["_id"]}, {"$set": {"subStatus.rawCrawler": 1}})
                    # in order to enhance efficient
                    break

            else:
                logger.info("refresh source company start: %s", t["companyId"])
                refresh_company(t["companyId"])
                collection.update_one({"_id": t["_id"]}, {"$set": {"subStatus.rawCrawler": 1}})

        conn.close()
        mongo.close()
        time.sleep(10)

