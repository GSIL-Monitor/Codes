# -*- coding: utf-8 -*-
import os, sys, re, json
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config, util
import db

#logger
loghelper.init_logger("lagou", stream=True)
logger = loghelper.get_logger("lagou")


#mongo
mongo = db.connect_mongo()
collection = mongo.job.job

collection_lagou = mongo.trend.jobs

def save_job_mongo(company_id, jobs, offline):
    for job in jobs:
        # jobitems = list(collection.find({"source":13050, "sourceId": job["sourceId"], "offline": 'N'}))
        # if len(jobitems) == 0:
        #     jobitems = list(collection.find({"source":13050, "companyId":company_id, "offline": 'N'}))
        jobitems=[]
        newflag = True

        for jobitem in jobitems:
            if jobitem["companyId"]==company_id and jobitem["position"]==job["position"] and jobitem["salary"]==job["salary"] and \
            jobitem["educationType"]==job["educationType"] and jobitem["locationId"]==job["locationId"] and jobitem["workYearType"]==job["workYearType"]:
                logger.info("Same job for existed and we got, update updateTime for job:%s for company:%s", job["position"], job["companyId"])
                updateflag = True
                newflag = False
                for updatetime in jobitem["updateDates"]:
                    if updatetime.date() == job["updateDate"].date(): updateflag = False; break
                if updateflag is True:
                    collection.update_one({"_id": jobitem["_id"]},{'$set': {"sourceId":job["sourceId"]},'$addToSet': {"updateDates": job["updateDate"]}})
                break

        if newflag is True:
            logger.info("add new job:%s for company:%s", job["position"], job["companyId"])
            item = {
                "source": 13050, "sourceId": job["sourceId"], "companyId": int(company_id),
                    "position": job["position"], "salary": job["salary"],
                    "description": job["description"], "domain": int(job["domain"]),
                    "locationId": int(job["locationId"]), "educationType": int(job["educationType"]),
                    "workYearType": int(job["workYearType"]),
                    # "jobNature":job["jobNature"],"positionAdvantage": job["positionAdvantage"],
                    # "companyLabelList": job["companyLabelList"],"financeStage": job["financeStage"], "district": job["district"],
                    "startDate": job["updateDate"] - datetime.timedelta(hours=8), "offline": offline,
                    "updateDate": job["updateDate"] - datetime.timedelta(hours=8),
                    "updateDates": [job["updateDate"] - datetime.timedelta(hours=8)],
                    "createTime": job["createTime"], "modifyTime": job["modifyTime"],
                    "active": None, "verify": None, "createUser": None, "modifyUser": None}

            collection.insert(item)

def save_job_mongo_2(job):

    newflag = True
    last_update = None

    for ud in job["updateDates"]:
        if last_update is None: last_update = ud
        else:
            if ud > last_update: last_update = ud

    if newflag is True:
        logger.info("add new job:%s|%s for company:%s", job["position"], last_update, job["companyId"])
        logger.info("%s,%s", last_update, job["updateDates"])
        item = {
            "source": 13050, "sourceId": job["sourceId"], "companyId": job["companyId"],
                "position": job["position"], "salary": job["salary"],
                "description": job["description"], "domain": int(job["domain"]),
                "locationId": int(job["locationId"]), "educationType": int(job["educationType"]),
                "workYearType": int(job["workYearType"]),
                # "jobNature":job["jobNature"],"positionAdvantage": job["positionAdvantage"],
                # "companyLabelList": job["companyLabelList"],"financeStage": job["financeStage"], "district": job["district"],
                "startDate": job["startDate"], "offline": job["offline"],
                "updateDate": last_update,
                "updateDates": job["updateDates"],
                "createTime": job["createTime"], "modifyTime": job["modifyTime"],
                "active": None, "verify": None, "createUser": None, "modifyUser": None}

        collection.insert(item)



if __name__ == "__main__":
    start = 0
    num = 0
    cid = 0
    # while True:
    #     conn = db.connect_torndb()
    #     jobs = list(conn.query("select * from job where offline='Y' and  modifyTime<'2017-02-05'"))
    #     if len(jobs) == 0:
    #         break
    #
    #     for job in jobs:
    #         job["sourceId"] = None
    #         save_job_mongo(job["companyId"],[job], 'Y')
    #         # break
    #
    #     conn.close()
    #     break

    while True:
        logger.info("lagou start...")
        # run(appmkt, WandoujiaCrawler(), "com.ctd.m3gd")
        jobs = list(collection_lagou.find({"m_processed": {"$ne": True}},limit=2000))
        for job in jobs:
            save_job_mongo_2(job)
            collection_lagou.update_one({"_id": job["_id"]},{"$set":{"m_processed": True}})
        logger.info("lagou end.")

        # break




