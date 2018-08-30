# -*- coding: utf-8 -*-
import os, sys, time
import datetime
import json
from kafka import (KafkaClient, SimpleProducer)
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db
import loghelper
import url_helper
import config
import name_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
import parser_db_util

#logger
loghelper.init_logger("investor_aggregator_13023", stream=True)
logger = loghelper.get_logger("investor_aggregator_13023")

# kafka
kafkaProducer = None

def init_kafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)

init_kafka()


def send_message(investorId, action):
    #action: create, delete
    msg = {"type":"investor", "id":investorId , "action":action}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("search_investor", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)


def replace(investor, source_investor):
    conn = db.connect_torndb()
    columns =  [
                "website",
                "domain",
                "description",
                "logo",
                ]
    flag = False
    for column in columns:
        if source_investor.has_key(column) is True and source_investor[column] is not None and source_investor[column].strip()!="":
            conn.update("update investor set " + column + "=%s where id=%s", source_investor[column], investor["id"])
    conn.close()


def find_in_investor(column, value):
    conn = db.connect_torndb()
    # investor = conn.get("select * from investor where " + column + "=%s and (active is null or active='Y') order by id limit 1", value)
    if column in ["name","fullName"]:
        investor = conn.get("select i.* from investor i join investor_alias ia on "
                            "i.id = ia.investorId  where (i.active is null or i.active='Y') and "
                            "(ia.active is null or ia.active='Y') and ia.name=%s limit 1", value)
        # logger.info("here %s",investor)
    else:
        investor = conn.get(
            "select * from investor where " + column + "=%s and (active is null or active='Y') order by id limit 1",
            value)

    conn.close()
    return investor


def get_android_domain(app_market, app_id):
    domain = None
    if app_market == 16010 or app_market == 16020:
        android_app = parser_db_util.find_android_market(app_market, app_id)
        if android_app:
            domain = android_app["apkname"]
    else:
        domain = app_id
    return domain

def update_investor(investor,source_investor):
    conn = db.connect_torndb()
    investor_id = investor["id"]
    logger.info("****checking %s/%s/%s", investor["name"], investor["id"], source_investor["id"])
    if investor["online"] is not None and investor["online"] == "Y":
        logger.info("online not update!!!")
        time.sleep(1)
        pass
    else:
        logger.info("Update investor : %d with source_investor: %d ", investor_id, source_investor["id"])
        replace(investor, source_investor)


    #insert investor_alias
    for name in [source_investor["name"], source_investor["fullName"],source_investor["enName"], source_investor["enFullName"]]:
        if name is None or name.strip() == "": continue
        investor_alias = conn.get("select * from investor_alias where name=%s and "
                                  "investorId=%s and (active is null or active='Y') limit 1",
                                  name, investor["id"])
        # logger.info("here: %s", investor_alias)
        if investor_alias is None:
            chinese, is_company = name_helper.name_check(name)
            if is_company:
                type = 12010
            else:
                type = 12020
            sql = "insert investor_alias(investorId, name, type, createTime,modifyTime) values(%s,%s,%s, now(),now())"
            logger.info("Add new investor alias: %s for %s", name, investor["id"])
            conn.insert(sql, investor["id"], name, type)

    #insert investor_artifact:
    artifacts = []
    if source_investor["website"] is not None and source_investor["website"] != "":
        type, market, app_id = url_helper.get_market(source_investor["website"])
        if type == 4010:
            if source_investor["website"].find('36kr') > 0 and source_investor["website"].find("baidu") > 0:
                pass
            else:
                artifact = {
                    "investorId": investor["id"],
                    "name": investor["name"] ,
                    "description": None,
                    "link": source_investor["website"],
                    "domain": app_id,
                    "type": type
                }
                artifacts.append(artifact)
        elif (type == 4040 or type == 4050) and app_id is not None:
            domain = get_android_domain(market, app_id)
            if (type == 4040 or type == 4050) and domain is not None:
                artifact = {
                    "investorId": investor["id"],
                    "name": investor["name"] ,
                    "description": None,
                    "link": source_investor["website"],
                    "domain": domain,
                    "type": type
                }
                artifacts.append(artifact)


    weibo = source_investor.get("weibo", "")
    if weibo is not None and weibo.strip() != "" and weibo.find("weibo") >= 0:
        artifact = {
            "investorId": investor["id"],
            "name": investor["name"] ,
            "description": None,
            "link": weibo,
            "domain": None,
            "type": 4030
        }
        artifacts.append(artifact)

    weixin = source_investor.get("wechatId", "")
    if weixin is not None and weixin.strip() != "":
        artifact = {
            "investorId": investor["id"],
            "name": investor["name"] ,
            "description": None,
            "link": weixin,
            "domain": weixin,
            "type": 4020
        }
        artifacts.append(artifact)

    if len(artifacts) > 0:
        for art in artifacts:
            if art["type"] not in [4030] and art["domain"] is not None and art["domain"].strip()!="":

                iart = conn.get("select * from investor_artifact where type=%s and investorId=%s and domain=%s limit 1",
                            art["type"], investor["id"], art["domain"])
            else:
                iart = conn.get("select * from investor_artifact where type=%s and investorId=%s and link=%s limit 1",
                                art["type"], investor["id"], art["link"])

            if iart is None:
                logger.info("add new artifact: %s/%s/%s", art["type"], art["name"], art["link"])
                sql = "insert investor_artifact(investorId,type, name, link, domain, createTime,modifyTime) \
                                         values(%s,%s,%s,%s,%s,now(),now())"
                conn.insert(sql, investor["id"], art["type"], art["name"], art["link"], art["domain"])


    #insert contact

    contacts = conn.query("select * from source_investor_contact where sourceInvestorId=%s", source_investor["id"])
    if len(contacts) >0:
        conn.execute("delete from investor_contact where investorId=%s and createUser=139", investor["id"])
        for s in contacts:
            sql = "insert investor_contact(investorId, locationId, address, phone, email, createUser, " \
                  "createTime,modifyTime) \
                              values(%s,%s,%s,%s,%s,%s,now(),now())"
            conn.insert(sql, investor["id"], s["locationId"], s["address"], s["phone"], s["email"], 139)


    # insert member
    members = conn.query("select * from source_investor_member where sourceInvestorId=%s", source_investor["id"])
    for m in members:
        member = conn.get("select * from investor_member where investorId=%s and name=%s limit 1", investor["id"], m["name"])
        if member is not None: continue
        sql = "insert investor_member(investorId,name,logo, position, description,createUser,createTime,modifyTime) \
                              values(%s,%s,%s,%s,%s,%s,now(),now())"
        conn.insert(sql, investor["id"], m["name"], m["logo"], m["position"],
                    m["description"], 139)
    conn.close()


def set_investorId(investorId, id):
    conn = db.connect_torndb()
    sql = "insert investor_source_rel(investorId, sourceInvestorId, createTime,modifyTime) " \
          "values(%s,%s, now(),now())"
    # logger.info("Add new investor alias: %s for %s", source_investor["name"], investor["id"])
    conn.insert(sql, investorId, id)
    conn.close()

def set_processStatus(id):
    conn = db.connect_torndb()
    sql = "update source_investor set processStatus=2, modifyTime=now() where id=%s"
    conn.update(sql,id)
    conn.close()

def set_processStatus_1(id):
    conn = db.connect_torndb()
    sql = "update source_investor set processStatus=1, modifyTime=now() where id=%s"
    conn.update(sql,id)
    conn.close()

def update_domain_website():
    conn = db.connect_torndb()
    arts = conn.query("select * from investor where (active ='Y' or active is null) and "
                      "domain is null and website is not null")
    for art in arts:
        (linktype,appmarket , domain) = url_helper.get_market(art["website"])
        if domain is not None:
            sql = "update investor set domain=%s where id=%s"
            conn.update(sql, domain, art["id"])
    conn.close()

def find_investor_source_rel(source_investor_id):
    conn = db.connect_torndb()
    rel = conn.get("select isr.* from investor i join investor_source_rel isr on "
                     "i.id = isr.investorId  where (i.active is null or i.active='Y') and "
                     "(isr.active is null or isr.active='Y') and isr.sourceInvestorId=%s limit 1", source_investor_id)
    if rel is None:
        investorId = None
    else:
        investorId = rel["investorId"]
    conn.close()
    return investorId


if __name__ == '__main__':

    while True:
        logger.info("investor aggregator start")
        update_domain_website()
        #get source_investors
        conn = db.connect_torndb()
        #Check verify or processStatus

        investor_source_rels = conn.query("select * from investor_source_rel where (active is null or active !='N')"
                                          )

        for isr in investor_source_rels:
            investor = conn.get("select * from investor where id=%s", isr["investorId"])
            source_investor = conn.get("select * from source_investor where id=%s", isr["sourceInvestorId"])
            update_investor(investor, source_investor)
        break


        source_investors = conn.query("select * from source_investor where processStatus=0 and source=13023 "
                                      "order by id")
        conn.close()

        for source_investor in source_investors:
            logger.info("checking source_investor: %s/%s", source_investor["name"], source_investor["id"])
            #get Domain
            domain = None
            if source_investor["website"] is not None:
                source_investor["website"] = url_helper.url_normalize(source_investor["website"])
                type, market, website_domain = url_helper.get_market(source_investor["website"])
                if type == 4010 and website_domain is not None:
                    domain = website_domain

            investorId = find_investor_source_rel(source_investor["id"])
            if investorId is not None:
                logger.info("already matched investor: %s", investorId)
                # investor = find_in_investor("id",source_investor["investorId"])
                # update_investor(investor,source_investor)
                set_processStatus(source_investor["id"])
                continue

            else:
                #name check
                fullname = source_investor["fullName"]
                if fullname is not None and fullname.strip() != "":
                    investor = find_in_investor("fullName",fullname)
                    if investor:
                        logger.info("fullName is same in investor : %d with source_investor: %d ", investor["id"],source_investor["id"])
                        # update_investor(investor, source_investor)
                        set_investorId(investor["id"], source_investor["id"])
                        set_processStatus(source_investor["id"])
                        continue

                #website check
                website = source_investor["website"]
                if website is not None and website.strip() != "":
                    investor = find_in_investor("website",website)
                    if investor:
                        # update_investor(investor, source_investor)
                        logger.info("website is same in investor : %d with source_investor: %d ", investor["id"],source_investor["id"])
                        set_investorId(investor["id"], source_investor["id"])
                        set_processStatus(source_investor["id"])
                        continue

                #Domain check

                if domain is not None and domain.strip() != "":
                    investor = find_in_investor("domain",domain)
                    if investor:
                        logger.info("domain is same in investor : %d with source_investor: %d ", investor["id"],source_investor["id"])
                        # update_investor(investor, source_investor)
                        set_investorId(investor["id"], source_investor["id"])
                        set_processStatus(source_investor["id"])
                        continue

                name = source_investor["name"]
                if name is not None and name.strip() != "":
                    investor = find_in_investor("name", name)
                    if investor:
                        logger.info("name is same in investor : %d with source_investor: %d ", investor["id"],
                                    source_investor["id"])
                        # update_investor(investor, source_investor)
                        set_investorId(investor["id"], source_investor["id"])
                        set_processStatus(source_investor["id"])
                        continue

            #insert new investor
            # if source_investor["name"] is not None and source_investor["name"].strip() != "":
            #     investor_id = insert_investor(source_investor)
            #     set_investorId(investor_id, source_investor["id"])
            set_processStatus_1(source_investor["id"])


            # break
        #break

        logger.info("investor aggregator end.")
        time.sleep(30*60)


