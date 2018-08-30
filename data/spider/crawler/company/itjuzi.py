# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer)
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import util
import db

#logger
loghelper.init_logger("itjuzi_spider", stream=True)
logger = loghelper.get_logger("itjuzi_spider")

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
source = 13030

#################################################
def fetch_company(url):
    (company_key, ) = util.re_get_result("http://www.itjuzi.com/company/(\d+)", url)
    logger.info("company_key=%s" % company_key)

    company_content = None
    member_contents = []
    news_contents = []
    investor_contents = []

    (flag, r) = my_request.get(logger, url)
    logger.info("flag=%d", flag)
    if flag == -1:
        return -1

    logger.info("status=%d", r.status_code)

    if r.status_code == 404:
        logger.info("Page Not Found!!!")
        return r.status_code

    if r.status_code != 200:
        #logger.info(r.status_code)
        return r.status_code

    #logger.info(r.text)
    d = pq(r.text)
    product_name = d('div.line-title> span> b').clone().children().remove().end().text().strip()
    if product_name == "":
        return 404

    company_content = {"date":datetime.datetime.now(), "source":source, "url":url, "company_key":company_key, "company_key_int":int(company_key) ,"content":r.text}

    #members
    lis = d('h4.person-name> a.title')
    for li in lis:
        try:
            l = pq(li)
            href = l.attr("href").strip()
            logger.info(href)
            member_name = l('b> span.c').text().strip()
            (member_key,) = util.re_get_result(r'http://www.itjuzi.com/person/(\d*?)$',href)
            logger.info("member_key=%s, member_name=%s" % (member_key, member_name))

            href = href.replace("http://","https://")
            #if member_collection.find_one({"source":source, "member_key":member_key}) == None:
            if 1 == 1:
                flag = -1
                while flag!=0:
                    (flag, r) = my_request.get(logger, href)
                    if flag==0 and r.status_code != 200:
                        flag = -1
                    if flag != 0:
                        my_request.get_https_session(new=True, agent=True)
                #logger.info(r.text)
                member_contents.append({"date":datetime.datetime.now(), "source":source, "url":url, "member_key":member_key,
                                        "member_name":member_name, "content":r.text})
        except Exception,ex:
            logger.exception(ex)

    #news
    lis = d('ul.list-news> li')
    for li in lis:
        try:
            l = pq(li)
            news_title = l('p.title> a').text().strip()
            news_url = l('p.title> a').attr("href").strip()
            news_date_str = l('p> span.marr10').text().strip()
            news_source_domain = l('p> span.from').text().strip()
            (news_key,) = util.re_get_result(r"http://www.itjuzi.com/overview/news/(\d*)$", news_url)
            (news_year,news_month,news_day) = util.re_get_result(r'^(\d*)[^\d]*(\d*)[^\d]*(\d*)[^\d]*', news_date_str)
            logger.info(news_title)
            logger.info(news_url)
            logger.info(news_source_domain)
            logger.info(news_date_str)
            logger.info("%s-%s-%s" % (news_year,news_month,news_day))
            logger.info(news_key)

            if news_collection.find_one({"source":source, "company_key":company_key, "news_key":news_key}) == None:
                (flag, r) = my_request.get(logger, news_url)
                if flag == -1:
                    continue
                if r.status_code != 200:
                    continue
                #logger.info(r.text)
                f = pq(r.text)
                url = f('iframe').attr("src").strip()
                (flag, r) = my_request.get_no_sesion(logger, url)
                if flag == -1:
                    continue
                if r.status_code != 200:
                    continue
                #logger.info(r.text)

                news_contents.append({"date":datetime.datetime.now(), "source":source, "url":url, "company_key":company_key, "news_key":news_key,
                                      "news_title":news_title,"news_date":"%s/%s/%s" % (news_year,news_month,news_day),
                                      "news_url":news_url, "news_source_domain":news_source_domain, "content":r.text})
        except Exception,ex:
            logger.exception(ex)

    #investors
    lis = d('table.list-round-v2 >tr > td> a')
    if len(lis) > 0:
        my_request.get_https_session(new=True, agent=True)
    for li in lis:
        try:
            l = pq(li)
            investor_url = l.attr('href').strip()
            investor_name = l.text().strip()
            (investor_key,) = util.re_get_result(r"http://www.itjuzi.com/investfirm/(\d*)$", investor_url)
            logger.info(investor_url)
            logger.info(investor_name)
            logger.info(investor_key)
            #if investor_collection.find_one({"source":source, "investor_key":investor_key}) == None:
            investor_url = investor_url.replace("http://","https://")
            if 1 == 1:
                flag = -1
                while flag!=0:
                    (flag, r) = my_request.get(logger, investor_url)
                    if flag==0 and r.status_code != 200:
                        flag = -1
                    if flag != 0:
                        my_request.get_https_session(new=True, agent=True)
                #logger.info(r.text)
                investor_contents.append({"date":datetime.datetime.now(), "source":source, "url":investor_url, "investor_key":investor_key,
                                            "investor_name":investor_name, "content":r.text})

        except Exception,ex:
            logger.exception(ex)

    #save
    #logger.info(company_content)
    if company_collection.find_one({"source":source, "company_key":company_key}) != None:
        company_collection.delete_one({"source":source, "company_key":company_key})
    company_collection.insert_one(company_content)

    for member in member_contents:
        m = member_collection.find_one({"source":source, "member_key":member["member_key"]})
        if  m == None:
            member_collection.insert_one(member)
        else:
            member_collection.replace_one({"_id":m["_id"]}, member)

    for news in news_contents:
        if news_collection.find_one({"source":source, "company_key":company_key, "news_key":news["news_key"]}) == None:
            news_collection.insert_one(news)

    for investor in investor_contents:
        inv = investor_collection.find_one({"source":source, "investor_key":investor["investor_key"]})
        if inv == None:
            investor_collection.insert_one(investor)
        else:
            investor_collection.replace_one({"_id":inv["_id"]},investor)

    msg = {"type":"company", "source":source, "company_key":company_key}
    logger.info(json.dumps(msg))
    kafka_producer.send_messages("crawler_itjuzi_v2", json.dumps(msg))

    return 200


login_users = [
    {"name":"daffy@mailinator.com", "pwd":"daffy123"},
    {"name":"minnie@mailinator.com", "pwd":"minnie"},
    {"name":"elmer@mailinator.com", "pwd":"elmer123"},
    {"name":"tweety@mailinator.com", "pwd":"tweety"},
    {"name":"alfonse@mailinator.com", "pwd":"alfonse"}
]


def login():
    retry_times = 0

    while True:
        try:
            idx = random.randint(0, len(login_users)-1)
            login_user = login_users[idx]
            logger.info(login_user)


            flag = -1
            while flag != 0:
                s = my_request.get_https_session(new=True, agent=True)
                (flag,r) = my_request.get(logger, "https://www.itjuzi.com/user/login")
                logger.info(r.status_code)
                if flag == 0 and r.status_code != 200:
                    flag = -1
            logger.info(r.headers["Set-Cookie"])
            r = s.post("https://www.itjuzi.com/user/login",data={"identity":login_user["name"],"password":login_user["pwd"]}, timeout=10)
            logger.info(r.headers["Refresh"])
            if "0;url=https://www.itjuzi.com/"==r.headers["Refresh"]:
                return True
        except Exception,ex:
            logger.exception(ex)
            time.sleep(10)

        '''
        retry_times += 1
        if retry_times >=5:
            break
        '''

    return False


def fix():
    cnt = 0
    collection = mongo.crawler_v3.projectdata
    items = list(collection.find({"source":13030, "type":36002, "processed":{"$ne":True}}).sort("key_int", pymongo.ASCENDING))
    for item in items:
        key = item["key"]
        html = item["content"]
        d = pq(html)
        str = d("a.name").attr("href")
        if str is None:
            continue

        company_key = str.strip().split("/")[-1]

        conn = db.connect_torndb()
        source_company = conn.get("select * from source_company where source=%s and sourceId=%s", 13030, company_key)
        conn.close()

        if source_company is None:
            logger.info("company %s doesn't exist yet, key=%s", company_key, key)
            url = "http://www.itjuzi.com/company/%s" % company_key

            if cnt <= 0:
                if login() == False:
                    logger.info("Login Fail!")
                    exit(0)
                cnt = 10

            my_request.get_http_session(new=True, agent=True)

            status = -1
            while status != 200:
                try:
                    status = fetch_company(url)
                    #logger.info("status=%s" % status)
                    if status == 404:
                        break
                    if status != 200:
                        my_request.get_http_session(new=True, agent=True)
                except Exception,ex:
                    logger.exception(ex)



if __name__ == "__main__":
    logger.info("Start...")

    flag = "incr"
    if len(sys.argv) > 1:
        flag = sys.argv[1]

    if flag == "fix":
        fix()
        exit()

    cnt = 0
    i = 0

    if flag == "incr":
        latest_company = company_collection.find({"source":source}).sort("company_key_int", pymongo.DESCENDING).limit(1)
        if latest_company.count() > 0:
            i = latest_company[0]["company_key_int"]
    elif flag == "all":
        pass
    else:
        i = int(flag)

    latest = i
    logger.info("From: %d" % i)

    while True:
        i += 1
        #i=2 #test
        url = "http://www.itjuzi.com/company/%d" % (i)

        if cnt <= 0:
            if login() == False:
                logger.info("Login Fail!")
                exit(0)
            cnt = 10

        my_request.get_http_session(new=True, agent=True)

        status = -1
        while status != 200:
            try:
                status = fetch_company(url)
                #logger.info("status=%s" % status)
                if status == 404:
                    break
                if status != 200:
                    my_request.get_http_session(new=True, agent=True)
            except Exception,ex:
                logger.exception(ex)

        #cnt -= 1

        if status == 200:
            latest = i
            #exit(0) #test

        if flag == "incr":
            if latest < i - 100:
                break
        else:
            if latest < i - 2000:
                break

    logger.info("Finish.")
