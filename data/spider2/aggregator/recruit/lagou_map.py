# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper
#logger
loghelper.init_logger("lagou_map", stream=True)
logger = loghelper.get_logger("lagou_map")

# not only for lagou also for boss
DATE = None

def find_company_by_name(full_name, short_name):
    # companyIds = []
    # full_name = name_helper.company_name_normalize(full_name)
    # conn = db.connect_torndb()
    # companies = conn.query("select * from company where fullName=%s and (active is null or active !='N') order by id desc", full_name)
    # companyIds.extend([company["id"] for company in companies if company["id"] not in companyIds])
    # # logger.info("a: %s",companyIds)
    # companies2 = conn.query( "select * from company where (name=%s or name=%s) and (active is null or active !='N') order by id desc", full_name, short_name)
    # companyIds.extend([company["id"] for company in companies2 if company["id"] not in companyIds])
    # # logger.info("b: %s", companyIds)
    # company_alias = conn.query("select distinct a.companyId from company_alias a join company c on c.id=a.companyId where (c.active is null or c.active !='N') \
    #                            and (a.active is null or a.active !='N') and (a.name=%s or a.name=%s) order by c.id desc", full_name, short_name)
    # companyIds.extend([company["companyId"] for company in company_alias if company["companyId"] not in companyIds])
    # # logger.info("c: %s", companyIds)
    # return companyIds
    pass


def get_companyId(sourceId, source):
    conn = db.connect_torndb()
    source_company = conn.get("select * from source_company where source=%s and sourceId=%s", source, sourceId)
    if source_company is None:
        cid = None; active = None
    else:
        if source_company["companyId"] is not None:
            cid = int(source_company["companyId"]); active = source_company["active"]
        else:
            cid = None; active = source_company["active"]
    conn.close()
    return {"cid": cid, "active": active}



def insert(companyId,jobCompanyId):
    sql = "insert company_recruitment_rel(jobCompanyId,companyId,createTime,modifyTime) values(%s,%s,now(),now())"
    conn = db.connect_torndb()
    rel = conn.get("select * from company_recruitment_rel where jobCompanyId=%s and companyId=%s",jobCompanyId,companyId)
    if rel is None:
        conn.insert(sql, jobCompanyId,companyId)
    conn.close()
    pass

if __name__ == '__main__':
    logger.info("Begin...")
    # num0=0;num1=0;num2=0;num3=0;num4=0;num5=0
    while True:
        num0 = 0
        num1 = 0
        num2 = 0
        num3 = 0
        num4 = 0
        num5 = 0
        mongo = db.connect_mongo()
        collection_company = mongo.job.company

        dt = datetime.date.today()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        if datestr != DATE:
            # init
            collection_company.update_many({"mapChecked": False}, {"$set": {"mapChecked": None}})
            DATE = datestr

        # mongo = db.connect_mongo()
        # collection_company = mongo.job.company
        source_companies = list(collection_company.find({"mapChecked": None,"source":13050}).limit(1000))

        for sourcecompany in source_companies:
            # logger.info("sourceId %s", sourcecompany['sourceId'])
            # checking source
            if sourcecompany["source"] not in [13050]:
                collection_company.update_one({"_id": sourcecompany["_id"]}, {"$set": {"mapChecked": False}})
                continue

            result = get_companyId(sourcecompany["sourceId"], sourcecompany["source"])


            if result["cid"] is None:
                logger.info("source: %s|%s maped nothing", sourcecompany["name"], sourcecompany["sourceId"])
                if result["active"] == 'A' or result["active"] == 'P': num1 += 1
                elif result["active"] == 'N': num2 += 1
                else: num3 += 1
                collection_company.update_one({"_id": sourcecompany["_id"]}, {"$set": {"mapChecked": False}})
            else:
                # logger.info("source: %s|%s maped company: %s|%s", sourcecompany["name"], sourcecompany["sourceId"],
                #             result["cid"], result["active"])
                if result["active"] == 'N':
                    num4 += 1
                    collection_company.update_one({"_id": sourcecompany["_id"]}, {"$set": {"mapChecked": False}})
                else:
                    num5 += 1
                    insert(int(result["cid"]),str(sourcecompany["_id"]))
                    collection_company.update_one({"_id": sourcecompany["_id"]}, {"$set": {"mapChecked": True}})

            num0 += 1
        logger.info("recruit has finished")
        mongo.close()
        # break
        logger.info("num: %s/%s/%s/%s/%s/%s", num0, num1, num2, num3, num4, num5)
        logger.info("End.")
        if len(source_companies) == 0:
            time.sleep(60*60)
