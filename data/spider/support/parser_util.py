# -*- coding: utf-8 -*-

import sys, os
from pymongo import MongoClient
import pymongo
from kafka import KafkaClient, KafkaConsumer, SimpleProducer

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import config
import loghelper
import my_request
import util
import db
import extract

import gridfs

# mongo
mongo = db.connect_mongo()
fromdb = mongo.crawler_v2
imgfs = gridfs.GridFS(mongo.gridfs)


# logger
loghelper.init_logger("parser_util", stream=True)
logger = loghelper.get_logger("parser_util")


def parser_init(spider_name, msg_name):
    # logger
    loghelper.init_logger("parser(" + spider_name + ")", stream=True)
    logger = loghelper.get_logger("parser(" + spider_name + ")")

    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafka_producer = SimpleProducer(kafka)
    kafka_consumer = KafkaConsumer(msg_name, group_id="parser_" + spider_name,
                                   metadata_broker_list=[url],
                                   auto_offset_reset='smallest')

    return logger, fromdb, kafka_producer, kafka_consumer


def parser_news_init(spider_name, msg_name):
    # logger
    loghelper.init_logger("parser(" + spider_name + ")", stream=True)
    logger = loghelper.get_logger("parser(" + spider_name + ")")

    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafka_producer = SimpleProducer(kafka)
    kafka_consumer = KafkaConsumer(msg_name, group_id="parser_" + spider_name,
                                   metadata_broker_list=[url],
                                   auto_offset_reset='smallest')

    news_collection = mongo.parser_v2.direct_news
    news_collection.create_index([("source", pymongo.DESCENDING), ("news_key", pymongo.DESCENDING)], unique=True)

    return logger, fromdb, kafka_producer, kafka_consumer, news_collection


def get_location_id(location_name):
    if location_name == None or location_name == "":
        return 0

    conn = db.connect_torndb()
    result = conn.get("select * from location where locationName=%s", location_name)
    if result is not None:
        location_id = result["locationId"]
    else:
        location_id = 0

    conn.close()
    return location_id


def get_logo_id(source, key, type, logo_url):
    # logger.info("%s, %s, %s, %s" % (source,key,type,logo_url))
    if logo_url.strip() == "":
        return None

    logo_id = None
    conn = db.connect_torndb()

    name = "logo"
    if type == 'company':
        type = 'source_company'
    elif type == 'member':
        type = 'source_member'
        name = "photo"
    elif type == 'investor':
        type = 'source_investor'

    source_company = conn.get("select * from " + type + " where source=%s and sourceId=%s", source, key)
    if source_company == None or source_company[name] == None or source_company[name] == "":
        image_value = my_request.get_image(logger, logo_url)
        if image_value is not None:
            logo_id = imgfs.put(image_value, content_type='jpeg', filename='%s_%s_%s.jpg' % (source, type, key))
            # logger.info("gridfs logo_id=%s" % logo_id)
    else:
        logo_id = source_company[name]

    conn.close()
    return logo_id


def get_cf_pic_id(sourceCfId, sourceId, pic_url):
    conn = db.connect_torndb()
    source_cf_pic = conn.get("select * from source_cf_document where sourceCfId=%s and sourceId=%s", sourceCfId,
                             sourceId)
    if source_cf_pic == None or source_cf_pic['link'] == None or source_cf_pic['link'] == "":
        image_value = my_request.get_image(logger, pic_url)
        pic_id = imgfs.put(image_value, content_type='jpeg', filename='%s_%s.jpg' % (sourceCfId, sourceId))
        # logger.info("gridfs logo_id=%s" % logo_id)
    else:
        pic_id = source_cf_pic['link']

    conn.close()
    return pic_id


def insert_source_company(source_company):
    conn = db.connect_torndb()

    s = source_company
    result = conn.get("select * from source_company where source=%s and sourceId=%s", s["source"], s["sourceId"])
    if result != None:
        source_company_id = result["id"]
        s["id"] = source_company_id
        update_source_company(s)
    else:
        # logger.info(s["name"])
        # logger.info(s["fullName"])
        # logger.info(s["description"])
        # logger.info(s["brief"])
        # logger.info(s["round"])
        # logger.info(s["roundDesc"])
        # logger.info(s["companyStatus"])
        # logger.info(s["fundingType"])
        # logger.info(s["locationId"])
        # logger.info(s["establishDate"])
        # logger.info(s["logo"])
        # logger.info(s["source"])
        # logger.info(s["sourceId"])
        # logger.info(s["field"])
        # logger.info(s["subField"])
        # logger.info(s["tags"])

        sql = "insert source_company(name,fullName,description,brief,round, \
              productDesc, modelDesc, operationDesc, teamDesc, marketDesc, compititorDesc, advantageDesc, planDesc, \
              roundDesc,companyStatus,fundingType,locationId, address, \
              phone, establishDate, logo,source,sourceId, \
              createTime,modifyTime, \
              field,subField,tags, headCountMin, headCountMax) \
              values \
              (%s,%s,%s,%s,%s, \
              %s,%s,%s,%s,%s,%s,%s,%s, \
              %s,%s,%s,%s,%s, \
              %s,%s,%s, %s, %s, \
              now(),now(), \
              %s,%s,%s, %s, %s)"

        source_company_id = conn.insert(sql,
                                        s["name"], s["fullName"], s["description"], s["brief"], s["round"],
                                        s.get("productDesc"), s.get("modelDesc"), s.get("operationDesc"),
                                        s.get("teamDesc"), s.get("marketDesc"), s.get("compititorDesc"),
                                        s.get("advantageDesc"), s.get("planDesc"),
                                        s["roundDesc"], s["companyStatus"], s["fundingType"], s["locationId"],
                                        s["address"],
                                        s["phone"], s["establishDate"], s["logo"], s["source"], s["sourceId"],
                                        s["field"], s["subField"], s["tags"], s["headCountMin"], s["headCountMax"]
                                        )
    conn.close()
    return source_company_id


def update_source_company(source_company):
    s = source_company
    conn = db.connect_torndb()
    conn.update("update source_company set \
                        name=%s, fullName=%s, description=%s, companyStatus=%s, fundingType=%s,\
                        locationId=%s,establishDate=%s,logo=%s, \
                        productDesc=%s, modelDesc=%s, operationDesc=%s, teamDesc=%s, marketDesc=%s, compititorDesc=%s, advantageDesc=%s, planDesc=%s, \
                        modifyTime=now() \
                        where id=%s",
                s["name"], s["fullName"], s["description"], s["companyStatus"], s["fundingType"],
                s["locationId"], s["establishDate"], s["logo"],
                s.get("productDesc"), s.get("modelDesc"), s.get("operationDesc"), s.get("teamDesc"),
                s.get("marketDesc"), s.get("compititorDesc"), s.get("advantageDesc"), s.get("planDesc"),
                s["id"]
                )
    conn.close()


def insert_source_member(source_member, source_company_member_rel):
    s = source_member
    r = source_company_member_rel
    conn = db.connect_torndb()
    source_member = conn.get("select * from source_member where source=%s and sourceId=%s",
                             s['source'], s['sourceId'])

    source = s["source"]
    sourceId = s["sourceId"]
    photo_url = s["photo_url"]

    photo_id = None
    if photo_url is not None and photo_url.strip() != "":
        photo_id = get_logo_id(source, sourceId, "member", photo_url)

    if source_member is None:
        sql = "insert source_member(name,photo,weibo,location,role,description,\
                education,work,source,sourceId,createTime,modifyTime) \
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"
        source_member_id = conn.insert(sql,
                                       s["name"], photo_id, s['weibo'], s['location'], s['role'], s['description'],
                                       s['education'], s['work'], s['source'], s['sourceId'])
    else:
        source_member_id = source_member["id"]
        sql = "update source_member set name=%s,photo=%s,weibo=%s,location=%s,role=%s,description=%s,\
        education=%s,work=%s,modifyTime=now() where id=%s"
        conn.update(sql,
                    s["name"], photo_id, s['weibo'], s['location'], s['role'], s['description'],
                    s['education'], s['work'], source_member_id)

    source_company_member_rel = conn.get("select * from source_company_member_rel where \
                    sourceCompanyId=%s and sourceMemberId=%s",
                                         r["sourceCompanyId"], source_member_id)
    if source_company_member_rel is None:
        conn.insert("insert source_company_member_rel(sourceCompanyId, sourceMemberId, \
                    position, joinDate, leaveDate, type,createTime,modifyTime) \
                    values(%s,%s,%s,%s,%s,%s, now(),now())",
                    r["sourceCompanyId"], source_member_id, r['position'], r['joinDate'], r['leaveDate'], r['type'])
    else:
        sql = "update source_company_member_rel set \
                position=%s, joinDate=%s, leaveDate=%s,type=%s,modifyTime=now() \
                where id=%s"
        conn.update(sql, r["position"], r["joinDate"], r["leaveDate"], r["type"], source_company_member_rel["id"])

    conn.close()


def insert_source_footprint(source_footprint):
    f = source_footprint
    conn = db.connect_torndb()
    fp = conn.get("select * from source_footprint where sourceCompanyId=%s and footDate=%s and description=%s",
                  f["sourceCompanyId"], f["footDate"], f["description"])
    if fp == None:
        conn.insert("insert source_footprint(sourceCompanyId,footDate,description,createTime,modifyTime) \
                    values(%s,%s,%s,now(),now())",
                    f["sourceCompanyId"], f["footDate"], f["description"])
    conn.close()


def insert_source_news(source_news):
    s = source_news
    if s is None:
        return None

    try:
        source = s["source"]
        company_key = s["company_key"]
        news_key = s["news_key"]
        title = s["title"]
        url = s["url"]
        domain = s["domain"]
        date = s["date"]
        html = s["content"]

        if html.find("404未找到页面") != -1:
            logger.info("404未找到页面")
            return None

        if fromdb.source_news.find_one({"source": source, "company_key": company_key, "news_key": news_key}) == None:
            contents = extract.extractContents(url, html)
            data = {"source": source,
                    "news_key": news_key,
                    "company_key": company_key,
                    "url": url,
                    "title": title,
                    "source_domain": domain,
                    "date": date,
                    "contents": contents}
            fromdb.source_news.insert_one(data)
    except Exception, ex:
        logger.exception(ex)


def insert_source_funding(source_funding, investors):
    f = source_funding
    conn = db.connect_torndb()
    source_funding = conn.get("select * from source_funding where sourceCompanyId=%s and roundDesc=%s",
                              f["sourceCompanyId"], f["roundDesc"])

    investment = f['investment']

    if investment is None or investment == 'None':
        investment = 0

    if source_funding == None:
        source_funding_id = conn.insert("insert source_funding(\
                                sourceCompanyId, investment, round, roundDesc, currency,\
                                precise, fundingDate, createTime, modifyTime) \
                                values(%s,%s,%s,%s,%s,%s,%s,now(),now())",
                                        f["sourceCompanyId"], investment, f["round"], f["roundDesc"], f["currency"],
                                        f["precise"], f["fundingDate"])
    else:
        source_funding_id = source_funding["id"]
        conn.update("update source_funding set investment=%s,currency=%s, precise=%s, fundingDate=%s, modifyTime=now() \
                    where id=%s",
                    investment, f["currency"], f["precise"], f["fundingDate"], source_funding_id
                    )

    if len(investors) != 0:
        for investor in investors:
            source_investor_id = insert_source_investor(investor)
            source_funding_investor_rel = conn.get("select * from source_funding_investor_rel where \
                sourceFundingId=%s and sourceInvestorId=%s",
                                                   source_funding_id, source_investor_id)
            if source_funding_investor_rel is None:
                conn.insert("insert source_funding_investor_rel(sourceFundingId, sourceInvestorId, \
                            createTime,modifyTime) \
                            values(%s,%s, now(),now())",
                            source_funding_id, source_investor_id)

    conn.close()


def insert_source_investor(source_investor):
    s = source_investor
    source = s["source"]
    sourceId = s["sourceId"]
    logo_url = s["logo_url"]
    conn = db.connect_torndb()
    source_investor = conn.get("select * from source_investor where source=%s and sourceId=%s",
                               source, sourceId)

    logo_id = None
    if logo_url is not None and logo_url.strip() != "":
        logo_id = get_logo_id(source, sourceId, "investor", logo_url)

    if source_investor is None:
        sql = "insert source_investor(" \
              "name,website,description,logo,stage," \
              "field,type, source,sourceId,createTime," \
              "modifyTime)" \
              " values" \
              "(%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,now()," \
              "now())"
        source_investor_id = conn.insert(sql,
                                         s["name"], s["website"], s["description"], logo_id, s["stage"],
                                         s["field"], s["type"], source, sourceId)
    else:
        source_investor_id = source_investor["id"]
        sql = "update source_investor set name=%s,website=%s,description=%s,logo=%s,stage=%s,\
        field=%s,type=%s,modifyTime=now() where id=%s"
        conn.update(sql,
                    s["name"], s["website"], s["description"], logo_id, s["stage"],
                    s["field"], s["type"], source_investor_id)

    conn.close()
    return source_investor_id


def insert_source_job(source_job):
    s = source_job
    sourceCompanyId = s["sourceCompanyId"]
    sourceId = s["sourceId"]
    conn = db.connect_torndb()
    source_job = conn.get("select * from source_job where sourceCompanyId=%s and sourceId=%s",
                          sourceCompanyId, sourceId)

    if source_job is None:
        sql = "insert source_job(sourceCompanyId, position, salary, description, domain," \
              "locationId, educationType, workYearType, startDate, updateDate," \
              "sourceId, createTime, modifyTime)" \
              "values" \
              "(%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s, now(),now())"
        conn.insert(sql,
                    sourceCompanyId, s["position"], s["salary"], s["description"], s["domain"],
                    s["locationId"], s["educationType"], s["workYearType"], s["startDate"], s["updateDate"],
                    sourceId)
    else:
        sql = "update source_job set position=%s, salary=%s, description=%s, domain=%s, locationId=%s,\
                educationType=%s, workYearType=%s, startDate=%s, updateDate=%s where id=%s"
        conn.update(sql, s["position"], s["salary"], s["description"], s["domain"], s["locationId"],
                    s["educationType"], s["workYearType"], s["startDate"], s["updateDate"], source_job["id"]
                    )


def insert_source_artifact(source_artifact):
    s = source_artifact
    sourceCompanyId = s["sourceCompanyId"]
    conn = db.connect_torndb()

    link = s["link"]
    if link is None:
        source_artifact = conn.get("select * from source_artifact where sourceCompanyId=%s and type=%s",
                                   sourceCompanyId, s["type"])
    else:
        source_artifact = conn.get("select * from source_artifact where sourceCompanyId=%s and type=%s and link=%s",
                                   sourceCompanyId, s["type"], s["link"])

    if source_artifact is None:
        sql = "insert source_artifact(sourceCompanyId, name, description, link, type,createTime,modifyTime) \
                          values(%s,%s,%s,%s,%s,now(),now())"
        conn.insert(sql, sourceCompanyId, s["name"], s["description"], s["link"], s["type"])
    else:
        sql = "update source_artifact set description=%s, link=%s where id=%s"
        conn.update(sql, s["description"], s["link"], source_artifact["id"])


def get_source_company(source, sourceId):
    conn = db.connect_torndb()
    result = conn.get('select * from source_company where source=%s and sourceId=%s', source, sourceId)
    if result is not None:
        return result['id']


#######################        crowdfunding      ##############################

def insert_source_crowdfunding(source_crowdfunding):
    s = source_crowdfunding
    conn = db.connect_torndb()

    source_crowdfunding = conn.get("select * from source_crowdfunding where source=%s and sourceId=%s",
                                   s['source'], s["sourceId"])

    if source_crowdfunding is None:
        sql = "insert source_crowdfunding(" \
              "name, description, coinvestorCount, maxCoinvestorNum, minRaising, " \
              "successRaising, maxRaising, minInvestment, currency, startDate," \
              "endDate, preMoney, postMoney, status, round," \
              "roundDesc, value, tags, accessCount, likesCount, " \
              "followCount, painPoint, marketSituation,  competitorAnalyze, profitModel," \
              "marketShare, coreResources, cfAdvantage, advantageAnalysis, companyVision," \
              "companyDesc, bmSolution, source, sourceId, sourceCompanyId, " \
              "createTime, modifyTime) \
              values(%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "now(),now())"

        source_cf_id = conn.insert(sql,
                                   s['name'], s['description'], s['coinvestorCount'], s['maxCoinvestorNum'],
                                   s['minRaising'],
                                   s['successRaising'], s['maxRaising'], s['minInvestment'], s['currency'],
                                   s['startDate'],
                                   s['endDate'], s['preMoney'], s['postMoney'], s['status'], s['round'],
                                   s['roundDesc'], s['value'], s['tags'], s['accessCount'], s['likesCount'],
                                   s['followCount'], s['painPoint'], s['marketSituation'], s['competitorAnalyze'],
                                   s['profitModel'],
                                   s['marketShare'], s['coreResources'], s['cfAdvantage'], s['advantageAnalysis'],
                                   s['companyVision'],
                                   s['companyDesc'], s['bmSolution'], s['source'], s['sourceId'], s['sourceCompanyId']
                                   )
    else:
        source_cf_id = source_crowdfunding['id']
        sql = "update source_crowdfunding set description=%s, " \
              " accessCount=%s, likesCount=%s , followCount=%s, coinvestorCount=%s, status=%s, " \
              " value=%s, preMoney=%s, postMoney=%s where id = %s "
        conn.update(sql, s['description'],
                    s["accessCount"], s["likesCount"], s['followCount'], s['coinvestorCount'], s['status'],
                    s['value'], s['preMoney'], s['postMoney'], source_cf_id)

    return source_cf_id


def find_source_investor(source, sourceId):
    if sourceId == None or sourceId == '':
        return None
    conn = db.connect_torndb()
    investor = conn.get('select * from source_investor where source=%s and sourceId =%s', source, sourceId)
    if investor != None:
        source_investor_id = investor['id']
        return source_investor_id

    return None


def insert_source_cf_leader(source_cf_leader):
    s = source_cf_leader
    if s['investorName'] is None or s['investorName'] == '':
        return

    conn = db.connect_torndb()

    sourceCfId = s["sourceCfId"]
    source_cf_leader = conn.get("select * from source_cf_leader where sourceCfId=%s", sourceCfId)
    if source_cf_leader is None:
        sql = "insert source_cf_leader(" \
              "sourceCfId, investorName, investorType, sourceInvestorId, description, investment," \
              "valuation, businessDesc, reason, risk, " \
              "createTime, modifyTime) \
              values(%s,%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s," \
              "now(),now())"
        conn.insert(sql,
                    sourceCfId, s["investorName"], s["investorType"], s['sourceInvestorId'], s["description"],
                    s["investment"],
                    s['valuation'], s["businessDesc"], s["reason"], s["risk"],
                    )
    else:
        sql = "update source_cf_leader set" \
              " investorName=%s, investorType=%s , sourceInvestorId=%s, investment=%s, valuation=%s, businessDesc=%s" \
              " where id = %s "
        conn.update(sql, s["investorName"], s["investorType"], s['sourceInvestorId'], s['investment'], s['valuation'],
                    s['businessDesc'],
                    source_cf_leader['id'])


def insert_source_cf_document(source_cf_document):
    s = source_cf_document
    if s['link'] is None or s['link'] == '':
        return

    conn = db.connect_torndb()

    sourceCfId = s["sourceCfId"]
    type = s['type']
    link = s['link']
    sourceId = s['sourceId']

    source_cf_document = conn.get("select * from source_cf_document where sourceCfId=%s and link=%s and type=%s",
                                  sourceCfId, link, type)
    if source_cf_document is None:
        sql = "insert source_cf_document(" \
              "sourceCfId, name, description, link, rank," \
              "sourceId, type," \
              "createTime, modifyTime) \
              values(%s,%s,%s,%s,%s," \
              "%s, %s," \
              "now(),now())"
        conn.insert(sql,
                    sourceCfId, s["name"], s["description"], s["link"], s["rank"],
                    sourceId, s['type']
                    )
    else:
        sql = "update source_cf_document set" \
              " name=%s, description=%s , link=%s, rank=%s, sourceId = %s" \
              " where id = %s "
        conn.update(sql, s["name"], s["description"], s['link'], s['rank'], sourceId,
                    source_cf_document['id'])


def insert_source_cf_member(source_cf_member):
    s = source_cf_member
    conn = db.connect_torndb()
    source_cf_member = conn.get("select * from source_cf_member where source=%s and sourceId=%s",
                                s['source'], s['sourceId'])

    source = s["source"]
    sourceId = s["sourceId"]
    photo_url = s["photo_url"]

    photo_id = None
    if photo_url is not None and photo_url.strip() != "":
        photo_id = get_logo_id(source, sourceId, "member", photo_url)

    if source_cf_member is None:
        sql = "insert source_cf_member(sourceCfId, name, photo,location,role," \
              "description,education,work,source,sourceId," \
              "createTime,modifyTime) \
                values(%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "now(),now())"
        conn.insert(sql,
                    s['sourceCfId'], s["name"], photo_id, s['location'], s['role'],
                    s['description'], s['education'], s['work'], s['source'], s['sourceId'])
    else:
        sql = "update source_member set name=%s,photo=%s, location=%s,role=%s,description=%s,\
                education=%s,work=%s,modifyTime=now() where id=%s"
        conn.update(sql,
                    s["name"], photo_id, s['location'], s['role'], s['description'],
                    s['education'], s['work'], source_cf_member["id"])

    conn.close()


def update_source_cf_desc(cf_key, desc):
    conn = db.connect_torndb()
    source_cf_id = conn.update('update source_crowdfunding set description = %s where sourceId = %s', desc, cf_key)
    conn.close()

    return source_cf_id
