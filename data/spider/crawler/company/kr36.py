# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer)

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import util

#logger
loghelper.init_logger("kr36_spider", stream=True)
logger = loghelper.get_logger("kr36_spider")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)

#kafka
(kafka_url) = config.get_kafka_config()
kafka = KafkaClient(kafka_url)
# HashedPartitioner is default
kafka_producer = SimpleProducer(kafka)

#
company_collection = mongo.crawler_v2.company
company_collection.create_index([("source", pymongo.DESCENDING), ("company_key", pymongo.DESCENDING)], unique=True)
member_collection = mongo.crawler_v2.member
member_collection.create_index([("source", pymongo.DESCENDING), ("member_key", pymongo.DESCENDING)], unique=True)
news_collection = mongo.crawler_v2.news
news_collection.create_index([("source", pymongo.DESCENDING),("company_key", pymongo.DESCENDING),("news_key", pymongo.DESCENDING)], unique=True)
investor_collection = mongo.crawler_v2.investor
investor_collection.create_index([("source", pymongo.DESCENDING), ("investor_key", pymongo.DESCENDING)], unique=True)

#
source = 13020

#################################################
def fetch_company(url):
    (company_key, ) = util.re_get_result("http://rong.36kr.com/api/company/(\d+)", url)
    logger.info("company_key=%s" % company_key)

    company_content = None
    member_contents = []
    news_contents = []
    investor_contents = []
    member_ids = []

    #company base info
    time.sleep(5)
    (flag, r) = my_request.get(logger, url)
    if flag == -1:
        return -1

    if r.status_code == 404:
        logger.info("Page Not Found!!!")
        return r.status_code

    if r.status_code != 200:
        logger.info("status_code=%d" % r.status_code)
        return r.status_code

    company_base = r.json()
    logger.info(company_base)

    if company_base["code"] != 0:
        return 404

    logger.info(company_base["data"]["company"]["name"])

    #past-finance (investment events)
    url = "http://rong.36kr.com/api/company/%s/past-finance" % company_key
    time.sleep(5)
    (flag, r) = my_request.get(logger, url)
    if flag == -1:
        return -1
    past_finance = r.json()

    #past-investor
    url = "http://rong.36kr.com/api/company/%s/past-investor?pageSize=100" % company_key
    time.sleep(5)
    (flag, r) = my_request.get(logger, url)
    if flag == -1:
        return -1
    past_investor = r.json()

    #funds (非投资人没有查看权限)
    url = "http://rong.36kr.com/api/company/%s/funds" % company_key
    time.sleep(5)
    (flag, r) = my_request.get(logger, url)
    if flag == -1:
        return -1
    funds = r.json()

    #product
    url = "http://rong.36kr.com/api/company/%s/product" % company_key
    time.sleep(5)
    (flag, r) = my_request.get(logger, url)
    if flag == -1:
        return -1
    product = r.json()

    #past-investment
    url = "http://rong.36kr.com/api/company/%s/past-investment" % company_key
    time.sleep(5)
    (flag, r) = my_request.get(logger, url)
    if flag == -1:
        return -1
    past_investment = r.json()

    #company-fa?
    url ="http://rong.36kr.com/api/fa/company-fa?cid=%s" % company_key
    time.sleep(5)
    (flag, r) = my_request.get(logger, url)
    if flag == -1:
        return -1
    company_fa = r.json()

    #founders
    url = "http://rong.36kr.com/api/company/%s/founder?pageSize=1000" % company_key
    time.sleep(5)
    (flag, r) = my_request.get(logger, url)
    if flag == -1:
        return -1
    founders = r.json()

    #employee
    url ="http://rong.36kr.com/api/company/%s/employee?pageSize=1000" % company_key
    time.sleep(5)
    (flag, r) = my_request.get(logger, url)
    if flag == -1:
        return -1
    employees = r.json()

    #former-member
    url = "http://rong.36kr.com/api/company/%s/former-member?pageSize=1000" % company_key
    time.sleep(5)
    (flag, r) = my_request.get(logger, url)
    if flag == -1:
        return -1
    former_members = r.json()

    company_content = {"date":datetime.datetime.now(), "source":source, "url":url, "company_key":company_key,
                       "company_key_int":int(company_key),
                       "company_base":company_base,
                       "past_finance":past_finance,
                       "past_investor":past_investor,
                       "funds":funds,
                       "product":product,
                       "past_investment":past_investment,
                       "company_fa":company_fa,
                       "founders":founders,
                       "employees":employees,
                       "former_members":former_members}

    #member
    for m in founders["data"]["data"]:
        m_id = m["id"]
        member_ids.append(m_id)
    for m in employees["data"]["data"]:
        m_id = m["id"]
        member_ids.append(m_id)
    for m in former_members["data"]["data"]:
        m_id = m["id"]
        member_ids.append(m_id)
    for v in past_investor["data"]["data"]:
        if v["entityType"] == "INDIVIDUAL":
            m_id = v["entityId"]
            member_ids.append(m_id)

    for m_id in member_ids:
        member_key = str(m_id)

        if member_collection.find_one({"source":source, "member_key":member_key}):
            continue

        #basic
        url = "http://rong.36kr.com/api/user/%s/basic" % member_key
        time.sleep(5)
        (flag, r) = my_request.get(logger, url)
        if flag == -1:
            return -1
        member_base = r.json()

        #past-investment
        url = "http://rong.36kr.com/api/user/%s/past-investment" % member_key
        time.sleep(5)
        (flag, r) = my_request.get(logger, url)
        if flag == -1:
            return -1
        member_past_investment = r.json()

        #
        url = "http://rong.36kr.com/api/user/%s/company" % member_key
        time.sleep(5)
        (flag, r) = my_request.get(logger, url)
        if flag == -1:
            return -1
        member_company = r.json()

        #
        url = "http://rong.36kr.com/api/user/%s/work" % member_key
        time.sleep(5)
        (flag, r) = my_request.get(logger, url)
        if flag == -1:
            return -1
        member_work = r.json()

        #
        url = "http://rong.36kr.com/api/p/lead-investor/%s/financing" % member_key
        time.sleep(5)
        (flag, r) = my_request.get(logger, url)
        if flag == -1:
            return -1
        member_financing = r.json()

        member_content = {"date":datetime.datetime.now(), "source":source, "url":url, "member_key":member_key,
                          "member_base":member_base,
                          "member_past_investment":member_past_investment,
                          "member_company":member_company,
                          "member_work":member_work,
                          "member_financing":member_financing}
        member_contents.append(member_content)

    #investor organization
    for e in past_finance["data"]["data"]:
        for investor in e.get("participants",{}):
            investor_key = str(investor["entityId"])

            if investor_collection.find_one({"source":source, "investor_key":investor_key}):
                continue

            #base info
            url = "http://rong.36kr.com/api/organization/%s/basic" % investor_key
            time.sleep(5)
            (flag, r) = my_request.get(logger, url)
            if flag == -1:
                return -1
            investor_base = r.json()

            #staffs
            url = "http://rong.36kr.com/api/organization/%s/user" % investor_key
            time.sleep(5)
            (flag, r) = my_request.get(logger, url)
            if flag == -1:
                return -1
            staffs = r.json()

            #former-member
            url = "http://rong.36kr.com/api/organization/%s/former-member" % investor_key
            time.sleep(5)
            (flag, r) = my_request.get(logger, url)
            if flag == -1:
                return -1
            former_members = r.json()

            investor_content = {"date":datetime.datetime.now(), "source":source, "url":url, "investor_key":investor_key,
                                "investor_base":investor_base,
                                "staffs":staffs,
                                "former_members":former_members}

            investor_contents.append(investor_content)

    #logger.info(company_content)
    #logger.info("************")
    #logger.info(member_contents)
    #logger.info("************")
    #logger.info(investor_contents)

    #save
    if company_collection.find_one({"source":source, "company_key":company_key}) != None:
        company_collection.delete_one({"source":source, "company_key":company_key})
    company_collection.insert_one(company_content)

    for member in member_contents:
        if member_collection.find_one({"source":source, "member_key":member["member_key"]}) == None:
            member_collection.insert_one(member)

    for news in news_contents:
        if news_collection.find_one({"source":source, "company_key":company_key, "news_key":news["news_key"]}) == None:
            news_collection.insert_one(news)

    for investor in investor_contents:
        if investor_collection.find_one({"source":source, "investor_key":investor["investor_key"]}) == None:
            investor_collection.insert_one(investor)

    msg = {"type":"company", "source":source, "company_key":company_key}
    logger.info(json.dumps(msg))
    kafka_producer.send_messages("crawler_kr36_v2", json.dumps(msg))

    return 200


login_users = [
    {"name":"daffy@mailinator.com", "pwd":"daffy123"},
    {"name":"minnie@mailinator.com", "pwd":"minnie"},
    {"name":"elmer@mailinator.com", "pwd":"elmer123"},
    {"name":"tweety@mailinator.com", "pwd":"tweety"},
    {"name":"alfonse@mailinator.com", "pwd":"alfonse"}
]

'''
http://passport.36kr.com/passport/sign_in
type=login&bind=false&needCaptcha=false&username=daffy%40mailinator.com&password=daffy123&ok_url=
Content-Type  application/x-www-form-urlencoded
Referer     http://passport.36kr.com

https://passport.36kr.com/pages/?ok_url=%2Foauth%2Fauthorize%3Fclient_id%3Dd80f4c1aaba936ced68ebac474a68ce6c2ca2d6ae346d8232ccf6b9c573f9bb7%26redirect_uri%3Dhttps%253A%252F%252Frong.36kr.com%252Foauth%252Fcallback%26response_type%3Dcode%26state%3Dhttp%253A%252F%252F36kr.com%252F&from=rong#/login
'''

def login():
    while True:
        idx = random.randint(0, len(login_users)-1)
        login_user = login_users[idx]
        logger.info(login_user)

        s = my_request.get_http_session(new=True, agent=False)
        data = {
            "type":"login",
            "bind":False,
            "needCaptcha":False,
            "username":login_user["name"],
            "password":login_user["pwd"],
            "ok_url":"/"

        }
        headers = {
            "Referer":"http://passport.36kr.com"
        }

        try:
            r = s.post("http://passport.36kr.com/passport/sign_in",data=data, headers=headers, timeout=10)
            logger.info(r.text)
        except:
            continue

        if r.status_code != 200:
            continue

        if r.text.strip() != '{"redirect_to":"/"}':
            continue

        (flag, r) = my_request.get(logger,"http://uc.36kr.com/api/user/identity")
        if flag == 0 and r is not None and r.status_code==200:
            result = r.json()
            logger.info(result)
            if result["code"] == 4031:
                break


if __name__ == "__main__":
    logger.info("Start...")

    flag = "incr"
    if len(sys.argv) > 1:
        flag = sys.argv[1]

    cnt = 0
    i = 0

    if flag == "incr":
        latest_company = company_collection.find({"source":source}).sort("company_key_int", pymongo.DESCENDING).limit(1)
        if latest_company.count() > 0:
            i = latest_company[0]["company_key_int"]

    latest = i
    logger.info("From: %d" % i)

    while True:
        i += 1
        url = "http://rong.36kr.com/api/company/%d" % (i)

        if cnt <= 0:
            login()
            cnt = 100

        status = -1
        retry_times = 0
        while status != 200 and status !=404:
            cnt -= 1
            try:
                status = fetch_company(url)
            except Exception,ex:
                logger.exception(ex)
                #exit(0)

            if status == -1 or status == 403:
                login()
                cnt = 100

            retry_times += 1
            if retry_times >= 3:
                break

        if status == 200:
            latest = i

        if flag == "incr":
            if latest < i - 100:
                break
        else:
            if latest < i - 100:
                break

        #no data in this range
        if i > 35395 and i < 130721:
            i = 130721
            latest = i