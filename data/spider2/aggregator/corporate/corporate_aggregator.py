# -*- coding: utf-8 -*-
import os, sys
import time, datetime
from pypinyin import pinyin, lazy_pinyin
import pypinyin
import re, random
import pymongo
from kafka import (KafkaClient, SimpleProducer)
import find_company
import json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import name_helper
import db
import image_helper
import oss2_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
# import aggregator_db_util
import helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../score'))
import score_util
# import corporate_util


#logger
loghelper.init_logger("corporate_aggregate", stream=True)
logger = loghelper.get_logger("corporate_aggregate")

# kafka
kafkaProducer = None

oss2put = oss2_helper.Oss2Helper()


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
    msg = {"type":"company", "id":company_id , "action":action, "from": "bamy"}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("aggregator_v2", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)


def send_message_task(company_id, action, source, noupdate):
    if kafkaProducer is None:
        init_kafka()

    #action: create, delete
    msg = {"source":action, "id":company_id , "detail":source, "no_update": False, "from":"bamy"}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("task_company", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)

def update_corporate(company_id):

    logger.info("company_id: %s" % company_id)
    conn = db.connect_torndb()

    company = conn.get("select * from company where id=%s", company_id)
    if company["corporateId"] is None:
        corporate_id = insert_corporate(company)
    else:
        corporate_id = company["corporateId"]
        # aggregator_db_util.update_corporate(company_id, company["corporateId"])
        update_column(company_id, corporate_id)

    conn.close()
    return corporate_id

def add_corporate_alias(source_company_id, company_id, corporate_id):
    conn = db.connect_torndb()
    corporate_aliases = conn.query("select * from company_alias where companyId=%s and type=12010", company_id)
    for s in corporate_aliases:
        if s["name"] is None or s["name"].strip() == "":
            continue
        name = s["name"].strip()
        alias = conn.get("select * from corporate_alias where corporateId=%s and name=%s limit 1",
                         corporate_id, name)
        if alias is None:
            sql = "insert corporate_alias(corporateId,name,type,active,createTime,modifyTime) \
                    values(%s,%s,%s,%s,now(),now())"
            conn.insert(sql, corporate_id, name, s["type"], 'Y')

    if source_company_id is not None:
        corporate_aliases_2 = conn.query("select * from source_company_name where sourceCompanyId=%s and "
                                         " type=12010", source_company_id)
        for s in corporate_aliases_2:
            if s["name"] is None or s["name"].strip() == "":
                continue
            name = s["name"].strip()
            alias = conn.get("select * from corporate_alias where corporateId=%s and name=%s limit 1",
                             corporate_id, name)
            if alias is None:
                sql = "insert corporate_alias(corporateId,name,type,active,createTime,modifyTime) \
                            values(%s,%s,%s,%s,now(),now())"
                conn.insert(sql, corporate_id, name, s["type"], 'Y')
    conn.close()

def add_corporate_alias_new(source_company_id, company_id, corporate_id):
    conn = db.connect_torndb()

    if source_company_id is not None:
        corporate_aliases_2 = conn.query("select * from source_company_name where sourceCompanyId=%s and "
                                         " type=12010", source_company_id)
        for s in corporate_aliases_2:
            if s["name"] is None or s["name"].strip() == "":
                continue
            name = s["name"].strip()
            alias = conn.get("select * from corporate_alias where corporateId=%s and name=%s limit 1",
                             corporate_id, name)
            if alias is None:
                sql = "insert corporate_alias(corporateId,name,active,createTime,modifyTime) \
                            values(%s,%s,%s,now(),now())"
                conn.insert(sql, corporate_id, name, 'Y')
    conn.close()


def add_funding_corporateId(company_id, corporate_id):
    conn = db.connect_torndb()
    conn.update("update funding set corporateId=%s where companyId=%s", corporate_id, company_id)
    conn.close()


def set_corporateId(company_id, corporate_id):
    conn = db.connect_torndb()
    conn.update("update company set corporateId=%s where id=%s", corporate_id, company_id)
    conn.close()


def insert_corporate(s):

    conn = db.connect_torndb()
    sql = "insert corporate(code,name,fullName,website,brief,description,round,roundDesc,corporateStatus,fundingType,currentRound,currentRoundDesc, \
           preMoney,investment,postMoney,shareRatio,currency,headCountMin,headCountMax,locationId,address,phone,establishDate,logo, \
           verify,active,createTime,modifyTime) \
           values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"

    corporate_id = conn.insert(sql,
                                s["code"], s["name"], s["fullName"], s["website"], s["brief"], s["description"], -1, s["roundDesc"],
                                s["companyStatus"], s["fundingType"], s["currentRound"], s["currentRoundDesc"],s["preMoney"], s["investment"],
                                s["postMoney"], s["shareRatio"], s["currency"], s["headCountMin"], s["headCountMax"], s["locationId"], s["address"],
                                s["phone"], s["establishDate"], s["logo"], s["verify"], 'A'
                                )
    conn.close()
    return corporate_id


def update_column(company_id, corporate_id):
    columns = [
        "fullName",
        "round",
        "establishDate",
        "locationId",
    ]

    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", company_id)
    corporate = conn.get("select * from corporate where id=%s", corporate_id)
    if company is not None and corporate is not None:
        for column in columns:
            sql = "update corporate set " + column + "=%s where id=%s"
            if (corporate[column] is None and company[column] is not None):
               # (corporate[column] is not None and company[column] is not None and company[column]!=corporate[column]):
                conn.update(sql, company[column], corporate_id)
    conn.close()

def insert_company(code, source_company, test):
    table_names = helper.get_table_names(test)
    s = source_company
    conn = db.connect_torndb()
    sql = "insert " + table_names["company"] + "(code,name,fullName,description,brief,\
        productDesc, modelDesc, operationDesc, teamDesc, marketDesc, compititorDesc, advantageDesc, planDesc, \
        round,roundDesc,companyStatus,fundingType,preMoney,currency,\
        locationId,address,phone,establishDate,logo,type,\
        headCountMin,headCountMax,\
        active,createTime,modifyTime) \
        values(%s,%s,%s,%s,%s,\
            %s,%s,%s,%s,%s,%s,%s,%s, \
            %s,%s,%s,%s,%s,%s,\
            %s,%s,%s,%s,%s,%s,\
            %s,%s,\
            %s,now(),now())"
    company_id = conn.insert(sql,
            code,s["name"],s["fullName"],s["description"],s["brief"],
            s.get("productDesc"), s.get("modelDesc"), s.get("operationDesc"), s.get("teamDesc"), s.get("marketDesc"), s.get("compititorDesc"), s.get("advantageDesc"), s.get("planDesc"),
            s["round"],s["roundDesc"],s["companyStatus"],s["fundingType"],s["preMoney"],s["currency"],
            s["locationId"],s["address"],s["phone"],s["establishDate"],s["logo"],s["type"],
            s["headCountMin"],s["headCountMax"],
            'A')

    if not test:
        conn.update("update source_company set companyId=%s where id=%s", company_id, s["id"])

    conn.close()
    return company_id

def insert_company_new(code, source_company, test):
    table_names = helper.get_table_names(test)
    s = source_company
    conn = db.connect_torndb()
    sql = "insert " + table_names["company"] + "(code,name,description,brief,\
        companyStatus,logo,active,createTime,modifyTime) \
        values(%s,%s,%s,%s,\
            %s,%s,%s,\
            now(),now())"
    company_id = conn.insert(sql,
            code,s["name"],s["description"],s["brief"],
            s["companyStatus"],s["logo"],
            'A')

    if not test:
        conn.update("update source_company set companyId=%s where id=%s", company_id, s["id"])

    conn.close()
    return company_id

def insert_corporate_new(source_company, company_id):
    s = source_company
    conn = db.connect_torndb()
    sql = "insert corporate(name,fullName,round,\
        locationId,establishDate,active,createTime,modifyTime) \
        values(%s,%s,%s,\
            %s,%s,%s,\
            now(),now())"
    corporate_id = conn.insert(sql,
            s["name"],s["fullName"],-1,
            s["locationId"],s["establishDate"],
            'A')

    conn.close()
    return corporate_id

def insert_company_dev(code, source_company, test):
    table_names = helper.get_table_names(test)
    s = source_company
    conn = db.connect_torndb()
    sql = "insert " + table_names["company"] + "(code,name,fullName,description,brief,\
        productDesc, modelDesc, operationDesc, teamDesc, marketDesc, compititorDesc, advantageDesc, planDesc, \
        round,roundDesc,companyStatus,fundingType,preMoney,currency,\
        locationId,address,phone,establishDate,logo,type,\
        headCountMin,headCountMax,\
        active,createTime,modifyTime) \
        values(%s,%s,%s,%s,%s,\
            %s,%s,%s,%s,%s,%s,%s,%s, \
            %s,%s,%s,%s,%s,%s,\
            %s,%s,%s,%s,%s,%s,\
            %s,%s,\
            %s,now(),now())"
    company_id = conn.insert(sql,
            code,s["name"],s["fullName"],s["description"],s["brief"],
            s.get("productDesc"), s.get("modelDesc"), s.get("operationDesc"), s.get("teamDesc"), s.get("marketDesc"), s.get("compititorDesc"), s.get("advantageDesc"), s.get("planDesc"),
            s["round"],s["roundDesc"],s["companyStatus"],s["fundingType"],s["preMoney"],s["currency"],
            s["locationId"],s["address"],s["phone"],s["establishDate"],s["logo"],s["type"],
            s["headCountMin"],s["headCountMax"],
            'A')

    conn.close()
    return company_id

def get_logo_stock(stockname, code, source):
    name = None
    height = None
    width = None
    if stockname is not None and code is not None:
        logger.info("prepare logo: %s|%s", stockname, code)
        # (image_value, width, height) = download_crawler.get_image_size(logo_url)
        im,image = image_helper.gen_stock_image(stockname, code)
        name = str(source)+"-"+code
        logger.info("%s|%s", name,image)

        headers = {"Content-Type": "image/jpeg"}
        oss2put.put(name, image.getvalue(), headers=headers)
    return (name, width, height)



def patch_logo(companyId,source,sourceId,stockname):

    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s",companyId)
    if company["logo"] is None:
        logger.info("patch logo for %s|%s", stockname, companyId)
        logoName,h,w = get_logo_stock(stockname,sourceId,source)
        if logoName is not None:
            conn.update("update company set logo=%s where id=%s",logoName,companyId)
            # exit()
    conn.close()
    # exit()

def patch_company_establish_date(corporate_id):
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection_gongshang = mongo.info.gongshang

    establish_date = None
    # logger.info("checking esdate: %s", corporate_id)
    corporate = conn.get("select * from corporate where id=%s", corporate_id)
    if corporate is not None and corporate["fullName"] is not None:
        gongshang = collection_gongshang.find_one({"name": corporate["fullName"]})

        if gongshang is not None and gongshang.has_key("establishTime"):
            try:
                if establish_date is None or (gongshang["establishTime"] is not None and gongshang["establishTime"] != establish_date):
                    establish_date = gongshang["establishTime"]
            except:
                pass

    if establish_date is None:
        aliases = conn.query("select * from corporate_alias where "
                             "(active is null or active !='N') and corporateId=%s", corporate_id)
        for alias in aliases:
            gongshang = collection_gongshang.find_one({"name": alias["name"]})
            if gongshang is not None and gongshang.has_key("establishTime"):
                try:
                    if establish_date is None or (gongshang["establishTime"] is not None and gongshang["establishTime"] != establish_date):
                        establish_date = gongshang["establishTime"]
                except:
                    pass
            if establish_date is not None:
                break

    if establish_date is not None:

        logger.info("Corporate: %s establishDate: %s", corporate_id, establish_date)
        try:
            conn.update("update corporate set establishDate=%s where id=%s", establish_date, corporate_id)
        except:
            pass

    #patch round
    if corporate is not None:
        funding = conn.get("select * from funding where corporateId=%s and (active is null or active !='N') "
                           "order by fundingDate desc limit 1",
                           corporate["id"])
        if funding is not None:
            # corporate = conn.get("select * from corporate where id=%s", corporate_id)
            # if corporate is not None:
            conn.update("update corporate set round=%s where id=%s",
                        funding["round"],  corporate["id"])
        else:
            if corporate["round"] is not None:
                conn.update("update corporate set round=-1 where id=%s", corporate["id"])
    conn.close()
    mongo.close()

def patch_company_location(corporate_id):
    conn = db.connect_torndb()

    corporate = conn.get("select * from corporate where id=%s", corporate_id)

    if corporate is not None and (corporate["locationId"] is None or corporate["locationId"] == 0):
        locationId = None

        alias0 = [{"name":corporate["fullName"]}] if corporate["fullName"] is not None else []
        aliases = conn.query("select * from corporate_alias where corporateId=%s and "
                             "(active is null or active ='Y') and verify='Y'",
                             corporate_id)
        for alias in alias0+aliases:
            # logger.info(alias["name"])
            loc1, loc2 = name_helper.get_location_from_company_name(alias["name"])
            # logger.info("%s/%s",loc1,loc2)
            if loc1 is not None:
                l = conn.get("select *from location where locationName=%s", loc1)
                if l:
                    locationId = l["locationId"]
                    break
        if locationId is not None:
            logger.info("Corporate: %s location: %s", corporate_id, locationId)
            conn.update("update corporate set locationId=%s where id=%s", locationId, corporate_id)
    conn.close()

def check_cor_info():
    conn = db.connect_torndb()
    cs = conn.query("select id from corporate where (active is null or active !='N') and "
                    "locationId is null and modifyTime>%s order by id desc",
                    datetime.datetime.now() - datetime.timedelta(days=3))
    logger.info("missing %s cs location", len(cs))
    for c in cs:
        patch_company_location(c["id"])

    cs2 = conn.query("select id from corporate where (active is null or active !='N') and "
                     "(locationId is not null and locationId<=370) and "
                     "establishDate is null and modifyTime>%s order by id desc",
                     datetime.datetime.now() - datetime.timedelta(days=3))

    logger.info("missing %s cs establishDate", len(cs2))
    for c in cs2:
        patch_company_establish_date(c["id"])
    conn.close()

if __name__ == "__main__":
    # conn = db.connect_torndb()
    # connp = db.connect_torndb_proxy()
    print("here")
    while True:
        # conn = db.connect_torndb()
        connp = db.connect_torndb_proxy()
        logger.info("start active 13020, 13030, 13400, 13401, 13402 and send message to 13050")
        coms = connp.query("select id,corporateId from company where (active='A' or active='P')")
        logger.info("%s coms to check", len(coms))
        for com in coms:
            if com["corporateId"] is None: continue
            c = connp.get("select * from corporate where id=%s", com["corporateId"])
            if c is None: continue
            sourceCompanies = connp.query("select * from source_company where companyId=%s order by source desc",
                                         com["id"])
            activeflag = False

            for sc in sourceCompanies:
                if sc["source"] in [13022, 13030, 13400, 13401, 13402, 13121]:
                    activeflag = True

                if sc["source"] in [13400,13401,13402] and sc["companyId"] is not None:
                    patch_logo(sc["companyId"], sc["source"], sc["sourceId"], sc["name"])
                    # break
                # else:
                #     pass
                    # activeflag = False
                    # break

            if activeflag is True:
                logger.info("active %s", c["id"])
                connp.update("update corporate set active=null where id=%s", c["id"])
                connp.update("update company set active=null where id=%s", com["id"])
                companies = connp.query("select id,logo from company where corporateId=%s", c["id"])
                for company in companies:
                    send_message(company["id"], "create")
                continue

            # lagou part: score and send_message
            if len(sourceCompanies) == 1 and sourceCompanies[0]["source"] == 13050 and \
                 c["createTime"] >=  datetime.datetime.today() - datetime.timedelta(days=1):

                if c["fullName"] is not None and c["fullName"].find("分公司") >= 0: continue
                source_lagou = sourceCompanies[0]
                if source_lagou["companyId"] is None: continue
                company_id = source_lagou["companyId"]

                # score = score_util.get_score(company_id)
                # if score is None:
                #     score = score_util.getCompanyScore(company_id)
                # if score == -1:
                #     # logger.info()
                #     continue
                # score_util.save_score(company_id, score)
                # if score >= 4:
                #     logger.info("company from lagou: %s %s has score: %s go to pub", source_lagou["name"], company_id,
                #                 score)
                #
                #     send_message_task(company_id, "company_newcover", source_lagou["source"],True)
                #     # break

                score = score_util.checkjob(company_id)
                if score > 0:
                    logger.info("company from lagou: %s %s has score: %s go to pub", source_lagou["name"], company_id,
                                score)

                    send_message_task(company_id, "company_job", source_lagou["source"], True)
                    # break
        logger.info("end")
        logger.info("start check 3 days corporate info")
        check_cor_info()
        # connp.close()
        connp.close()
        time.sleep(180)
    pass