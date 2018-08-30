# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html

from bson.objectid import ObjectId
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import util
import db
import parser_util
from pyquery import PyQuery as pq

source = 13051
def parse_job(job_key):

    job = fromdb.job.find_one({"source": source, "job_key":job_key})
    if job == None:
        return
    job_key = job["job_key"]
    company_key = job["company_key"]

    logger.info(job_key)
    logger.info(company_key)
    content = job["content"]
    d = pq(content)

    if len(d('.jobnote')) == 0:
        return

    publish_date = d('.jobnote:first').text()  # text() result is tuple
    date_len = len(publish_date)
    start_time = ''.join(publish_date)[date_len-9:date_len-4]
    start_time = start_time.replace('月', '-')


    # add start year based on job_key
    # 17748: 2013
    # 330001: 2014

    if int(job_key) < 17748:
        start_year = 2013
    elif int(job_key) < 330001:
        start_year = 2014
    elif int(job_key) < 430000:
        start_year = 2015
    else:
        start_year = 2016
        now = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        if(now[5:7] < start_time[0:2]):
            start_year = 2015

    start_time = str(start_year)+ '-'+start_time

    position = d('.jobnote> strong').text()
    salary = d('.pay').text()
    experience = d('.experience').text()

    if salary is not None:
        salary = salary.replace('[', '').replace(']', '')

    if experience is not None:
        experience = experience.replace('[', '').replace(']', '')
        workYear_type = 7000
        if experience == '应届毕业生':
            workYear_type = 7010
        elif experience == '1年以下':
            workYear_type = 7020
        elif experience == '1-3年':
            workYear_type = 7030
        elif experience == '3-5年':
            workYear_type = 7040
        elif experience == '5-10年':
            workYear_type = 7050
        elif experience == '10年以上':
            workYear_type = 7060


    location = d('.jobtitle-r').html()
    # if location is not None:
    #     (location,) = util.re_get_result('地点：(\S+)', ''.join(location))
    #
    # # try to find location
    # if location is not None:
    #     location = location[0:2]
    #     location_id = parser_util.get_location_id(location)

    desc = d('.jobdetail').html()

    source_company_id = parse_company(company_key)

    source_job = {
                    "sourceId": job_key,
                    "sourceCompanyId": source_company_id,
                    "position": position,
                    "salary": salary,
                    "description": desc,
                    "domain": None,
                    "locationId": None,
                    "educationType": None,
                    "workYearType": workYear_type,
                    "startDate": start_time,
                    "updateDate": None,
                    }

    parser_util.insert_source_job(source_job)

    msg = {"type":"job", "id":source_company_id}
    kafka_producer.send_messages("parser_v2", json.dumps(msg))



def parse_company(company_key):
    company = fromdb.company.find_one({"source": source, "company_key":company_key})
    if company == None:
        return

    content = company["content"]
    d = pq(content)
    logo_url = d('.img_inner').attr('src')
    logo_id = None
    if logo_url is not None:
        logo_id = parser_util.get_logo_id(source, company_key, 'company', logo_url)

    name = d('.online_resume_cont > h3').html()
    (name,) = util.re_get_result('<span>(\S+) <em to="links">',name)

    link = d('em > a').attr('href')

    location = d('.company_des_item:eq(0) > span:eq(1)').text()
    field = d('.company_des_item:eq(1) > span:eq(1)').text()
    headCount = d('.company_des_item:eq(2) > span:eq(1)').text()
    stage = d('.company_des_item:eq(3) > span:eq(1)').text()
    brief = d('.company_des_item:eq(4) > span:eq(1)').text()
    desc = d('.detail_infos').html()


    location_id = parser_util.get_location_id(location)

    stage = ''.join(stage)

    funding_type = 0
    if stage == '不需要融资':
        stage = 0
        funding_type = 8010
    elif stage == '未融资':
        stage = 0
    elif stage == '天使轮':
        stage = 1010
    elif stage == 'A轮':
        stage = 1030
    elif stage == 'B轮':
        stage = 1040
    elif stage == 'C轮':
        stage = 1050
    elif stage == 'D轮':
        stage = 1060
    elif stage == '已上市':
        stage = 1110
    else:
        stage = 0

    headCount = ''.join(headCount).replace('人', '')

    if headCount == "少于15" or headCount == '15以下':
        min_staff = 1
        max_staff = 15
    elif headCount == '1000以上':
        min_staff = 1000
        max_staff = None
    else:
        staffarr = headCount.split('-')
        if len(staffarr) > 1:
            min_staff = staffarr[0]
            max_staff = staffarr[1]
        else:
            min_staff = staffarr[0]
            max_staff = None

    if min_staff == '':
        min_staff = None

    source_company = {"name": name,
                      "fullName": None,
                      "description": desc,
                      "brief": brief,
                      "round": stage,
                      "roundDesc": None,
                      "companyStatus": 2010,
                      'fundingType':funding_type,
                      "locationId": location_id,
                      "address": None,
                      "phone": None,
                      "establishDate": None,
                      "logo": logo_id,
                      "source": source,
                      "sourceId": company_key,
                      "field": field,
                      "subField": None,
                      "tags": None,
                      "headCountMin": min_staff,
                      "headCountMax": max_staff
                      }

    source_company_id = parser_util.insert_source_company(source_company)

    source_artifact = {"sourceCompanyId": source_company_id,
                       "name": name,
                       "description": None,
                       "link": link,
                       "type": 4010
                       }

    parser_util.insert_source_artifact(source_artifact)


    return source_company_id




if __name__ == '__main__':
    (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("recruit_neitui", "crawler_recruit_neitui")

    while True:
        try:
            for message in kafka_consumer:
                try:
                    # logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                    #                                            message.offset, message.key,
                    #                                            message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    job_key = msg["job_key"]

                    if type == "job":
                        parse_job(job_key)

                    # kafka_consumer.task_done(message)
                    # kafka_consumer.commit()
                except Exception,e :
                    logger.error(e)
                    traceback.print_exc()
        except Exception,e :
            logger.error(e)
            traceback.print_exc()
            time.sleep(60)
            (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("recruit_neitui", "crawler_recruit_neitui")
