# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer)

from pyquery import PyQuery as pq
import datetime, time
import json, re
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import spider_util, util,  parser_util
import proxy_pool
import db, config
import loghelper


#logger
loghelper.init_logger("lagou_trends", stream=True)
logger = loghelper.get_logger("lagou_trends")

cnt = 0
total = 0

SOURCE = 13050

def request(url, callback):
    global total
    proxy = {'type': 'http', 'anonymity':'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)

    http_client.fetch(url, callback, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),request_timeout=10)

def handle_result(response, source_company):
    global total
    if response.error:
        # logger.info("Error: %s, %s" % (response.error,response.request.url))
        url = "http://www.lagou.com/gongsi/searchPosition.json?companyId=%s&pageSize=1000" % source_company['sourceId']
        request(url, lambda r,source_company=source_company:handle_result(r, source_company))
        return
    try:
        result = json.loads(response.body)
        job_result = result['content']['data']['page']['result']
        if len(job_result) > 0:
            for job in job_result:
                parser_job(source_company, job)
    except:
        traceback.print_exc()

    total -= 1
    if total <= 0:
        begin()


def parser_job(source_company, job_content):

    positionId = job_content['positionId']
    born_time = job_content["bornTime"]
    position = job_content["positionName"]
    education = job_content["education"]
    city = job_content["city"]
    # keywords = job_content["keyWords"]
    salary = job_content["salary"]
    work_year = job_content["workYear"]
    position_type = job_content["positionFirstType"]
    update_time = job_content["createTime"]


    location_id = parser_util.get_location_id(city)

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
        born_time = date+ ' '+ born_time.strip()
    if '-' not in update_time and update_time != None:
        update_time = date+ ' '+ update_time.strip()

    source_job = {
                "sourceId": positionId,
                "sourceCompanyId": source_company['id'],
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

    parser_util.insert_source_job(source_job)
    if source_company['companyId'] is not None:
        save_job(source_company['companyId'], source_job)


def save_job(company_id, job):
    conn = db.connect_torndb()
    sql = 'select * from job where companyId=%s and position=%s  and startDate=%s'
    result = conn.get(sql, company_id, job['position'], job['startDate'])
    if result is None:
        sql = 'insert job(companyId, position, salary, description, domain,' \
              ' locationId, educationType, workYearType, startDate, updateDate,' \
              'createTime) values(' \
              '%s, %s, %s, %s, %s,' \
              '%s, %s, %s, %s, %s,' \
              'now())'
        job_id = conn.insert(sql, company_id, job['position'], job['salary'], job['description'], job['domain'],
                job['locationId'], job['educationType'], job['workYearType'], job['startDate'], job['updateDate'])
    else:
        job_id = result['id']
        sql = 'update job set updateDate = %s where id =%s'
        conn.update(sql, result['updateDate'], job_id)

    # conn.update('update source_job set jobId = %s where id=%s', job_id, job['id'])
    conn.close()


def begin():
    global total, cnt
    conn = db.connect_torndb()

    source_companies = conn.query("select * from source_company where source=13050 order by id desc limit %s,1000", cnt)
    if len(source_companies) == 0:
        logger.info("Finish.")
        exit()

    for source_company in source_companies:
        cnt += 1
        total += 1
        url = "http://www.lagou.com/gongsi/searchPosition.json?companyId=%s&pageSize=1000" % source_company['sourceId']
        request(url, lambda r,source_company=source_company:handle_result(r, source_company))
    conn.close()


if __name__ == "__main__":
    logger.info("Start...")

    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()