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
import time
from pyquery import PyQuery as pq



source = 13020
#################################################
def fetch_cf(data):
    # sleep_time = random.randint(10, 30)
    # time.sleep(sleep_time)

    cf_key = data['id']
    company_key = data['company_id']


    logger.info("cf_key=%s" % cf_key)

    url = 'https://rong.36kr.com/company/'+str(company_key)+'/crowFunding?fundingId='+str(cf_key)

    (flag, r) = my_request.get(logger, url)
    logger.info("flag=%d", flag)

    if flag == -1:
        return -1

    if r.status_code == 404:
        return r.status_code

    if r.status_code != 200:
        return r.status_code

    html = r.text

    finance = fetch_finance(company_key)
    crowdfunding = fetch_crowdfunding(cf_key)
    overview = fetch_rong_overview(company_key)
    # header = fetch_rong_header()
    qichacha =fetch_qichacha(company_key)
    founder = fetch_founder(company_key)
    status = fetch_status(company_key)

    content = {'html': html,
               'finance': finance,
               'crowdfunding': crowdfunding,
               'overview': overview,
               # 'header': header,
               'qichacha': qichacha,
               'founder': founder,
               'status': status
               }

    cf_content = {"date":datetime.datetime.now(),
                   "source":source,
                   "url":url,
                   "company_key":company_key,
                   "cf_key":cf_key,
                   "content":content
                   }

    result = cf_collection.find_one({"source":source, "company_key":company_key, 'cf_key': cf_key})
    if result != None:
        cf_collection.replace_one({'_id': result['_id']}, cf_content)
    else:
        cf_collection.insert_one(cf_content)

    msg = {"type":"cf", "source":source, "cf_key":cf_key}
    logger.info(json.dumps(msg))
    kafka_producer.send_messages("crawler_cf_36kr_v2", json.dumps(msg))

def fetch_finance(company_key):
    url = 'https://rong.36kr.com/api/company/'+str(company_key)+'/finance'
    (flag, r) = my_request.get(logger, url)
    if flag == 0:
        finance = json.loads(r.text)

    return finance


def fetch_crowdfunding(cf_key):
    url = 'https://rong.36kr.com/api/p/crowd-funding/'+str(cf_key)
    (flag, r) = my_request.get(logger, url)
    if flag == 0:
        crowdfunding = json.loads(r.text)

    return crowdfunding

def fetch_rong_overview(company_key):
    url = 'https://rong.36kr.com/api/p/sm/seo/summary/rong-company-overview/'+str(company_key)
    (flag, r) = my_request.get(logger, url)
    if flag == 0:
        overview = json.loads(r.text)

    return overview

def fetch_rong_header():
    url = 'https://rong.36kr.com/api/p/sm/seo/fragment/header-footer'
    (flag, r) = my_request.get(logger, url)
    if flag == 0:
        header = json.loads(r.text)

    return header



def fetch_qichacha(company_key):
    url = 'https://rong.36kr.com/api/company/'+str(company_key)+'/qichacha'
    (flag, r) = my_request.get(logger, url)
    if flag == 0:
        qichacha = json.loads(r.text)

    return qichacha



def fetch_founder(company_key):
    url = 'https://rong.36kr.com/api/company/'+str(company_key)+'/founder?pageSize=1000'
    (flag, r) = my_request.get(logger, url)
    if flag == 0:
        founder = json.loads(r.text)

    return founder


def fetch_status(company_key):
    url = 'https://rong.36kr.com/api/company/'+str(company_key)
    (flag, r) = my_request.get(logger, url)
    if flag == 0:
        status = json.loads(r.text)

    return status


def login():
    retry_times = 0
    login_user = {"name":"18911544075", "pwd":"Tomorrow9"}
    # login_user = {"name":"18605104197", "pwd":"wang2857"}
    while True:
        try:
            s = my_request.get_agent_session()
            r = s.post("https://passport.36kr.com/passport/sign_in",
                       data={"type":"login",
                             "username":login_user["name"],
                             "password":login_user["pwd"]},
                       timeout=10)
            logger.info(r.text)
            result = json.loads(r.text)
            if result["redirect_to"] == '/':
                return True
        except Exception,ex:
            logger.exception(ex)
            time.sleep(60)

    return False


if __name__ == "__main__":
    (logger, mongo, kafka_producer, company_collection, member_collection, news_collection, cf_collection) \
        = spider_util.spider_cf_init('jd')


    login()

    flag = True
    while flag:
        i = 1
        url = 'https://rong.36kr.com/api/p/crowd-funding?page='+str(i)+'&per_page=100&status=all'
        (flag, r) = my_request.get(logger, url)
        if flag ==0:
            data = json.loads(r.text)
            data = data['data']
            last_page = data['last_page']
            if last_page > 1:
                for i in xrange(0, last_page):
                    url = 'https://rong.36kr.com/api/p/crowd-funding?page='+str(i)+'&per_page=100&status=all'
                    (flag, r) = my_request.get(logger, url)
                    if flag == 0:
                        data = json.loads(r.text)['data']['data']
                        for d in data:
                            fetch_cf(d)
                flag = False
            else:
                for d in data['data']:
                    fetch_cf(d)

                flag = False






    # login()
