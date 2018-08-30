# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
from kafka import (KafkaClient, SimpleProducer)
import json
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper
import config
#logger
loghelper.init_logger("stock_aggregate", stream=True)
logger = loghelper.get_logger("stock_aggregate")

source_map = {
    13400: "新三板",
    13401: "上证",
    13402: "深证"
}

# kafka
kafkaProducer = None


def init_kafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)

def send_message(company_id, action):
    if kafkaProducer is None:
        init_kafka()

    #action: create, delete
    msg = {"type":"company", "id":company_id , "action":action}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("aggregator_v2", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)

def get_locations(areacode):
    conn = db.connect_torndb()
    locations = conn.query("select * from location where areacode=%s", areacode)
    conn.close()
    if len(locations) > 0:
        return [int(location["locationId"]) for location in locations]
    else:
        return []

def find_companies(full_name, short_name, locations):
    companyIds = []
    companyIds.extend(find_company_by_fullname(full_name))
    if locations is not None:
        companyIds.extend([id for id in find_company_by_shortname(short_name, locations) if id not in companyIds])
    return companyIds

def find_company_by_fullname(full_name):
    fcompanyIds = []
    full_name = name_helper.company_name_normalize(full_name)
    conn = db.connect_torndb()
    fcompanies = conn.query("select * from company where fullName=%s and (active is null or active !='N') order by id desc", full_name)
    fcompanyIds.extend([company["id"] for company in fcompanies if company["id"] not in fcompanyIds])
    # logger.info("a: %s",companyIds)
    fcompanies2 = conn.query( "select * from company where name=%s and (active is null or active !='N') order by id desc", full_name)
    fcompanyIds.extend([company["id"] for company in fcompanies2 if company["id"] not in fcompanyIds])
    # logger.info("b: %s", companyIds)
    conn.close()
    return fcompanyIds

def find_company_by_shortname(short_name, locations):
    scompanyIds = []
    conn = db.connect_torndb()
    scompanies = conn.query("select distinct a.companyId,c.locationId from company_alias a join company c on c.id=a.companyId where (c.active is null or c.active !='N') \
                            and (a.active is null or a.active !='N') and a.name=%s order by c.id desc", short_name)
    scompanyIds.extend([company["companyId"] for company in scompanies if int(company["locationId"]) in locations])

    # logger.info("shortname_mapping: %s", scompanyIds)
    conn.close()
    return scompanyIds

def check_funding(stockCode, stockName, fcompanyIds):
    ifcompanyIds = []
    conn = db.connect_torndb()
    for fcompanyId in fcompanyIds:
        neeqf = conn.get("select * from funding where companyId=%s and (active is null or active='Y') and round=1105 limit 1",fcompanyId)
        if neeqf is None:
            logger.info("stock: %s|%s, company:%s missing funding", stockCode, stockName, fcompanyId)
            ifcompanyIds.append(fcompanyId)
    conn.close()
    return ifcompanyIds

def insert_company(stock):
    pass

def insert_stock(companyId, stock):
    pass

def insert_funding(companyId, stock):
    try:
        conn = db.connect_torndb()
        sql = "insert funding(companyId,round,currency,fundingDate,tracked,createTime,modifyTime) values(%s,%s,%s,%s,now(),now(),%s)"
        funding_id = conn.insert(sql,companyId,1105,3020,stock["listingDate"],'Y')
        conn.close()
    except Exception, e:
        pass

def insert_funding_check(fccompanyIds, stock):
    if stock["source"] == 13400:
        ldate = stock["listingDate"]
        stockName = stock["name"]+ "|" + stock["shortname"]
        stockWebsite = stock["stockWebsite"]
    else:
        return
    data = {
        "name": source_map[stock["source"]] + " : " + stockName,
        "processStatus": 0,
        "items": [{
            "sort": 1,
            "brief": stockWebsite,
            "round": source_map[stock["source"]]
        }, {
            "sort": 1.01,
            "brief": "挂牌时间: %s" % ldate,
            "round": source_map[stock["source"]]
        }
        ],
        "company": fccompanyIds,
        "news_date": datetime.datetime.now() - datetime.timedelta(hours=8),
        "news_id": [],
        "createTime": datetime.datetime.now() - datetime.timedelta(hours=8)
    }

    # print data
    mongo = db.connect_mongo()
    mongo.raw.funding.insert(data)
    mongo.close()

def aggregate(stock):
    #新三板
    (name, shortname, location, stockcode) = (None, None, None, None)
    if stock["source"] == 13400:
        name = stock["content"]["baseinfo"]["name"]
        shortname = stock["content"]["baseinfo"]["shortname"]
        # location = stock["locationId"]
        stockcode = stock["sourceId"]
    if name is None or shortname is None:
        return

    company_ids = find_companies(name, shortname, location)

    if len(company_ids) == 0:
        #insert stock as new company
        company_id = insert_company(stock)
        insert_funding(company_id, stock)
        insert_stock(company_id,stock)
        send_message(company_id, "create")
    else:
        #check funding has 新三板
        incorrent_funding_company_ids = check_funding(stockcode, name, company_ids)

        if len(incorrent_funding_company_ids) == 0:
            #funding all correct
            for company_id in company_ids: insert_stock(company_id, stock)
        else:
            if len(company_ids) == 1:
                # one company missing one funding
                insert_funding(company_ids[0], stock)
                insert_stock(company_ids[0], stock)
            else:
                # multiple companies missng some fundings: we need check!
                insert_funding_check(company_ids, stock)

if __name__ == '__main__':
    logger.info("Begin...")

    logger.info("End.")