# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html
from pymongo import MongoClient
import gridfs
import pymongo
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)
from tld import get_tld
from urlparse import urlsplit
import tldextract

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import util
import db
import extract

#logger
loghelper.init_logger("beian", stream=True)
logger = loghelper.get_logger("beian")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
fromdb = mongo.crawler_v2
imgfs = gridfs.GridFS(mongo.gridfs)

#mysql
conn = None

# kafka
kafkaProducer = None
kafkaConsumer = None


def initKafka():
    global kafkaProducer
    global kafkaConsumer

    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("parser_v2", group_id="beian",
                metadata_broker_list=[url],
                auto_offset_reset='smallest')


def get_main_beianhao(beianhao):
    strs = beianhao.split("-")
    if len(strs[-1]) <=3:
        del strs[-1]
    main_beianhao = "-".join(strs)
    return main_beianhao


def parse_query(source_company_id,html):
    doc = lxml.html.fromstring(html)
    dms = doc.xpath("//tr[@bgcolor='#FFFFFF']")
    for dm in dms:
        try:
            temps = dm.xpath("td")
            if len(temps) == 3:
                #未备案
                idx = temps[0].xpath("text()")[0].strip()
                domain_name = temps[1].xpath("a/text()")[0].strip()
                logger.info("%s 未备案", domain_name)
                domain = conn.get("select * from source_domain where domain=%s limit 1", domain_name)
                if domain is None:
                    conn.insert("insert source_domain(sourceCompanyId,domain,createTime,modifyTime) \
                                values(%s,%s,now(),now())",
                            source_company_id,domain_name)
                continue

            if len(temps) < 8:
                continue

            idx = temps[0].xpath("text()")[0].strip()
            domain_name = temps[1].xpath("a/text()")[0].strip()

            expire = 'N'
            dels = dm.xpath("td/del")
            if len(dels) >=6:
                expire = 'Y'

            if expire == 'N':
                temp = temps[2].xpath("a/font/text()")
                if len(temp) > 0:
                    organizer_name = temp[0].strip()
                else:
                    temp = temps[2].xpath("a/text()")
                    if len(temp) > 0:
                        organizer_name = temp[0].strip()
                organizer_type = temps[3].xpath("text()")[0].strip()
                beianhao = temps[4].xpath("a/text()")[0].strip()
                if beianhao == "":
                    beianhao = temps[4].xpath("a/font/text()")[0].strip() + temps[4].xpath("a/text()")[1].strip()
                website_name = temps[5].xpath("a/text()")[0].strip()
                website_homepage = temps[6].xpath("text()")[0].strip()
                review_date = temps[7].xpath("text()")[0].strip()
            else:
                organizer_name = dels[0].xpath("a/text()")[0].strip()
                organizer_type = dels[1].xpath("text()")[0].strip()
                beianhao = dels[2].xpath("a/text()")[0].strip()

                website_name = dels[3].xpath("a/text()")[0].strip()
                website_homepage = dels[4].xpath("text()")[0].strip()
                review_date = dels[5].xpath("text()")[0].strip()
            main_beianhao = get_main_beianhao(beianhao)
            organizer_name = util.norm_company_name(organizer_name)
            logger.info("%s, %s, %s, %s, %s, %s, %s, %s" %
                        (idx, domain_name, organizer_name, organizer_type, beianhao,website_name,website_homepage,review_date))

            domain = conn.get("select * from source_domain where domain=%s and organizer=%s limit 1", domain_name, organizer_name)
            if domain is None:
                conn.insert("insert source_domain(sourceCompanyId,domain,organizer,organizerType,\
                                        beianhao,mainBeianhao,websiteName,homepage,beianDate,expire,\
                                        createTime,modifyTime) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())",
                            source_company_id,domain_name,organizer_name,organizer_type,
                            beianhao,main_beianhao,website_name,website_homepage,review_date,expire
                            )
        except Exception,ex:
            logger.exception(ex)


def query_by_company_name(source_company_id, name):
    if name is None or name == "":
        return True

    #不是正常的中国公司名
    if name.find(".") != -1:
        return True

    result = conn.get("select count(*) cnt from source_domain where sourceCompanyId=%s", source_company_id)
    if result["cnt"] > 0:
        return True

    name = name.replace("_","")
    idx = name.rfind(u"公司")
    if idx != -1:
        name = name[:(idx+len(u"公司"))]

    #url = "http://beian.links.cn/beian.asp?beiantype=zbdwmc&keywords=%s" % name
    url = "http://beian.links.cn/zbdwmc_%s.html" % name
    (flag, r) = my_request.get(logger, url)
    #logger.info(r.text)
    if flag != 0 or r.status_code != 200:
        return False

    parse_query(source_company_id, r.text)

    return True


def query_by_domain(source_company_id, website):
    if website is None or website == "":
        return True

    s = urlsplit(website)
    if s.query != '' or s.fragment != '':
        return True
    if s.path != '' and s.path != '/':
        return True

    s = tldextract.extract(website)
    if s.subdomain != "www" and s.subdomain != "m" and s.subdomain != "":
        return True

    try:
        domain = get_tld(website)
    except:
        return True

    result = conn.get("select count(*) cnt from source_domain where sourceCompanyId=%s and domain=%s", source_company_id, domain)
    if result["cnt"] > 0:
        return True

    url = "http://beian.links.cn/beian.asp?beiantype=domain&keywords=%s" % domain
    (flag, r) = my_request.get(logger, url)
    #logger.info(r.text)
    if flag != 0 or r.status_code != 200:
        return False

    parse_query(source_company_id, r.text)

    return True


def query_by_beianhao(source_company_id, beianhao):
    if beianhao is None or beianhao == "":
        return True

    url = "http://beian.links.cn/beianhao_%s.html" % beianhao
    (flag, r) = my_request.get(logger, url)
    #logger.info(r.text)
    if flag != 0 or r.status_code != 200:
        return False

    parse_query(source_company_id, r.text)

    return True


def process(source_company_id):
    logger.info(source_company_id)
    source_company = conn.get("select * from source_company where id=%s", source_company_id)
    flag = query_by_company_name(source_company_id,source_company["fullName"])
    if flag == False:
        return False

    artifacts = conn.query("select * from source_artifact where sourceCompanyId=%s and type=4010", source_company_id)
    for artifact in artifacts:
        link = artifact["link"]
        logger.info(link)
        flag = query_by_domain(source_company_id, link)
        if flag == False:
            return False

    main_beianhaos = conn.query("select distinct mainBeianhao from source_domain where sourceCompanyId=%s", source_company_id)
    for main_beianhao in main_beianhaos:
        flag = query_by_beianhao(source_company_id,main_beianhao["mainBeianhao"])
        if flag == False:
            return False

    msg = {"type":"company", "id":source_company_id}
    kafkaProducer.send_messages("beian_v2", json.dumps(msg))

    return True

login_users = [
    {"name":"daffy","pwd":"daffy123456"}
]


def login():
    while True:
        try:
            idx = random.randint(0, len(login_users)-1)
            login_user = login_users[idx]
            logger.info(login_user)

            data = {
                    "backurl":"	http://beian.links.cn",
                    "bsave": "1",
                    "opaction":"login",
                    "username":login_user["name"],
                    "password":login_user["pwd"],}

            s = my_request.get_http_session(new=True, agent=False)
            logger.info("proxies=%s" % s.proxies)
            r = s.post("http://my.links.cn/checklogin.asp",data=data, timeout=10)
            if r.status_code == 200:
                #html = util.html_encode_4_requests(r.text, r.content, r.encoding)
                r.encoding = r.apparent_encoding
                html = r.text
                #logger.info(html)
                if html is not None:
                    if util.re_get_result(r"(loaduserinfo)",html):
                        return True
        except Exception,ex:
            logger.exception(ex)

        time.sleep(10)
    return False


if __name__ == '__main__':
    initKafka()

    #source_company_id = int(sys.argv[1])

    conn = db.connect_torndb()
    login()

    sc = conn.query("select * from source_company where source=13030 and companyId is null")
    for s in sc:
        source_company_id = s["id"]
        r = 0
        while True:
            flag = process(source_company_id)
            if flag == True:
                break
            else:
                login()
                flag = process(source_company_id)
            r +=1
            if r>10:
                break

    conn.close()
