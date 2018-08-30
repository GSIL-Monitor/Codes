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


source = 13051
#################################################
def fetch_job(url):

    urlarr = url.split("=")
    job_key = urlarr[len(urlarr)-1]
    logger.info("job_key=%s" % job_key)

    (flag, r) = my_request.get(logger, url)
    logger.info("flag=%d", flag)

    if flag == -1:
        return -1

    if r.status_code == 404:
        logger.info("Page Not Found!!!")
        return r.status_code

    if r.status_code != 200:
        #logger.info(r.status_code)
        return r.status_code

    if r.url != url:
        logger.info("Page Redirect <--")
        return 302

    doc = lxml.html.fromstring(r.text)
    company_url = doc.xpath('//div[@class="c_name"]/a/@href')
    if len(company_url) == 0:
        return 200

    company_url = company_url[0]
    (company_key,) = util.re_get_result("/company/detail/domain=(\S+).html", company_url)
    logger.info(company_key)

    job_content = {"date":datetime.datetime.now(), "source":source, "url":url,
                   "company_key": company_key, "job_key": int(job_key), "content":r.text}


    result = job_collection.find_one({"source":source, "company_key":company_key, "job_key": job_key})
    if result == None:
        job_collection.insert_one(job_content)
    # else:
    #     job_collection.replace_one({"_id":result["_id"]}, job_content)

    if company_collection.find_one({"source":source, "company_key":company_key}) == None:
        company_url =  'http://www.neitui.me/'+company_url
        (flag, r) = my_request.get(logger, company_url)
        if flag == -1:
            return -1
        company_content = {"date":datetime.datetime.now(), "source":source, "url":company_url, "company_key":company_key, "content":r.text}
        company_collection.insert_one(company_content)


    msg = {"type":"job", "source":source, "job_key":job_key}
    logger.info(json.dumps(msg))
    kafka_producer.send_messages("crawler_recruit_neitui", json.dumps(msg))

    return 200

if __name__ == "__main__":
    (logger, mongo, kafka_producer, company_collection, member_collection, news_collection, job_collection) \
        = spider_util.spider_recruit_init('recruit_neitui')

    type = ''
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            type = 'all'
        else:
            type = 'incr'
    else:
        type = 'incr'

    cnt = 0
    latest_job = job_collection.find({"source":source}).sort("job_key", pymongo.DESCENDING).limit(1)
    if latest_job.count() == 0:
        i = 0
    else:
        i = int(latest_job[0]["job_key"])
    latest = i
    logger.info("From: %d" % i)

    while True:
        i += 1
        url = "http://www.neitui.me/?name=job&handle=detail&id=%d" % (i)

        if cnt <= 0:
            proxy = {'type': 'http', 'anonymity':'high', 'country': 'cn', 'ping': 5}
            my_request.get_single_session(proxy, new=True, agent=False)
            cnt = 100

        status = -1
        retry_times = 0
        while status != 200 and status !=404 and status != 302:
            try:
                status = fetch_job(url)
                #logger.info("status=%s" % status)
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


        if latest < i - 1000:
            break
