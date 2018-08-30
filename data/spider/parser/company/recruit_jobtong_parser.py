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
import requests
import util
import parser_util
from pyquery import PyQuery as pq

source = 13052
def parse_company(company_key):
    company = fromdb.company.find_one({"source": source, "company_key":company_key})
    if company == None:
        return

    content = company["content"]

    d = pq(content)

    logo_url = d('.header > img').attr('src')
    logo_id = None
    logo_url = ''.join(logo_url)
    if logo_url != '':
        logo_id = parser_util.get_logo_id(source, company_key, 'company', logo_url)

    name = d('.header > h1').text()
    brief = d('.header > h3').text()

    location = d('.tag:eq(0)').text()
    stage = ''
    headCount = None
    field = None

    if len(d('.tag')) == 5:
        stage = d('.tag:eq(1)').text()
        headCount = d('.tag:eq(2)').text()
        companyType = d('.tag:eq(3)').text()
        field = d('.tag:eq(4)').text()
    elif len(d('.tag')) == 4:
        headCount = d('.tag:eq(1)').text()
        companyType = d('.tag:eq(2)').text()
        field = d('.tag:eq(3)').text()


    fullName = d('.info > p:eq(0)').text()
    link = d('.info > p:eq(1)').text()
    address = d('.info > p:eq(2)').text()
    address =  location + address

    desc = d('.introduce > div:eq(0)').text()


    location = location.replace('市', '')
    location_id = parser_util.get_location_id(location)


    funding_type = 0
    if '天使' in stage:
        stage = 1010
    elif 'A' in stage:
        stage = 1030
    elif 'B' in stage:
        stage = 1040
    elif 'C' in stage:
        stage = 1050
    elif 'D' in stage:
        stage = 1060
    elif 'public' in stage:
        stage = 1110
    else:
        stage = 0

    logger.info(stage)

    if headCount is None or headCount == '':
        min_staff = 0
        max_staff = 0
    elif headCount == "15人以下":
        min_staff = 1
        max_staff = 15
    elif headCount == "2000人以上":
        min_staff = 2000
        max_staff = None
    else:
        headCount = headCount.replace('人', '')
        staffarr = headCount.split('-')
        if len(staffarr) > 1:
            min_staff = staffarr[0]
            max_staff = staffarr[1]
        else:
            min_staff = staffarr[0]
            max_staff = None

    source_company = {"name": name,
                      "fullName": fullName,
                      "description": desc,
                      "brief": brief,
                      "round": stage,
                      "roundDesc": None,
                      "companyStatus": 2010,
                      'fundingType':funding_type,
                      "locationId": location_id,
                      "address": address,
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

    parser_job(company_key, source_company_id)


    #
    # msg = {"type":"company", "id":source_company_id}
    # kafka_producer.send_messages("parser_v2", json.dumps(msg))


def parser_job(company_key, source_company_id):
    jobs = fromdb.job.find({"source": source, "company_key":company_key})
    for job in jobs:
        job_key = job["job_key"]
        job_content = job["content"]

        born_time = job_content["ctime"]
        position = job_content["name"]

        city = job_content["city_name"]
        desc = job_content["description"]
        salary_min = job_content["salary_min"]
        salary_max = job_content["salary_max"]
        salary = str(salary_min)+'-'+ str(salary_max)+'k'

        education = job_content["min_degree"]
        work_year = job_content["min_experience"]
        update_time = job_content["refresh_time"]

        city = city.replace('市', '')
        location_id = parser_util.get_location_id(city)

        education_type = 0
        education = int(education)
        if education == 1:
            education_type = 6020
        elif education == 2:
            education_type = 6030
        elif education == 3:
            education_type = 6040
        elif education == 4:
            education_type = 6050

        workYear_type = 7000
        work_year = int(work_year)
        if work_year == 1:
            workYear_type = 7010
        elif work_year == 2:
            workYear_type = 7020
        elif work_year == 3:
            workYear_type = 7030
        elif work_year == 4:
            workYear_type = 7040
        elif work_year == 5:
            workYear_type = 7050
        elif work_year == 6:
            workYear_type = 7060

        domain = 0

        born_time = datetime.datetime.fromtimestamp(int(born_time)).strftime('%Y-%m-%d %H:%M:%S')
        update_time = datetime.datetime.fromtimestamp(int(update_time)).strftime('%Y-%m-%d %H:%M:%S')

        source_job = {
                    "sourceId": job_key,
                    "sourceCompanyId": source_company_id,
                    "position": position,
                    "salary": salary,
                    "description": desc,
                    "domain": domain,
                    "locationId": location_id,
                    "educationType": education_type,
                    "workYearType": workYear_type,
                    "startDate": born_time,
                    "updateDate": update_time,
                    }

        parser_util.insert_source_job(source_job)


if __name__ == '__main__':
    (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("recruit_jobtong", "crawler_recruit_jobtong")

    while True:
        try:
            for message in kafka_consumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                               message.offset, message.key,
                                                               message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    company_key = msg["company_key"]

                    if type == "company":
                        parse_company(company_key)

                    # kafka_consumer.task_done(message)
                    # kafka_consumer.commit()
                except Exception,e :
                    logger.error(e)
                    traceback.print_exc()
        except Exception,e :
            logger.error(e)
            traceback.print_exc()
            time.sleep(60)
            (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("recruit_jobtong", "crawler_recruit_jobtong")
