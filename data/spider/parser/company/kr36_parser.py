# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html
from bson.objectid import ObjectId
import traceback
from kr36_location import kr36_cities

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import requests
import util
import parser_util

source = 13020

def formCityName(name):
    if name.endswith("市"):
        return name.split("市")[0]
    if name.endswith("县"):
        return name.split("县")[0]
    return name

def parse_company(company_key):
    item = fromdb.company.find_one({"source":source, "company_key":company_key})
    if item is None:
        return


    #company basic info
    c = item["company_base"]["data"]["company"]

    if c["status"] == "INIT":
        return

    tags = item["company_base"]["data"]["tags"]
    tags2 = []
    for tag in tags:
        tags2.append(tag["name"])
    tags_str = ",".join(tags2)

    logo_id = None
    logo_url = c["logo"]
    if logo_url != '':
        logo_id = parser_util.get_logo_id(source, company_key, 'company', logo_url)

    establish_date = None
    if c.has_key("startDate"):
        d = time.localtime(c["startDate"]/1000)
        establish_date = datetime.datetime(d.tm_year,d.tm_mon,d.tm_mday)

    address1 = None
    address2 = None
    if c.has_key("address1"):
        address1 = c["address1"]
    if c.has_key("address2"):
        address2 = c["address2"]

    location_id = 0
    if address2!=None:
        city = kr36_cities.get(str(address2),None)
        if city != None:
            location_id = parser_util.get_location_id(formCityName(city))

    if location_id==0 and address1 != None:
        city = kr36_cities.get(str(address1),None)
        if city != None:
            location_id = parser_util.get_location_id(formCityName(city))

    fullName = c["fullName"]
    fullName = fullName.replace("_","")
    idx = fullName.rfind(u"公司")
    if idx != -1:
        fullName = fullName[:(idx+len(u"公司"))]
    fullName = util.norm_company_name(fullName)

    desc = ""
    productDesc = None
    modelDesc = None
    operationDesc = None
    teamDesc = None
    marketDesc = None
    compititorDesc = None
    advantageDesc = None
    planDesc = None

    if c.has_key("projectAdvantage"):
        productDesc = c["projectAdvantage"].strip()
    if c.has_key("dataLights"):
        operationDesc = c["dataLights"].strip()
    if c.has_key("projectPlan"):
        modelDesc = c["projectPlan"].strip()
    if c.has_key("competitor"):
        compititorDesc = c["competitor"].strip()
    if c.has_key("intro"):
        desc = c["intro"].strip()
    if c.has_key("story"):
        teamDesc = c["story"].strip()


    source_company = {"name": c["name"],
                      "fullName": fullName,
                      "description": desc,
                      "productDesc":productDesc,
                      "modelDesc":modelDesc,
                      "operationDesc":operationDesc,
                      "teamDesc":teamDesc,
                      "marketDesc":marketDesc,
                      "compititorDesc":compititorDesc,
                      "advantageDesc":advantageDesc,
                      "planDesc":planDesc,
                      "brief": c["brief"],
                      "round": 0,
                      "roundDesc": None,
                      "companyStatus": 2010,
                      'fundingType':0,
                      "locationId": location_id,
                      "address": None,
                      "phone": None,
                      "establishDate": establish_date,
                      "logo": logo_id,
                      "source": source,
                      "sourceId": company_key,
                      "field":  c.get("industry"),
                      "subField": None,
                      "tags": tags_str,
                      "headCountMin": None,
                      "headCountMax": None
                      }

    source_company_id = parser_util.insert_source_company(source_company)

    # artifact
    website = c.get("website","").strip()
    if website is not None and website != "":
        source_artifact = {"sourceCompanyId": source_company_id,
                           "name": c["name"],
                           "description": None,
                           "link": website,
                           "type": 4010
                           }
        parser_util.insert_source_artifact(source_artifact)

    weibo = c.get("weibo","").strip()
    if weibo is not None and weibo != "":
        source_artifact = {"sourceCompanyId": source_company_id,
                           "name": c["name"],
                           "description": None,
                           "link": weibo,
                           "type": 4030
                           }
        parser_util.insert_source_artifact(source_artifact)

    weixin = c.get("weixin","").strip()
    if weixin is not None and weixin != "":
        source_artifact = {"sourceCompanyId": source_company_id,
                           "name": c["name"],
                           "description": None,
                           "link": weixin,
                           "type": 4020
                           }
        parser_util.insert_source_artifact(source_artifact)

    iphoneAppstoreLink = c.get("iphoneAppstoreLink","").strip()
    if iphoneAppstoreLink is not None and iphoneAppstoreLink != "":
        source_artifact = {"sourceCompanyId": source_company_id,
                           "name": c["name"],
                           "description": None,
                           "link": iphoneAppstoreLink,
                           "type": 4040
                           }
        parser_util.insert_source_artifact(source_artifact)

    ipadAppstoreLink = c.get("ipadAppstoreLink","").strip()
    if ipadAppstoreLink is not None and ipadAppstoreLink != "":
        source_artifact = {"sourceCompanyId": source_company_id,
                           "name": c["name"],
                           "description": None,
                           "link": ipadAppstoreLink,
                           "type": 4040
                           }
        parser_util.insert_source_artifact(source_artifact)

    # funding / past_finance
    parseFinance(source_company_id, item["past_finance"]["data"]["data"])

    # members
    parseMember(source_company_id,5010,item["founders"]["data"]["data"])
    parseMember(source_company_id,5030,item["employees"]["data"]["data"])
    parseMember(source_company_id,5040,item["former_members"]["data"]["data"])

    msg = {"type":"company", "id":source_company_id}
    kafka_producer.send_messages("parser_v2", json.dumps(msg))


def parseFinance(source_company_id, finances):
    for finance in finances:
        logger.info("%s,%s,%s,%s" % (finance.get("phase"),finance.get("financeAmountUnit"),finance["financeDate"],finance.get("financeAmount")))

        roundStr = finance.get("phase")
        fundingRound = 0
        if roundStr == "INFORMAL" or roundStr=="ANGEL":
            fundingRound = 1010
            roundStr = "天使"
        elif roundStr == "PRE_A":
            fundingRound = 1020
            roundStr = "Pre-A"
        elif roundStr == "A":
            fundingRound = 1030
        elif roundStr == "A_PLUS":
            fundingRound = 1030
            roundStr = "A+"
        elif roundStr == "B":
            fundingRound = 1040
        elif roundStr == "B_PLUS":
            fundingRound = 1040
            roundStr = "B+"
        elif roundStr == "C":
            fundingRound = 1050
        elif roundStr == "D":
            fundingRound = 1060
        elif roundStr == "E":
            fundingRound = 1070
        elif roundStr == "F":
            fundingRound = 1080
        elif roundStr == "IPO":
            fundingRound = 1110

        d = time.localtime(finance["financeDate"]/1000)
        fundingDate = datetime.datetime(d.tm_year,d.tm_mon,d.tm_mday)
        fundingCurrency = 3010
        if finance.get("financeAmountUnit") == "USD":
            fundingCurrency = 3010
        elif finance.get("financeAmountUnit") == "CNY":
            fundingCurrency = 3020

        fundingInvestment = 0
        precise = 'Y'
        financeAmount = finance.get("financeAmount")
        if financeAmount != None:
            try:
                fundingInvestment = int(financeAmount) * 10000
            except:
                pass

            if fundingInvestment == 0:
                if financeAmount == u"数万":
                    fundingInvestment = 1*10000
                    precise = 'N'
                elif financeAmount == u"数十万":
                    fundingInvestment = 10*10000
                    precise = 'N'
                elif financeAmount == u"数百万":
                    fundingInvestment = 100*10000
                    precise = 'N'
                elif financeAmount == u"数千万":
                    fundingInvestment = 1000*10000
                    precise = 'N'
                elif financeAmount == u"数万万":
                    fundingInvestment = 10000*10000
                    precise = 'N'
                elif financeAmount == u"数亿":
                    fundingInvestment = 10000*10000
                    precise = 'N'

        source_funding = {
            "sourceCompanyId":source_company_id,
            "preMoney": None,
            "postMoney": None,
            "investment":fundingInvestment,
            "precise":precise,
            "round":fundingRound,
            "roundDesc":roundStr,
            "currency":fundingCurrency,
            "fundingDate":fundingDate
        }


        source_investors = []
        investors = finance.get("participants")
        if investors is not None:
            for investor in investors:
                logger.info(investor.get("name"))
                entityId = investor.get("entityId")
                entityType = investor.get("entityType")
                if entityType == "ORGANIZATION":
                    item = fromdb.investor.find_one({"source":source, "investor_key":str(entityId)})
                    if item:
                        v = item["investor_base"]["data"]
                        source_investor = {
                            "name": v["name"],
                            "website": v["website"],
                            "description": v["intro"],
                            "logo_url":v["logo"],
                            "stage": None,
                            "field": None,
                            "type":10020,
                            "source":source,
                            "sourceId":str(entityId)
                        }
                        source_investors.append(source_investor)
                elif entityType == "COMPANY":
                    item = fromdb.company.find_one({"source":source, "company_key":str(entityId)})
                    if item:
                        v = item["company_base"]["data"]["company"]
                        source_investor = {
                            "name": v["name"],
                            "website": v["website"],
                            "description": v["intro"],
                            "logo_url":v["logo"],
                            "stage": None,
                            "field": None,
                            "type":10020,
                            "source":source,
                            "sourceId":str(entityId)
                        }
                        source_investors.append(source_investor)
                else:
                    logger.info("**********" + entityType + ", entityId=" + str(entityId))

        parser_util.insert_source_funding(source_funding, source_investors)

def parseMember(source_company_id, type, members):
    for m in members:
        logger.info(m["name"])
        source_member = {
            "source":source,
            "sourceId":str(m["id"]),
            "name":m["name"],
            "photo_url":m.get("avatar"),
            "weibo":None,
            "location":0,
            "role":None,
            "description":m.get("intro"),
            "education":None,
            "work":None
        }

        source_company_member_rel = {
            "sourceCompanyId":source_company_id,
            "position":m.get("position"),
            "joinDate":None,
            "leaveDate":None,
            "type": type
        }

        parser_util.insert_source_member(source_member, source_company_member_rel)

if __name__ == '__main__':
    (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("kr36", "crawler_kr36_v2")

    while True:
        try:
            for message in kafka_consumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                               message.offset, message.key,
                                                               message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    company_key = msg["company_key"]

                    if type == "company":
                        parse_company(company_key)
                except Exception,e :
                    logger.exception(e)
                finally:
                    kafka_consumer.task_done(message)
                    kafka_consumer.commit()
                    pass
        except KeyboardInterrupt:
            exit(0)
        except Exception,e :
            logger.error(e)
            time.sleep(60)
            (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("kr36", "crawler_kr36_v2")


