# -*- coding: utf-8 -*-
import os, sys
import time
import json
from kafka import (KafkaClient, SimpleProducer)
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import config, db, util, name_helper

#logger
loghelper.init_logger("merge_investor", stream=True)
logger = loghelper.get_logger("merge_investor")

scores = {"description":1, "website":1, "logo":1, "field":1, "stage":0.5}

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
    msg = {"type":"investor", "id":investorId , "action":action, "from": "bamy"}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("search_investor", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)

def insert_investor_alias(investorId, selected_investorId):
    conn = db.connect_torndb()
    investor_aliaes = conn.query("select * from investor_alias where investorId=%s and (active is null or active!='N')",
                                 investorId)
    for investor in investor_aliaes:
        # investor = conn.get("select * from investor where id=%s",investorId)
        ia = conn.get("select * from investor_alias where name=%s and investorId=%s and "
                      "(active is null or active!='N') limit 1",
                      investor["name"], selected_investorId)
        if ia is None:
            chinese, is_company = name_helper.name_check(investor["name"])
            if is_company:
                type = 12010
            else:
                type = 12020
            sql = "insert investor_alias(investorId, name, type, createTime,modifyTime) values(%s,%s,%s, now(),now())"
            logger.info("Add new investor alias: %s for %s", investor["name"], selected_investorId)
            conn.insert(sql, selected_investorId, investor["name"], type)
    conn.close()

def update_funding_rel(investorId, selected_investorId):
    conn = db.connect_torndb()
    fs = conn.query("select * from funding_investor_rel where investorId=%s", investorId)
    for f in fs:
        f1 = conn.get("select * from funding_investor_rel where fundingId=%s and investorId=%s and "
                      "(active is null or active !='N')", f["fundingId"], selected_investorId)
        if f1 is None:
            conn.update("update funding_investor_rel set investorId=%s where id=%s", selected_investorId, f["id"])
            logger.info("Update funding_rel: %s with %s <-> %s", f["id"], investorId, selected_investorId)
        else:
            conn.execute("delete from funding_investor_rel where id=%s", f["id"])
            logger.info("Remove funding_rel: %s since dup", f["id"])
    conn.close()

def choose(investorIds):
    #选择哪个合并哪个
    id_remain = None
    max = 0
    for investorId in investorIds:
        if id_remain is None:
            id_remain = investorId
        conn = db.connect_torndb()
        investor = conn.get("select * from investor where id=%s", investorId)
        try:
            logger.info(json.dumps(investor, ensure_ascii=False, cls=util.CJsonEncoder))
        except:
            pass
        score = 0
        for column in scores:
            if investor[column] is not None and investor[column].strip() != "":
                score += scores[column]
        if investor["online"] == "Y":
            score += 100
        if score > max:
            max = score
            id_remain = investorId
        conn.close()

    logger.info("Remain id : %s from %s", id_remain, ";".join(investorIds))
    return id_remain

def update_investors(investorId, selected_investorId):
    conn = db.connect_torndb()
    funds = conn.query("select * from funding where (active is null or active='Y') and investors is not null")
    for fund in funds:
        if fund["investors"].strip() == "" or fund["investors"].strip() == "[]":continue
        # logger.info("here is investors: %s",fund["investors"])
        investors_raw = fund["investors"]
        investors = investors_raw.replace("[", "").replace("]", "").replace("},", "}##").split("##")
        investors_raw_new = investors_raw
        update = False
        for investor in investors:
            try:
                j = json.loads(investor)
            except:
                logger.info("here is investors: %s", fund["investors"])
                logger.info("%s", investor)
                logger.info("%s -> %s", investors_raw, fund["id"])
                exit()
            if j.has_key("id") is True and j.has_key("type") is True and j["type"] == "investor":
                if j["id"] == int(investorId):
                    update = True

        if update is True:
            logger.info("investor : %s should change to %s", investorId, selected_investorId)
            logger.info("old: %s", investors_raw)
            idstr = "\"id\":"
            investors_raw_new = investors_raw.replace(idstr+str(investorId), idstr+str(selected_investorId))
            logger.info("new: %s", investors_raw_new)
            conn.update("update funding set investors =%s where id =%s", investors_raw_new, fund["id"])

    conn.close()

def copy_news(investorId, selected_investorId):

    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    newes = list(collection_news.find({"investorIds": int(investorId)}))
    logger.info("***************find %s news", len(newes))
    for news in newes:
         if int(selected_investorId) not in news["investorIds"]:
            collection_news.update_one({"_id": news["_id"]}, {'$addToSet': {"investorIds": int(selected_investorId)}})
    mongo.close()


def merge_investor(investorIds):
    logger.info("begin merge_investor: %s" , "<->".join(investorIds))
    selected_investorId = choose(investorIds)
    logger.info("choose merge_investor: %s", selected_investorId)

    for investorId in investorIds:
        if investorId == selected_investorId:
            continue
        insert_investor_alias(investorId, selected_investorId)
        update_funding_rel(investorId, selected_investorId)
        update_investors(investorId, selected_investorId)
        copy_news(investorId, selected_investorId)

        logger.info("Dup investor, remove %s", investorId)
        conn = db.connect_torndb()
        conn.update("update source_investor set investorId=%s where investorId=%s", selected_investorId, investorId)
        conn.update("update investor set active='N',modifyTime=now(),modifyUser=139 where id=%s", investorId)
        conn.close()

        send_message(investorId, "delete")

    return selected_investorId

def get_investor(investorId):
    conn = db.connect_torndb()
    investor = conn.get("select * from investor where id=%s and (active is null or active='Y')",investorId)
    conn.close()
    if investor is None:
        return None
    return investorId

if __name__ == "__main__":
    # update_investors(9999,121)
    if len(sys.argv) > 2:
        investorId1 = sys.argv[1]
        investorId2 = sys.argv[2]

        merge_investor([investorId1, investorId2])
    else:
        while True:
            conn = db.connect_torndb()
            ts = conn.query("select * from audit_reaggregate_investor where type=1 and processStatus=1")
            for t in ts:
                logger.info("Get request for databaseid: %s ------->  %s", t["id"], t["beforeProcess"])
                beforeProcess = t["beforeProcess"]
                codes = beforeProcess.replace(","," ").replace(";"," ").split(" ")
                if len(codes) <= 1:
                    conn.update("update audit_reaggregate_investor set processStatus=2 where id=%s", t["id"])
                    continue
                investorIds = [code for code in codes if get_investor(code) is not None]
                logger.info("Existed investors for databaseid: %s ------->  %s", t["id"], " ".join(investorIds))
                if len(investorIds) <= 1:
                    conn.update("update audit_reaggregate_investor set processStatus=2 where id=%s", t["id"])
                    continue

                select_investorId = merge_investor(investorIds)
                conn.update("update audit_reaggregate_investor set processStatus=2, afterProcess=%s where id=%s", select_investorId, t["id"])
            conn.close()

            time.sleep(10)

