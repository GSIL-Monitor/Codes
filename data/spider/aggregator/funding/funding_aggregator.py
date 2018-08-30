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
import extract
import aggregator_util
import trends_tool

#logger
loghelper.init_logger("funding_aggregator", stream=True)
logger = loghelper.get_logger("funding_aggregator")

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
    kafkaConsumer = KafkaConsumer("parser_funding_v2", group_id="funding_aggregator",
                metadata_broker_list=[url],
                auto_offset_reset='smallest')

def aggregate(source_funding_id):
    logger.info("source_funding_id: %s" % source_funding_id)
    sf = conn.get("select * from source_funding where id=%s", source_funding_id)
    if sf is None:
        return

    source_company = conn.get("select * from source_company where id=%s", sf["sourceCompanyId"])
    if source_company is None:
        return

    if source_company["companyId"] is None:
        return

    company_id = source_company["companyId"]

    if sf["fundingId"] is None:
        f = conn.get("select * from funding where companyId=%s and round=%s limit 1",
                     source_company["companyId"], sf["round"])
        if f is None:
            sql = "insert funding(companyId,preMoney,postMoney,investment,\
                        round,roundDesc,currency,precise,fundingDate,fundingType,\
                        active,createTime,modifyTime) \
                    values(%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,'Y',now(),now())"
            fundingId=conn.insert(sql,
                                  source_company["companyId"],
                                  sf["preMoney"],
                                  sf["postMoney"],
                                  sf["investment"],
                                  sf["round"],
                                  sf["roundDesc"],
                                  sf["currency"],
                                  sf["precise"],
                                  sf["fundingDate"],
                                  8030
                                  )
        else:
            fundingId = f["id"]
        conn.update("update source_funding set fundingId=%s where id=%s", fundingId, sf["id"])
    else:
        fundingId = sf["fundingId"]

    sfirs = conn.query("select * from source_funding_investor_rel where sourceFundingId=%s", sf["id"])
    for sfir in sfirs:
        if sfir["fundingInvestorRelId"] is not None:
            continue

        investor_id = None
        investor_company_id = None

        if sfir["investorType"] == 38001:
            source_investor = conn.get("select * from source_investor where id=%s", sfir["sourceInvestorId"])
            if source_investor is None:
                continue
            investor_id = aggregate_investor(source_investor)
        else:
            source_company = conn.get("select * from source_company where id=%s", sfir["sourceCompanyId"])
            if source_company is None or source_company["companyId"] is None:
                #TODO 如果company还未聚合好,如何处理?
                continue
            investor_company_id = source_company["companyId"]

        funding_investor_rel = conn.get("select * from funding_investor_rel \
                            where investorId=%s and fundingId=%s",
                            investor_id, fundingId)
        if funding_investor_rel is None:
            sql = "insert funding_investor_rel(fundingId, investorType, investorId, companyId, currency, investment,\
                    precise,active,createTime,modifyTime) \
                    values(%s,%s,%s,%s,%s,%s,%s,'Y',now(),now())"
            fundingInvestorRelId = conn.insert(sql,
                        fundingId,
                        sfir["investorType"],
                        investor_id,
                        investor_company_id,
                        sfir["currency"],
                        sfir["investment"],
                        sfir["precise"]
                    )
        else:
            fundingInvestorRelId = funding_investor_rel["id"]

        conn.update("update source_funding_investor_rel set fundingInvestorRelId=%s where id=%s",
                    fundingInvestorRelId,sfir["id"]
                    )

    # update company stage
    funding = conn.get("select * from funding where companyId=%s order by round desc, fundingDate desc limit 1",
                       company_id)
    if funding is not None:
        conn.update("update company set round=%s, roundDesc=%s where id=%s",
                    funding["round"],funding["roundDesc"],company_id)


    '''
    msg = {"type":"funding", "id":fundingId}
    flag = False
    while flag == False:
        try:
            kafkaProducer.send_messages("aggregator_funding_v2", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)
    '''

    return


def aggregate_investor(source_investor):
    investor_id = source_investor["investorId"]
    if investor_id is not None:
        return investor_id

    name = source_investor["name"]
    website = source_investor["website"]
    if website is not None and website.find("无") != -1:
        website = None
    domain = util.get_domain(website)

    investor = conn.get("select * from investor where name=%s", name)
    if investor is None and website is not None and website !="":
        investor = conn.get("select * from investor where website=%s",website)
    if investor is None and domain is not None and domain!="":
        investor = conn.get("select * from investor where domain=%s",domain)

    if investor is None:
        investor_id = conn.insert("insert investor(name,website,domain,\
                            description,logo,stage,field,type,\
                            active,createTime,modifyTime) \
                            values(%s,%s,%s,\
                            %s,%s,%s,%s,%s,\
                            'Y',now(),now())",
                            source_investor["name"],
                            website,
                            domain,
                            source_investor["description"],
                            source_investor["logo"],
                            source_investor["stage"],
                            source_investor["field"],
                            10020
                            )
    else:
        investor_id = investor["id"]
    conn.update("update source_investor set investorId=%s where id=%s",investor_id,source_investor["id"])

    return investor_id


if __name__ == '__main__':
    logger.info("funding aggregator start")
    initKafka()

    i = 0
    while True:
        try:
            for message in kafkaConsumer:
                try:
                    conn = db.connect_torndb()
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                     message.offset, message.key,
                                                     message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    source_funding_id = msg["id"]

                    if type == "funding":
                        aggregate(source_funding_id)
                except Exception,e :
                    logger.exception(e)
                finally:
                    kafkaConsumer.task_done(message)
                    kafkaConsumer.commit()
                    conn.close()
        except KeyboardInterrupt:
            exit(0)
        except Exception,e :
            logger.exception(e)
            time.sleep(60)
            initKafka()