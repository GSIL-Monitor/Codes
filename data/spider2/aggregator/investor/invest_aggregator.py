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


#logger
loghelper.init_logger("investor_aggregator", stream=True)
logger = loghelper.get_logger("investor_aggregator")

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
    columns =  ["name",
                "website",
                "domain",
                "description",
                "logo",
                "stage",
                "field",
                "type"]
    flag = False
    for column in columns:
        if column == "type":
            if (investor.has_key(column) == False or investor[column] is None or investor[column] == "") and (source_investor.has_key(column) and source_investor[column] is not None and source_investor[column] != ""):
                investor[column] = source_investor[column]
                flag = True
        else:
            if (investor.has_key(column) == False or investor[column] is None or investor[column].strip() == "") and (source_investor.has_key(column) and source_investor[column] is not None and source_investor[column].strip() != ""):
                investor[column] = source_investor[column]
                flag = True
    return flag


def find_in_investor(column, value):
    conn = db.connect_torndb()
    investor = conn.get("select * from investor where " + column + "=%s and (active is null or active='Y') order by id limit 1", value)
    if column == "name" and investor is None:
        investor_alias =  conn.get("select * from investor_alias where name=%s and (active is null or active='Y') limit 1",value)
        if investor_alias is not None:
            investor = conn.get("select * from investor where id=%s and (active is null or active='Y')", investor_alias["investorId"])
    conn.close()
    return investor

def insert_investor(investor):
    conn = db.connect_torndb()
    sql = "insert investor(name,website,domain,description,logo,stage,field,type,\
           createTime,modifyTime) values(%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"
    investor_id =conn.insert(sql,investor["name"],investor["website"],investor["domain"],investor["description"],
                    investor["logo"],investor["stage"],investor["field"],investor["type"])
    conn.close()
    logger.info("insert investor : %d with source_investor: %d", investor_id,investor["id"])
    send_message(investor_id, "create")
    return investor_id


def update_investor(investor,source_investor):
    conn = db.connect_torndb()
    investor_id = investor["id"]
    if replace(investor, source_investor):
        logger.info("Update investor : %d with source_investor: %d ", investor_id, source_investor["id"])
        sql =  "update investor set name=%s,website=%s,domain=%s,description=%s,logo=%s,stage=%s,\
            field=%s,type=%s,modifyTime=now() where id=%s"
        conn.update(sql, investor["name"],investor["website"],investor["domain"],investor["description"],
                     investor["logo"],investor["stage"],investor["field"],investor["type"],investor_id)
    else:
        logger.info("Not update investor : %d with source_investor: %d ", investor_id, source_investor["id"])

    #insert investor_alias
    investor_alias = conn.get("select * from investor_alias where name=%s and (active is null or active='Y') limit 1", source_investor["name"])
    if investor_alias is not None:
        chinese, is_company = name_helper.name_check(investor["name"])
        if is_company:
            type = 12010
        else:
            type = 12020
        sql = "insert investor_alias(investorId, name, type, createTime,modifyTime) values(%s,%s,%s, now(),now())"
        logger.info("Add new investor alias: %s for %s", source_investor["name"], investor["id"])
        conn.insert(sql, investor["id"], source_investor["name"], type)
    conn.close()

def set_investorId(investorId, id):
    conn = db.connect_torndb()
    sql = "update source_investor set investorId=%s where id=%s"
    conn.update(sql,investorId,id)
    conn.close()

def set_processStatus(id):
    conn = db.connect_torndb()
    sql = "update source_investor set processStatus=2, modifyTime=now() where id=%s"
    conn.update(sql,id)
    conn.close()



if __name__ == '__main__':

    while True:
        logger.info("investor aggregator start")
        #get source_investors
        conn = db.connect_torndb()
        #Check verify or processStatus
        source_investors = conn.query("select * from source_investor where processStatus=0 order by id")
        conn.close()

        for source_investor in source_investors:
            logger.info(source_investor["id"])
            #get Domain
            source_investor["domain"] = None
            if source_investor["website"] is not None:
                source_investor["website"] = url_helper.url_normalize(source_investor["website"])
                type, market, website_domain = url_helper.get_market(source_investor["website"])
                if type == 4010 and website_domain is not None:
                    source_investor["domain"] = website_domain

            if source_investor["investorId"] is not None:

                investor = find_in_investor("id",source_investor["investorId"])
                update_investor(investor,source_investor)
                set_processStatus(source_investor["id"])
                continue

            else:
                #name check
                name = source_investor["name"]
                if name is not None and name.strip != "":
                    investor = find_in_investor("name",name)
                    if investor:
                        logger.info("name is same in investor : %d with source_investor: %d ", investor["id"],source_investor["id"])
                        update_investor(investor, source_investor)
                        set_investorId(investor["id"], source_investor["id"])
                        set_processStatus(source_investor["id"])
                        continue

                #website check
                website = source_investor["website"]
                if website is not None and website.strip != "":
                    investor = find_in_investor("website",website)
                    if investor:
                        update_investor(investor, source_investor)
                        logger.info("website is same in investor : %d with source_investor: %d ", investor["id"],source_investor["id"])
                        set_investorId(investor["id"], source_investor["id"])
                        set_processStatus(source_investor["id"])
                        continue

                #Domain check
                domain = source_investor["domain"]
                if domain is not None and domain.strip != "":
                    investor = find_in_investor("domain",domain)
                    if investor:
                        logger.info("domain is same in investor : %d with source_investor: %d ", investor["id"],source_investor["id"])
                        update_investor(investor, source_investor)
                        set_investorId(investor["id"], source_investor["id"])
                        set_processStatus(source_investor["id"])
                        continue

            #insert new investor
            if source_investor["name"] is not None and source_investor["name"].strip() != "":
                investor_id = insert_investor(source_investor)
                set_investorId(investor_id, source_investor["id"])
            set_processStatus(source_investor["id"])


            #break
        #break

        logger.info("investor aggregator end.")
        time.sleep(30*60)


