#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import datetime
import random
import json
import lxml.html
import pymongo


reload(sys)
sys.setdefaultencoding("utf-8")
import my_request
import util
import spider_util


source = 13052
#################################################
def fetch_company(url):
    (company_key, ) = util.re_get_result("http://www.jobtong.com/e/(\d+)", url)

    if company_collection.find_one({"source":source, "company_key":company_key}) != None:
        return 200

    logger.info("company_key=%s" % company_key)

    (flag, r) = my_request.get(logger, url)
    logger.info("flag=%d", flag)

    if flag == -1:
        return -1

    if r.status_code == 404:
        logger.info("Page Not Found!!!")
        return r.status_code

    if r.status_code != 200:
        return r.status_code

    if r.url != url:
        logger.info("Page Redirect <--")
        return 302

    company_content = {"date":datetime.datetime.now(), "source":source, "url":url,
                       "company_key":company_key, "company_key_int":int(company_key), "content":r.text}

    doc = lxml.html.fromstring(r.text)

    #company invalid

    #job
    job_contents = get_job(company_key, 1)

    if len(job_contents) > 0:
        #save
        if company_collection.find_one({"source":source, "company_key":company_key}) != None:
            company_collection.delete_one({"source":source, "company_key":company_key})
        company_collection.insert_one(company_content)

        for job in job_contents:
            if job_collection.find_one({"source":source, "company_key":company_key, "news_key":job["job_key"]}) == None:
                job_collection.insert_one(job)

        msg = {"type":"company", "source":source, "company_key":company_key}
        logger.info(json.dumps(msg))
        kafka_producer.send_messages("crawler_recruit_jobtong", json.dumps(msg))
        return 200

    else:
        return 302




def get_job(company_key, page_no):
    job_contents = []
    items = ['1']
    while len(items) > 0 and page_no < 10:
        job_url = "http://www.jobtong.com/api/enterprises/%s/jobs?page=%s" % (company_key, page_no)
        logger.info(job_url)
        (flag, r) = my_request.get(logger, job_url)
        if flag == 0:
            job_data = json.loads(r.text)
            job_result = job_data['items']
            if len(job_result) > 0:
                for job in job_result:
                    job_content = {"date":datetime.datetime.now(), "source":source, "company_key":company_key,"job_key":job['id'], "content": job}
                    job_contents.append(job_content)
            items = job_result
            page_no += 1

    return job_contents


if __name__ == "__main__":
    (logger, mongo, kafka_producer, company_collection, member_collection, news_collection, job_collection) \
        = spider_util.spider_recruit_init('recruit_jobtong')

    type = ''
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            type = 'all'
        else:
            type = 'incr'
    else:
        type = 'incr'

    cnt = 0
    latest_company = company_collection.find({"source":source}).sort("company_key_int", pymongo.DESCENDING).limit(1)
    if latest_company.count() == 0:
        i = 0
    else:
        i = int(latest_company[0]["company_key_int"])
    latest = i
    logger.info("From: %d" % i)

    while True:
        i += 1
        url = "http://www.jobtong.com/e/%d" % (i)

        if cnt <= 0:
            proxy = {'type': 'http', 'anonymity':'high', 'country': 'cn', 'ping': 5}
            my_request.get_single_session(proxy, new=True, agent=False)
            cnt = 100

        status = -1
        retry_times = 0
        while status != 200 and status !=404 and status != 302:
            try:
                status = fetch_company(url)
            except Exception,ex:
                logger.exception(ex)

            if status == -1:
                my_request.get_http_session(new=True, agent=False)
                cnt = 100

            retry_times += 1
            if retry_times >= 3:
                break

        cnt -= 1

        if status == 200:
            latest = i

        if latest < i - 10000:
            break
