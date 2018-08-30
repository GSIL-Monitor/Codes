# -*- coding: utf-8 -*-
import os, sys
import datetime,time
import json
from bson import json_util
from pyquery import PyQuery as pq
from lxml import html

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

SOURCE = 13055  #Boss
TYPE = 36010    #job info


def parse_companyjobs(source_company_id, item, sourceId):
    source_jobs = []
    logger.info("source_company_id is %s", source_company_id)
    if item["content"].has_key("version") and item["content"]["version"] == 2:
        logger.info("version 2!!!!")
        for ptype in item["content"]:
            if ptype == "version":
                continue
            position_type = ptype
            for content in item["content"][position_type]:
                d = pq((html.fromstring(content.decode("utf-8"))))
                # logger.info("this page has %s jobs", position_type, len(jobs))
                domain = 0
                if position_type == '技术':
                    domain = 15010
                elif position_type == '产品':
                    domain = 15020
                elif position_type == '设计':
                    domain = 15030
                elif position_type == '运营':
                    domain = 15040
                elif position_type == '市场' or position_type == '销售':
                    domain = 15050
                elif position_type.find('职能')>=0:
                    domain = 15060
                elif position_type == '金融':
                    domain = 15070

                for li in d('div.job-list> ul> li'):

                    dj = pq(li)
                    job_link = dj('a').eq(0).attr("href")
                    job_key = job_link.split("/")[-1].replace(".html","")
                    born_time = dj('div.info-publis> p').text()
                    position = dj('div.title-box> div.job-title').text()
                    (city,work_year,education) = (None, None, None)
                    lll = dj('div.job-primary> div.info-primary> p').text().strip()
                    logger.info("lll %s", lll)
                    if len(lll.split(" ")) == 3:
                        education = lll.split(" ")[2]
                        city = lll.split(" ")[0]
                        work_year = lll.split(" ")[1]
                    logger.info("%s - %s - %s",city,work_year,education )
                    salary = dj('div.title-box> span').text()

                    # update_time = born_time

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

                    t = datetime.datetime.today()
                    logger.info("born time: %s", born_time)
                    try:
                        if born_time.find("发布于") >= 0:
                            born_time = born_time.replace("发布于","")
                            if born_time.find("月") >= 0:
                                logger.info("neeewdate:%s", str(t.year)+"年"+born_time)
                                update_time = datetime.datetime.strptime(str(t.year)+"年"+born_time, "%Y年%m月%d日")
                                if update_time > datetime.datetime.now():
                                    update_time = update_time - datetime.timedelta(days=365)
                            elif born_time.find("昨天") >= 0:
                                update_time = datetime.datetime.now() - datetime.timedelta(days=1)
                            else:
                                update_time = datetime.datetime.now()
                        else:
                            update_time = datetime.datetime.now()
                    except Exception,e:
                        logger.info(e)
                        update_time = datetime.datetime.now()



                    source_job = {
                        "source": 13055,
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
                       logger.info("%s->%s",i,source_job[i])

                    source_jobs.append(source_job)
    else:
        pass

    logger.info(json.dumps(source_jobs, ensure_ascii=False, cls=util.CJsonEncoder))
    logger.info("scid %s, sourceId %s currently has %s jobs", source_company_id, sourceId, len(source_jobs))
    return source_jobs



if __name__ == "__main__":
    pass