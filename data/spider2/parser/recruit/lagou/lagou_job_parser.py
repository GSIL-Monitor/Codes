# -*- coding: utf-8 -*-
import os, sys
import datetime,time
import json
from bson import json_util
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper,util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("lagou_job_parser", stream=True)
logger = loghelper.get_logger("lagou_job_parser")

SOURCE = 13050  #Lagou
TYPE = 36010    #job info

# def process():
#     logger.info("lagou_company_job_parser begin...")
#     while True:
#
#         items = parser_db_util.find_process_limit(SOURCE, TYPE, 0, 2000)
#
#         for item in items:
#             logger.info(item["url"])
#
#             company_key = item["key"]
#             source_company = parser_db_util.get_company(SOURCE, company_key)
#
#             if source_company is None:
#                 logger.info("Lagou company key %s doesn't exist yet", item["key"])
#                 #break
#             else:
#                 source_company_id = source_company["id"]
#                 source_jobs = parse_companyjobs_save(source_company_id, item)
#                 if len(source_jobs) > 0:
#                     parser_db_util.save_jobs_standard(source_jobs)
#                     pass
#
#                 parser_db_util.update_processed(item["_id"])
#
#             exit()
#             #break
#
#         if len(items) < 400:
#             break
#
#
#     logger.info("lagou_company_job_parser end.")

def parse_companyjobs(source_company_id, item, sourceId):
    source_jobs = []
    logger.info("source_company_id is %s", source_company_id)
    if item["content"].has_key("version") and item["content"]["version"] == 2:
        logger.info("version 2!!!!")
        for type in item["content"]:
            if type == "version":
                continue
            position_type = type
            for jobpage in item["content"][type]:
                jobs = jobpage['content']['data']['page']['result']
                logger.info("%s has %s jobs", position_type, len(jobs))
                for job_content in jobs:
                    #logger.info("%s has %s jobs", position_type, len(jobs))
                    if sourceId != str(job_content["companyId"]):
                        logger.info("sourceId is not correct")
                        continue
                    domain = 0
                    if position_type == '技术':
                        domain = 15010
                    elif position_type == '产品':
                        domain = 15020
                    elif position_type == '设计':
                        domain = 15030
                    elif position_type == '运营':
                        domain = 15040
                    elif position_type == '市场与销售':
                        domain = 15050
                    elif position_type == '职能':
                        domain = 15060
                    elif position_type == '金融':
                        domain = 15070

                    job_key = job_content["positionId"]
                    born_time = None
                    position = job_content.get("positionName")
                    education = job_content.get("education")
                    city = job_content.get("city")
                    salary = job_content["salary"]
                    work_year = job_content["workYear"]
                    update_time = job_content["createTime"]

                    location_id = 0
                    location_new = parser_db_util.get_location(city)
                    if location_new != None:
                        location_id = location_new["locationId"]

                    education_type = 0
                    if education == '大专':
                        education_type = 6020
                    elif education == '本科':
                        education_type = 6030
                    elif education == '硕士':
                        education_type = 6040
                    elif education == '博士':
                        education_type = 6050

                    workYear_type = 7000
                    if work_year == '应届毕业生':
                        workYear_type = 7010
                    elif work_year == '1年以下':
                        workYear_type = 7020
                    elif work_year == '1-3年':
                        workYear_type = 7030
                    elif work_year == '3-5年':
                        workYear_type = 7040
                    elif work_year == '5-10年':
                        workYear_type = 7050
                    elif work_year == '10年以上':
                        workYear_type = 7060

                    date = "%s" % time.strftime("%Y-%m-%d", time.localtime())
                    if '-' not in update_time and update_time != None:
                        update_time = date + ' ' + update_time.strip()


                    source_job = {
                        "sourceId": job_key,
                        "sourceCompanyId": source_company_id,
                        "position": position,
                        "salary": salary,
                        "description": None,
                        "domain": domain,
                        "locationId": location_id,
                        "educationType": education_type,
                        "workYearType": workYear_type,
                        "startDate": born_time,
                        "updateDate": update_time,
                    }
                    logger.info("job_key: %s", job_key)
                    # for i in source_job:
                    #    logger.info("%s->%s",i,source_job[i])

                    source_jobs.append(source_job)
    else:
        jobs = item["content"]['content']['data']['page']['result']
        for job_content in jobs:
            job_key = job_content["positionId"]

            born_time = job_content.get("bornTime")
            position = job_content.get("positionName")
            education = job_content.get("education")
            city = job_content["city"]
            # keywords = job_content["keyWords"]
            salary = job_content["salary"]
            work_year = job_content["workYear"]
            position_type = job_content["positionFirstType"]
            update_time = job_content["createTime"]

            #location_id = parser_util.get_location_id(city)
            location_id = 0
            location_new = parser_db_util.get_location(city)
            if location_new != None:
                location_id = location_new["locationId"]

            education_type = 0
            if education == '大专':
                education_type = 6020
            elif education == '本科':
                education_type = 6030
            elif education == '硕士':
                education_type = 6040
            elif education == '博士':
                education_type = 6050

            workYear_type = 7000
            if work_year == '应届毕业生':
                workYear_type = 7010
            elif work_year == '1年以下':
                workYear_type = 7020
            elif work_year == '1-3年':
                workYear_type = 7030
            elif work_year == '3-5年':
                workYear_type = 7040
            elif work_year == '5-10年':
                workYear_type = 7050
            elif work_year == '10年以上':
                workYear_type = 7060

            domain = 0
            if position_type == '技术':
                domain = 15010
            elif position_type == '产品':
                domain = 15020
            elif position_type == '设计':
                domain = 15030
            elif position_type == '运营':
                domain = 15040
            elif position_type == '市场与销售':
                domain = 15050
            elif position_type == '职能':
                domain = 15060
            elif position_type == '金融':
                domain = 15070

            date = "%s" % time.strftime("%Y-%m-%d", time.localtime())
            if '-' not in born_time:
                born_time = date + ' ' + born_time.strip()
            if '-' not in update_time and update_time != None:
                update_time = date + ' ' + update_time.strip()



            source_job = {
                "sourceId": job_key,
                "sourceCompanyId": source_company_id,
                "position": position,
                "salary": salary,
                "description": None,
                "domain": domain,
                "locationId": location_id,
                "educationType": education_type,
                "workYearType": workYear_type,
                "startDate": born_time,
                "updateDate": update_time,
            }
            logger.info("job_key: %s",job_key)
            #for i in source_job:
            #    logger.info("%s->%s",i,source_job[i])

            source_jobs.append(source_job)

    logger.info(json.dumps(source_jobs, ensure_ascii=False, cls=util.CJsonEncoder))
    logger.info("scid %s, sourceId %s currently has %s jobs", source_company_id, sourceId, len(source_jobs))
    return source_jobs



if __name__ == "__main__":
    pass