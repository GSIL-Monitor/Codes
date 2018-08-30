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
import proxy_pool
import db, config, util
import loghelper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/recruit/lagou'))
import lagou_job_parser

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
import parser_db_util

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
        result = {}
        result["content"] = json.loads(response.body)
        #logger.info(result)
        source_jobs = lagou_job_parser.parse_companyjobs_save(source_company['id'], result)
        logger.info(json.dumps(source_jobs, ensure_ascii=False, cls=util.CJsonEncoder))
        if len(source_jobs) > 0:
            parser_db_util.save_jobs_standard(source_jobs)
            if source_company['companyId'] is not None:
                save_job(source_company['companyId'], source_jobs)
    except:
        traceback.print_exc()

    total -= 1
    if total <= 0:
        begin()
        #exit()

def save_job(company_id, jobs):
    conn = db.connect_torndb()
    for job in jobs:

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
    #source_companies = conn.query("select * from source_company where source=13050 and sourceId=40208")
    if len(source_companies) == 0:
        logger.info("Finish.")
        exit()

    for source_company in source_companies:
        cnt += 1
        total += 1
        logger.info("sourceId %s",source_company['sourceId'] )
        url = "http://www.lagou.com/gongsi/searchPosition.json?companyId=%s&pageSize=1000" % source_company['sourceId']
        request(url, lambda r,source_company=source_company:handle_result(r, source_company))
    conn.close()


if __name__ == "__main__":
    logger.info("Lagou job Start...")

    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()