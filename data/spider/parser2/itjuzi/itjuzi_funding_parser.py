# -*- coding: utf-8 -*-
import os, sys
import datetime, time
from pymongo import MongoClient
import pymongo
import json
from bson import json_util
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)
from pyquery import PyQuery as pq

import itjuzi_helper

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import db
import util

#logger
loghelper.init_logger("itjuzi_funding_parser", stream=True)
logger = loghelper.get_logger("itjuzi_funding_parser")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
collection = mongo.crawler_v3.projectdata

# kafka
kafkaProducer = None


SOURCE = 13030  #ITJUZI
TYPE = 36002    #融资事件

def initKafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)


def process():
    logger.info("itjuzi_funding_parser begin...")
    initKafka()

    items = collection.find({"source":SOURCE, "type":TYPE, "processed":{"$ne":True}}).sort("key_int", pymongo.ASCENDING)
    #items = collection.find({"source":SOURCE, "type":TYPE, "key_int":16220})
    for item in items:
        logger.info(item["url"])

        f = parse(item)
        if f is None:
            continue
        if f == -1:
            collection.update({"_id":item["_id"]},{"$set":{"processed":True}})
            continue

        flag, source_funding_id= save(f)

        if flag:
            collection.update({"_id":item["_id"]},{"$set":{"processed":True}})

        msg = {"type":"funding", "id":source_funding_id}

        flag = False
        while not flag:
            try:
                kafkaProducer.send_messages("parser_funding_v2", json.dumps(msg))
                flag = True
            except Exception,e :
                logger.exception(e)
                time.sleep(60)

        #break
    logger.info("itjuzi_funding_parser end.")


def save(f):
    flag = True #是否完全处理

    conn = db.connect_torndb()

    #TODO make sure they have same roundStr
    #source_funding = conn.get("select * from source_funding where sourceCompanyId=%s and roundDesc=%s", f["sourceCompanyId"], f["roundStr"])
    source_funding = conn.get("select * from source_funding where sourceCompanyId=%s and round=%s order by fundingDate limit 1", f["sourceCompanyId"], f["fundingRound"])

    if source_funding is None:
        source_funding_id = conn.insert("insert source_funding(sourceCompanyId,investment,round,roundDesc, currency, precise, fundingDate,createTime,modifyTime) \
                                        values(%s,%s,%s,%s,%s,%s,%s,now(),now())",
                                        f["sourceCompanyId"], f["investment"], f["fundingRound"], f["roundStr"],
                                        f["currency"], f["precise"],f["fundingDate"])
    else:
        source_funding_id = source_funding["id"]
        conn.update("update source_funding set investment=%s,currency=%s, precise=%s, fundingDate=%s, modifyTime=now() \
                    where id=%s",
                    f["investment"], f["currency"], f["precise"], f["fundingDate"], source_funding_id
                        )

    for investor in f["investors"]:
        source_investor_id = None
        if investor["key"] is None:
            source_investor = conn.get("select * from source_investor where source=%s and name=%s limit 1",
                                    SOURCE, investor["name"])
            if source_investor is None:
                sql = "insert source_investor(name,website,description,logo,stage,field,type, \
                    source,sourceId,createTime,modifyTime) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"
                source_investor_id = conn.insert(sql,
                    investor["name"],None,None,None,None,None,10020,SOURCE,None)
            else:
                source_investor_id = source_investor["id"]
        else:
            source_investor = conn.get("select * from source_investor where source=%s and sourceId=%s",
                                       SOURCE, investor["key"])
            if source_investor is not None:
                source_investor_id = source_investor["id"]

        if source_investor_id is None:
            flag = False
        else:
            source_funding_investor_rel = conn.get("select * from source_funding_investor_rel where \
                    sourceFundingId=%s and sourceInvestorId=%s",
                    source_funding_id, source_investor_id)
            if source_funding_investor_rel is None:
                conn.insert("insert source_funding_investor_rel(sourceFundingId, investorType, sourceInvestorId, \
                            createTime,modifyTime) \
                            values(%s,%s,%s, now(),now())", source_funding_id, investor["type"], source_investor_id)
    conn.close()

    return flag, source_funding_id

def parse(item):
    if item is None:
        return None

    company_key = item["key"]
    html = item["content"]
    #logger.info(html)
    d = pq(html)
    logger.info("*** funding ***")

    str = d("a.name").attr("href")
    if str is None:
        return -1

    company_key = str.strip().split("/")[-1]
    logger.info("company_key: %s", company_key)

    conn = db.connect_torndb()
    source_company = conn.get("select * from source_company where source=%s and sourceId=%s", SOURCE, company_key)
    conn.close()

    if source_company is None:
        logger.info("this source company doesn't exist yet")
        return None
    else:
        source_company_id = source_company["id"]
        logger.info("sourceComapnyId: %s", source_company_id)
        dateStr = d('div.block> div.titlebar-center> p> span.date').text().strip()
        result = util.re_get_result('(\d*?)\.(\d*?)\.(\d*?)$',dateStr)
        fundingDate = None
        if result != None:
            (year, month, day) = result
            y = int(year)
            if y >= 2100 and y <= 2109:
                year = 2010 + y%10
            m = int(month)
            if m > 12:
                m = 12
                month = "12"
            if (m==4 or m==6 or m==9 or m==11) and int(day)>30:
                day = "30"
            elif itjuzi_helper.isRunnian(int(year)) and m==2 and int(day)>29:
                day = 29
            elif itjuzi_helper.isRunnian(int(year)) == False and m==2 and int(day)>28:
                day = 28
            elif int(day) > 31:
                day = 31

            fundingDate = datetime.datetime.strptime("%s-%s-%s" % (year,month,day), '%Y-%m-%d')
        logger.info(fundingDate)

        roundStr = d('span.round').text().strip()
        fundingRound, roundStr = itjuzi_helper.getFundingRound(roundStr)
        logger.info("fundingRound=%d, roundStr=%s", fundingRound, roundStr)

        moneyStr = d('span.fina').text().strip()
        (currency, investment, precise) = itjuzi_helper.getMoney(moneyStr)
        logger.info("%s - %s - %s" % (currency, investment, precise))

        investors = []
        fs = d('h4.person-name> b >a.title')
        for f in fs:
            l = pq(f)
            investor_name = l.text().strip()
            if investor_name == "":
                continue
            investor_url = l.attr("href")
            if investor_url is not None and investor_url != "":
                investor_key = investor_url.strip().split("/")[-1]
                investor = {
                    "name":investor_name,
                    "key":investor_key,
                    "url":investor_url,
                    "type":38001
                }
                investors.append(investor)
                logger.info("Investor: %s, %s, %s", investor_key, investor_name, investor_url)
            else:
                investor_key = None
                temps = investor_name.split(";")
                for name in temps:
                    name = name.strip()
                    if name == "":
                        continue
                    investor = {
                        "name":name,
                        "key":None,
                        "url":None,
                        "type":38001
                    }
                    investors.append(investor)
                    logger.info("Investor: %s, %s, %s", investor_key, name, investor_url)

    return {
        "sourceCompanyId":source_company_id,
        "fundingDate":fundingDate,
        "fundingRound":fundingRound,
        "roundStr":roundStr,
        "currency":currency,
        "investment":investment,
        "precise":precise,
        "investors":investors
    }

    fundings = []
    # 并购信息
    lis = d('table.list-round> tr')
    for li in lis:
        l = pq(li)
        dateStr = l('td:eq(2)').text().strip()
        result = util.re_get_result('(\d*?)\.(\d*?)\.(\d*?)$',dateStr)
        fundingDate = None
        if result != None:
            (year, month, day) = result
            fundingDate = datetime.datetime.strptime("%s-%s-%s" % (year,month,day), '%Y-%m-%d')
        logger.info(fundingDate)

        roundStr = l('td.base> a> span').text().strip()
        fundingRound, roundStr = getFundingRound(roundStr)
        logger.info("fundingRound=%d, roundStr=%s", fundingRound, roundStr)

        moneyStr = l('td.base> a').clone().children().remove().end().text().strip()
        (currency, investment, precise) = getMoney(moneyStr)
        logger.info("%s - %s - %s" % (currency, investment, precise))

        funding = {
            "fundingDate":fundingDate,
            "fundingRound":fundingRound,
            "roundStr":roundStr,
            "currency":currency,
            "investment":investment,
            "precise": precise
        }

        investors = []
        hs = l('td.investor> a')
        for h in hs:
            h = pq(h)
            investor_name = h.text().strip()
            if investor_name == u"并购方未透露" or investor_name == u"未透露" or investor_name == "":
                continue
            investor_url = h.attr("href").strip()
            if investor_url is not None and investor_url != "":
                (investor_key,) = util.re_get_result(r"http://www.itjuzi.com/investfirm/(\d*)$", investor_url)
            else:
                investor_key = None
            logger.info("Investor: %s, %s, %s", investor_key, investor_name, investor_url)
            investor = {
                "name":investor_name,
                "key":investor_key,
                "url":investor_url,
                "type":38001
            }
            investors.append(investor)

        funding["investors"] = investors
        fundings.append(funding)

    # funding
    lis = d('table.list-round-v2> tr')
    for li in lis:
        l = pq(li)
        dateStr = l('td> span.date').text().strip()
        result = util.re_get_result('(\d*?)\.(\d*?)\.(\d*?)$',dateStr)
        fundingDate = None
        if result != None:
            (year, month, day) = result
            fundingDate = datetime.datetime.strptime("%s-%s-%s" % (year,month,day), '%Y-%m-%d')
        logger.info(fundingDate)

        roundStr = l('td.mobile-none> span.round> a').text().strip()
        fundingRound, roundStr = getFundingRound(roundStr)
        logger.info("fundingRound=%d, roundStr=%s", fundingRound, roundStr)

        moneyStr = l('td> span.finades> a').text().strip()
        (currency, investment, precise) = getMoney(moneyStr)
        logger.info("%s - %s - %s" % (currency, investment, precise))

        funding = {
            "fundingDate":fundingDate,
            "fundingRound":fundingRound,
            "roundStr":roundStr,
            "currency":currency,
            "investment":investment,
            "precise": precise
        }

        investors = []
        hs = l('td:eq(3)> a')
        for h in hs:
            h = pq(h)
            investor_name = h.text().strip()
            investor_url = h.attr("href").strip()
            (investor_key,) = util.re_get_result(r"http://www.itjuzi.com/investfirm/(\d*)$", investor_url)
            logger.info("Investor: %s, %s, %s", investor_key, investor_name, investor_url)
            investor = {
                "name":investor_name,
                "key":investor_key,
                "url":investor_url,
                "type":38001
            }
            investors.append(investor)

        hs = l('td:eq(3)> span')
        for h in hs:
            h = pq(h)
            investor_name = h.text().strip()
            if investor_name == u"投资方未透露" or investor_name == "":
                continue
            investor_url = None
            investor_key = None
            logger.info("Investor: %s, %s, %s", investor_key, investor_name, investor_url)
            investor = {
                "name":investor_name,
                "key":investor_key,
                "url":investor_url,
                "type":38001
            }
            investors.append(investor)


        funding["investors"] = investors
        fundings.append(funding)

    logger.info("")
    return fundings