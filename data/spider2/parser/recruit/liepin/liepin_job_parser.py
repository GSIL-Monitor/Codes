# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
from bson import json_util
from pyquery import PyQuery as pq
from lxml import html

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper, util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util,db

# logger
loghelper.init_logger("liepin_job_parser", stream=True)
logger = loghelper.get_logger("liepin_job_parser")

SOURCE = 13056  # liepin
TYPE = 36010  # job info


def parse_companyjobs(source_company_id, item, sourceId):
    source_jobs = []
    logger.info("source_company_id is %s", source_company_id)

    d = pq((html.fromstring(item["content"].decode("utf-8"))))
    # logger.info("this page has %s jobs", position_type, len(jobs))
    for li in d('.job-info'):
        dj = pq(li)
        job_link = dj('a.title').attr("href")
        job_key = job_link.split("/")[-1].replace(".shtml", "")
        born_time = dj('time').attr('title')
        position = dj('a.title').attr("title")

        city = dj('.condition span:nth-child(2)').text().split('-')[0]
        work_year = dj('.condition span:nth-child(4)').text()
        education = dj('.condition span:nth-child(3)').text()
        logger.info("%s - %s - %s", city, work_year, education)

        salary = dj('.condition span:nth-child(1)').text()
        # update_time = born_time

        domain = 0

        location_id = 0
        location_new = parser_db_util.get_location(city)
        if location_new != None:
            location_id = location_new["locationId"]

        education_type = 0
        if '大专' in education:
            education_type = 6020
        elif '本科' in education:
            education_type = 6030
        elif '硕士' in education:
            education_type = 6040
        elif '博士' in education:
            education_type = 6050

        workYear_type = 7000
        if '应届' in work_year:
            workYear_type = 7010
        elif '1年以下' in work_year:
            workYear_type = 7020
        elif '1年以上' in work_year or '2年以上' in work_year:
            workYear_type = 7030
        elif '3年以上' in work_year:
            workYear_type = 7040
        elif '5年以上' in work_year or '6年以上' in work_year or '8年以上' in work_year:
            workYear_type = 7050
        elif '10年以上' in work_year:
            workYear_type = 7060

        logger.info("born time: %s", born_time)
        try:
            born_time = born_time.replace("发布于", "")
            if born_time.find("月") >= 0:
                logger.info("neeewdate:%s", born_time)
                update_time = datetime.datetime.strptime(born_time, "%Y年%m月%d日")
            else:
                update_time = datetime.datetime.now()
        except Exception, e:
            logger.info(e)
            update_time = datetime.datetime.now()

        source_job = {
            "source": SOURCE,
            "sourceId": job_key,
            "recruit_company_id": str(source_company_id),
            "position": position,
            "salary": salary,
            "description": None,
            "domain": domain,
            "locationId": location_id,
            "educationType": education_type,
            "workYearType": workYear_type,
            "startDate": update_time,
            "updateDate": update_time,
            "jobNature": None,
            "positionAdvantage": None,
            "companyLabelList": None,
            "financeStage": None,
            "district": None,
        }
        logger.info("job_key: %s", job_key)
        for i in source_job:
            logger.info("%s->%s", i, source_job[i])

        source_jobs.append(source_job)

    logger.info(json.dumps(source_jobs, ensure_ascii=False, cls=util.CJsonEncoder))
    logger.info("scid %s, sourceId %s currently has %s jobs", source_company_id, sourceId, len(source_jobs))
    save_job_mongo(source_jobs)


def save_job_mongo(jobs):
    mongo = db.connect_mongo()
    collection = mongo.job.job
    for job in jobs:
        jobitems = list(collection.find({"source": SOURCE, "sourceId": job["sourceId"], "offline": 'N'}))
        if len(jobitems) == 0:
            jobitems = list(
                collection.find({"source": SOURCE, "recruit_company_id": job["recruit_company_id"], "offline": 'N'}))

        newflag = True
        # try:
        #     job["updateDate"]=datetime.datetime.strptime(job["updateDate"],"%Y-%m-%d %H:%M")
        # except:
        #     job["updateDate"] = datetime.datetime.strptime(job["updateDate"], "%Y-%m-%d")

        for jobitem in jobitems:
            if jobitem["position"] == job["position"] and jobitem["salary"] == job["salary"] and \
                    jobitem["educationType"] == job["educationType"] and jobitem["locationId"] == job["locationId"] and \
                    jobitem["workYearType"] == job["workYearType"]:

                logger.info("Same job for existed and we got, update updateTime for job:%s for company:%s",
                            job["position"], job.get("recruit_company_id", "no_id"))
                updateflag = True
                newflag = False

                if jobitem.has_key("jobNature") is False:
                    logger.info("*********adding more info! great!!!!")
                    collection.update_one({"_id": jobitem["_id"]},
                                          {'$set': {"sourceId": job["sourceId"],
                                                    "jobNature": job["jobNature"],
                                                    "positionAdvantage": job["positionAdvantage"],
                                                    "companyLabelList": job["companyLabelList"],
                                                    "financeStage": job["financeStage"],
                                                    "district": job["district"],
                                                    "recruit_company_id": job["recruit_company_id"]
                                                    },
                                           })

                for updatetime in jobitem["updateDates"]:
                    if (updatetime + datetime.timedelta(hours=8)).date() == job[
                        "updateDate"].date(): updateflag = False; break
                if updateflag is True:
                    logger.info("update updatetime now")

                    collection.update_one({"_id": jobitem["_id"]},
                                          {'$set': {"modifyTime": datetime.datetime.now(),
                                                    "updateDate": job["updateDate"] - datetime.timedelta(hours=8)},
                                           '$addToSet': {
                                               "updateDates": job["updateDate"] - datetime.timedelta(hours=8)}})

                else:
                    collection.update_one({"_id": jobitem["_id"]}, {'$set': {"modifyTime": datetime.datetime.now()}})
                break

        if newflag is True:
            logger.info("add new job:%s for company:%s", job["position"], job["recruit_company_id"])
            item = {"source": SOURCE, "sourceId": job["sourceId"], "recruit_company_id": job["recruit_company_id"],
                    "position": job["position"], "salary": job["salary"],
                    "description": job["description"], "domain": int(job["domain"]),
                    "locationId": int(job["locationId"]), "educationType": int(job["educationType"]),
                    "workYearType": int(job["workYearType"]),
                    "jobNature": job["jobNature"], "positionAdvantage": job["positionAdvantage"],
                    "companyLabelList": job["companyLabelList"], "financeStage": job["financeStage"],
                    "district": job["district"],
                    "startDate": job["updateDate"] - datetime.timedelta(hours=8), "offline": "N",
                    "updateDate": job["updateDate"] - datetime.timedelta(hours=8),
                    "updateDates": [job["updateDate"] - datetime.timedelta(hours=8)],
                    "createTime": datetime.datetime.now(), "modifyTime": datetime.datetime.now(),
                    "active": None, "verify": None, "createUser": None, "modifyUser": None}
            collection.insert(item)
            

if __name__ == "__main__":
    pass
