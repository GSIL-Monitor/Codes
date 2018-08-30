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
loghelper.init_logger("lagou_patch", stream=True)
logger = loghelper.get_logger("lagou_patch")

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


def get_companyId(sourceId):
    conn = db.connect_torndb()
    source_company = conn.get("select * from source_company where source=13050 and sourceId=%s", sourceId)
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
    num0=0;num1=0;num2=0;num3=0;num4=0;num5=0
    while True:
        conn = db.connect_torndb()
        mongo = db.connect_mongo()
        collection_job = mongo.job.job
        jobs = list(collection_job.find({"recruit_company_id": None}).sort("_id", pymongo.DESCENDING).limit(10000))

        for job in jobs:
            # logger.info("sourceId %s", sourcecompany['sourceId'])

            if job["companyId"] is None:
                collection_job.update_one({"_id": job["_id"]}, {"$set": {"recruit_company_id": ""}})
                num4 += 1

            else:
                rels = conn.query("select * from company_recruitment_rel where companyId=%s",job["companyId"])


                if len(rels) == 0:
                    collection_job.update_one({"_id": job["_id"]},
                                              {"$set": {"recruit_company_id": ""}})

                elif len(rels) == 1:
                    collection_job.update_one({"_id": job["_id"]},
                                              {"$set": {"recruit_company_id": str(rels[0]["jobCompanyId"])}})
                    logger.info("update %s with %s", job["_id"], str(rels[0]["jobCompanyId"]))
                    num2 += 1
                else:
                    collection_job.update_one({"_id": job["_id"]},
                                              {"$set": {"recruit_company_id": ""}})

            num0 += 1
        logger.info("Lagou has finished")
        mongo.close()
        conn.close()
        # break

        if len(jobs) == 0:
            break
    logger.info("num: %s/%s/%s/%s/%s/%s", num0,num1,num2,num3,num4,num5)
    logger.info("End.")