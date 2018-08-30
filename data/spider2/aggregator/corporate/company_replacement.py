# -*- coding: utf-8 -*-
# corporate分拆或合并后替换原有的company
import os, sys
import time, datetime
import json
from kafka import (KafkaClient, SimpleProducer)

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper
import db
import config

#logger
loghelper.init_logger("company_replacement", stream=True)
logger = loghelper.get_logger("company_replacement")

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


def send_task_message(company_id, comments):
    if kafkaProducer is None:
        init_kafka()

    n = datetime.datetime.now()
    msg = {"source":"company_split", "id": company_id, "detail": comments,
           "posting_time": n.strftime('%Y-%m-%d %H:%M:%S')}
    while True:
        try:
            kafkaProducer.send_messages("task_company", json.dumps(msg))
            logger.info(msg)
            break
        except Exception,e :
            logger.exception(e)
            time.sleep(60)
            init_kafka()


def get_all_corporate_decompose_tasks():
    mongo = db.connect_mongo()
    corporate_decompose_tasks = mongo.task.corporate_decompose.find({"processStatus":2})
    mongo.close()
    return corporate_decompose_tasks


def get_all_corporate_reaggregate_tasks():
    mongo = db.connect_mongo()
    corporate_reaggregate_tasks = mongo.task.corporate_reaggregate.find({"processStatus": 0})
    mongo.close()
    return corporate_reaggregate_tasks


def replacement_company(oldCompanyId, newCompanyId, decompose=False):
    logger.info("oldCompanyId: %s, newCompanyId: %s", oldCompanyId, newCompanyId)

    mysql_tables = [
        {
            "table":"audit_investor_company",
            "field":"investorId"
        },
        {
            "table":"collection_company_rel",
            "field":"collectionId"
        },
        {
            "table":"companies_rel",
            "field":"company2Id"
        },
        {
            "table":"company_fa",
            "field": None
        },
        {
            "table":"company_fa_candidate",
            "field":"companyFaId"
        },
        {
            "table":"comps_company_rel",
            "field":"compsId"
        },
        # {
        #     "table":"contest_company",
        #     "field":"contestId"
        # },
        {
            "table":"deal",
            "field":"organizationId"
        },
        {
            "table":"company_recruitment_rel",
            "field":"jobCompanyId"
        },
        {
            "table":"mylist_company_rel",
            "field":"mylistId"
        },
        {
            "table":"recommendation",
            "field":"userId"
        },
        {
            "table":"user_default_company_rel",
            "field":"userId"
        },
        {
            "table":"topic_company",
            "field":"topicId"
        },
        {
            "table":"user_company_subscription",
            "field":"userId"
        },
        {
            "table":"company_message",
            "field": None
        },
        # tags need generate again
        # {
        #     "table": "company_tag_rel",
        #     "field": "tagId"
        # },
        {
            "table": "industry_company",
            "field": "industryId"
        },
        {
            "table": "org_track_company",
            "field": "orgId"
        },
        # "user_company_request", # TODO
        {
            "table": "digital_token",
            "field": None
        },
    ]

    if decompose is False:
        mysql_tables.append({
            "table":"source_company",
            "field": None
        })

    # topic_message relateId
    # company_message relateId
    mysql_tables2 = [
        "topic_message",
        "company_message"
    ]

    mongo_tables = [
        "company.correct",
        "task.company",
        "company.funding"
        # "track.track"
    ]

    conn = db.connect_torndb()
    for t in mysql_tables:
        logger.info("mysql table: %s", t["table"])
        items = conn.query("select * from " + t["table"] + " where companyId=%s", oldCompanyId)
        for item in items:
            _item = None
            if t["field"] is not None:  # if replacement exist
                _item = conn.get("select * from " + t["table"] + " where companyId=%s and " +
                                 t["field"] + "=%s limit 1",
                                 newCompanyId, item[t["field"]])
            if _item is None:
                logger.info("update " + t["table"] + " set companyId=%s where id=%s", newCompanyId, item["id"])
                conn.update("update " + t["table"] + " set companyId=%s where id=%s", newCompanyId, item["id"])

    for t in mysql_tables2:
        logger.info("mysql table: %s", t)
        items = conn.query("select * from " + t + " where relateType=3060 and relateId=%s", str(oldCompanyId))
        for item in items:
            logger.info("update " + t + " set relateId=%s where id=%s", str(newCompanyId), item["id"])
            conn.update("update " + t + " set relateId=%s where id=%s", str(newCompanyId), item["id"])

    conn.close()

    mongo = db.connect_mongo()
    for t in mongo_tables:
        logger.info("mongo table: %s", t)
        db_name, table_name = t.split(".")
        c = mongo[db_name][table_name]
        items = c.find({"companyId": oldCompanyId})
        for item in items:
            logger.info('{"_id":%s}, {"$set":{"companyId":%s}}', item["_id"], newCompanyId)
            c.update_one({"_id":item["_id"]}, {"$set":{"companyId":newCompanyId}})

    # task.news companyIds替换
    tasks = mongo.task.news.find({"companyIds": oldCompanyId})
    for task in tasks:
        mongo.task.news.update_one({"_id":task["_id"]}, {"$pull":{"companyIds":oldCompanyId}})
        mongo.task.news.update_one({"_id":task["_id"]}, {"$addToSet": {"companyIds": newCompanyId}})
    mongo.close()

    conn = db.connect_torndb()
    new_company = conn.get("select * from company where id=%s", newCompanyId)
    if new_company["corporateId"] is not None:
        conn.update("update corporate set active='Y' where id=%s", new_company["corporateId"])
    conn.update("update company set active='Y' where id=%s", newCompanyId)
    conn.update("update company set active='N' where id=%s", oldCompanyId)

    conn.execute("delete from company_tag_rel where companyId=%s and (verify is null or verify='N')", newCompanyId)
    conn.close()
    send_message(newCompanyId, "create")
    send_message(oldCompanyId, "delete")


def run1():
    # 分拆任务
    tasks = get_all_corporate_decompose_tasks()
    for task in tasks:
        logger.info("corporate_decompose_tasks")
        logger.info(task)
        for replacement in task["replacement"]:
            replacement_company(replacement["oldCompanyId"], replacement["newCompanyId"], decompose=True)
        conn = db.connect_torndb()
        for newCorporateId in task["newCorporateIds"]:
            conn.update("update corporate set active='Y' where id=%s", newCorporateId)
            cs = conn.query("select * from company where (active is null or active !='N') and corporateId=%s",
                            newCorporateId)
            for c in cs:
                send_task_message(c["id"], "old split corporateId: %s" % task["oldCorporateId"])
        conn.update("update corporate set active='N' where id=%s", task["oldCorporateId"])
        conn.close()

        mongo = db.connect_mongo()
        mongo.task.corporate_decompose.update({"_id": task["_id"]}, {"$set":{"processStatus":3}})
        mongo.close()


def get_corporate_id(company_id):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", company_id)
    conn.close()
    return company["corporateId"]


def reaggregate_funding(oldCompanyId, newCompanyId):
    logger.info("reaggregate_funding")
    old_corporate_id = get_corporate_id(oldCompanyId)
    new_corporate_id = get_corporate_id(newCompanyId)
    conn = db.connect_torndb()
    fundings = conn.query("select * from funding where corporateId=%s and (active is null or active='Y')", old_corporate_id)
    for f in fundings:
        logger.info("fundingDate:%s, round:%s", f["fundingDate"], f["round"])
        conn.update("update funding set companyId=%s, corporateId=%s, modifyTime=now() where id=%s", newCompanyId, new_corporate_id, f["id"])
    conn.close()


def reaggregate_artifact(oldCompanyId, newCompanyId):
    logger.info("reaggregate_artifact")
    conn = db.connect_torndb()
    arts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y')", oldCompanyId)
    for art in arts:
        if art["type"] in [4020, 4040, 4050]: #wechat, ios, android
            _art = conn.get("select * from artifact where companyId=%s and type=%s and domain=%s and (active is null or active='Y') limit 1",
                            newCompanyId,art["type"], art["domain"])
        elif art["type"] in [4010, 4030]: #website, weibo
            _art = conn.get("select * from artifact where companyId=%s and type=%s and link=%s and (active is null or active='Y') limit 1",
                newCompanyId, art["type"], art["link"])
        else:
            continue
        if _art is None:
            logger.info("type:%s, link:%s, domain:%s", art["type"], art["link"], art["domain"])
            conn.update("update artifact set companyId=%s where id=%s", newCompanyId, art["id"])
    conn.close()


def reaggregate_member(oldCompanyId, newCompanyId):
    logger.info("reaggregate_member")
    conn = db.connect_torndb()
    ms = conn.query("select * from company_member_rel where companyId=%s and (active is null or active='Y')", oldCompanyId)
    for m in ms:
        _m = conn.get("select * from company_member_rel where companyId=%s and memberId=%s and (active is null or active='Y')",
                      newCompanyId, m["memberId"])
        if _m is None:
            logger.info("memberId: %s", m["memberId"])
            conn.update("update company_member_rel set companyId=%s where id=%s", newCompanyId, m["id"])
    conn.close()


def reaggregate_news(oldCompanyId, newCompanyId):
    logger.info("reaggregate_news")
    mongo = db.connect_mongo()
    newses = mongo.article.news.find({"$or":[{"companyIds":oldCompanyId},{"companyId":oldCompanyId}]})
    for news in newses:
        if newCompanyId == news.get("companyId") or (news.get("companyIds") is not None and newCompanyId in news.get("companyIds")):
            continue
        logger.info("add to new _id: %s", news["_id"])
        mongo.article.news.update({"_id":news["_id"]}, {"$push":{"companyIds":newCompanyId}})
        if oldCompanyId == news.get("companyId"):
            logger.info("remove from old _id: %s", news["_id"])
            mongo.article.news.update({"_id":news["_id"]}, {"$set":{"companyId":None}})
        if news.get("companyIds") is not None and oldCompanyId in news.get("companyIds"):
            logger.info("remove from old _id: %s", news["_id"])
            mongo.article.news.update({"_id": news["_id"]}, {"$pull": {"companyIds": oldCompanyId}})

    mongo.close()


def reaggregate_corporate_alias(oldCompanyId, newCompanyId):
    logger.info("reaggregate_corporate_alias")
    old_corporate_id = get_corporate_id(oldCompanyId)
    new_corporate_id = get_corporate_id(newCompanyId)
    conn = db.connect_torndb()
    aliases = conn.query(
        "select * from corporate_alias where corporateId=%s and (active is null or active='Y')",
        old_corporate_id)
    for alias in aliases:
        _alias = conn.get(
            "select * from corporate_alias where corporateId=%s and name=%s and (active is null or active='Y') limit 1",
            new_corporate_id, alias["name"])
        if _alias is None:
            logger.info("name: %s", alias["name"])
            conn.update("update corporate_alias set corporateId=%s where id=%s", new_corporate_id, alias["id"])
    conn.close()


def reaggregate_company_alias(oldCompanyId, newCompanyId):
    logger.info("reaggregate_company_alias")
    conn = db.connect_torndb()
    #只处理短名
    aliases = conn.query("select * from company_alias where companyId=%s and (active is null or active='Y')",
                         oldCompanyId)
    for alias in aliases:
        _alias = conn.get("select * from company_alias where companyId=%s and name=%s and (active is null or active='Y') limit 1",
                          newCompanyId, alias["name"])
        if _alias is None:
            logger.info("name: %s", alias["name"])
            conn.update("update company_alias set companyId=%s where id=%s", newCompanyId, alias["id"])
    conn.close()


def check_task(task):
    # check
    # 只能保留同一个corporate下的company
    reserved_company_ids = task["reservedCompanyIds"]
    replacement = task["replacement"]

    corporates = []
    for company_id in reserved_company_ids:
        corporate_id = get_corporate_id(company_id)
        if corporate_id not in corporates:
            corporates.append(corporate_id)
    if len(corporates) > 1:
        logger.info("Error: reserved company in different corporate!")
        mongo = db.connect_mongo()
        mongo.task.corporate_reaggregate.update({"_id": task["_id"]}, {"$set": {"processStatus":-1, "errorMessage":"Reserved companies are in different corporates!"}})
        mongo.close()
        return False

    # 不保留的company都要设置替代关系
    for item in replacement:
        if item["newCompanyId"] not in  reserved_company_ids:
            logger.info("Error: replacement newCompanyId error!")
            mongo = db.connect_mongo()
            mongo.task.corporate_reaggregate.update({"_id": task["_id"]}, {
                "$set": {"processStatus": -1, "errorMessage": "replacement newCompanyId error!"}})
            mongo.close()
            return False

    all_company_ids = []
    conn = db.connect_torndb()
    for corporate_id in task["corporateIds"]:
        companies = conn.query("select * from company where corporateId=%s and (active is null or active !='N')", corporate_id)
        for c in companies:
            if c["id"] not in all_company_ids and c["id"] not in reserved_company_ids:
                all_company_ids.append(c["id"])
    conn.close()

    replaced_company_ids = []
    for item in replacement:
        if item["oldCompanyId"] not in replaced_company_ids:
            replaced_company_ids.append(item["oldCompanyId"])
    for id in all_company_ids:
        if id not in replaced_company_ids:
            logger.info("Error: companyId %s should be replaced!", id)
            mongo = db.connect_mongo()
            mongo.task.corporate_reaggregate.update({"_id": task["_id"]}, {
                "$set": {"processStatus": -1, "errorMessage": "companyId %s should be replaced!" % id}})
            mongo.close()
            return False


    # 所有的源都必须设置为要保留的company
    # for item in replacement:
    #     old_company_id = item["oldCompanyId"]
    #     conn = db.connect_torndb()
    #     ss = conn.query("select * from source_company where companyId=%s and (active is null or active='Y')", old_company_id)
    #     conn.close()
    #     if len(ss) != 0:
    #         logger.info("Error: companyId:%s, its sourcecompanies should be replaced!", old_company_id)
    #         mongo = db.connect_mongo()
    #         mongo.task.corporate_reaggregate.update({"_id": task["_id"]}, {
    #             "$set": {"processStatus": -1, "errorMessage": "companyId:%s, its sourcecompanies should be replaced!" % old_company_id}})
    #         mongo.close()
    #         return False
    return True


def run2():
    #聚合任务
    tasks = get_all_corporate_reaggregate_tasks()
    for task in tasks:
        logger.info("corporate_reaggregate_tasks")
        if check_task(task) is False:
            continue

        for replacement in task["replacement"]:
            old_company_id = replacement["oldCompanyId"]
            new_company_id = replacement["newCompanyId"]
            reaggregate_funding(old_company_id, new_company_id)
            reaggregate_artifact(old_company_id, new_company_id)
            reaggregate_member(old_company_id, new_company_id)
            reaggregate_news(old_company_id, new_company_id)
            reaggregate_corporate_alias(old_company_id, new_company_id)
            reaggregate_company_alias(old_company_id, new_company_id)
            replacement_company(old_company_id, new_company_id)

        conn = db.connect_torndb()
        corporate_ids = task["corporateIds"]
        reserved_company_ids = task["reservedCompanyIds"]
        for corporate_id in corporate_ids:
            companies = conn.query("select id, name from company where corporateId=%s and (active is null or active!='N')", corporate_id)
            remove = True
            for company in companies:
                if company["id"] in reserved_company_ids:
                    remove = False
                    break
            if remove is True:
                logger.info("remove corporate: %s", corporate_id)
                conn.update("update corporate set active='N' where id=%s", corporate_id)
        conn.close()

        mongo = db.connect_mongo()
        mongo.task.corporate_reaggregate.update({"_id": task["_id"]}, {"$set": {"processStatus": 3}})
        mongo.close()


if __name__ == '__main__':
    while True:
        logger.info("Begin...")
        # reaggregate_news(243540,310981)
        run1()
        run2()
        logger.info("End.")
        time.sleep(30)
