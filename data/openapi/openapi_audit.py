# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
import json
from kafka import (KafkaClient, SimpleProducer)

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, config, util

#logger
loghelper.init_logger("openapi_audit", stream=True)
logger = loghelper.get_logger("openapi_audit")


# kafka
kafkaProducer = None

def init_kafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)


def send_message(company_id, comments):
    if kafkaProducer is None:
        init_kafka()

    n = datetime.datetime.now()
    msg = {"source":"visit_openapi", "id": company_id, "detail": comments,
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


def find_companies(conn, full_name):
    cs = {}
    items = conn.query("select * from company where (active is null or active='Y') and fullName=%s", full_name)
    for item in items:
        if not cs.has_key(item["id"]):
            cs[item["id"]] = item

    items = conn.query("select c.* from company c join corporate_alias a"
                       " on c.corporateId=a.corporateId"
                       " where a.name = %s"
                       " and (a.active = 'Y' or a.active is null)"
                       " and (c.active = 'Y' or c.active is null)",
                       full_name)
    for item in items:
        if not cs.has_key(item["id"]):
            cs[item["id"]] = item

    companies = []
    for key, value in cs.items():
        companies.append(value)
    return companies


def find_unverified_companies(conn, companies):
    unverfied_companies = []
    for c in companies:
        if c["verify"] != 'Y':
            unverfied_companies.append(c)
    return unverfied_companies


def insert_audit_company(company, project_name, product_desc, org_name, detect_time, mongo):
    audit = mongo.task.audit_company.find_one({"companyId":company["id"], "type":"openapi", "subtype":"unverified"})
    if audit is None:
        mongo.task.audit_company.insert_one({
            "org": org_name,
            "comments": "%s\n%s" % (project_name, product_desc),
            "companyId": int(company["id"]),
            "type": "openapi",
            "subtype": "unverified",
            "detectTime": detect_time,
            "processStatus": 0,
            "createUser": None,
            "modifyUser": None,
            "createTime": datetime.datetime.utcnow(),
            "modifyTime": datetime.datetime.utcnow()
        })
    elif audit["comments"] == "":
        mongo.task.audit_company.update_one({"_id":audit["_id"]}, {"$set":{"comments": project_name}})


def insert_notfound_company(full_name, project_name, product_desc, org_name, detect_time, mongo, conn):
    # sc = conn.get("select * from source_company where source=13100 and sourceId=%s", util.md5str(full_name))
    # if sc is None:
    #     conn.insert("insert source_company(name, fullname,description,source,sourceId,createTime,modifyTime) "
    #                 "values(%s,%s,%s,%s,%s,now(),now())",
    #                 project_name, full_name, product_desc, 13100, util.md5str(full_name))
    #     # exit()

    audit = mongo.task.audit_company.find_one({"fullName":full_name, "type":"openapi", "subtype":"notfound"})
    if audit is None:
        mongo.task.audit_company.insert_one({
            "org": org_name,
            "comments": "%s\n%s" % (project_name, product_desc),
            "fullName": full_name,
            "type": "openapi",
            "subtype": "notfound",
            "detectTime": detect_time,
            "processStatus": 0,
            "createUser": None,
            "modifyUser": None,
            "createTime": datetime.datetime.utcnow(),
            "modifyTime": datetime.datetime.utcnow()
        })
    elif audit["comments"] == "":
        mongo.task.audit_company.update_one({"_id":audit["_id"]}, {"$set":{"comments": project_name}})


def main():
    logger.info("Start...")
    while True:
        mongo = db.connect_mongo()
        items = list(mongo.log.openapi_log.find({"requestURL":"/openapi/company/search_by_fullname",
                                             "checkedTime":{"$exists":False}}).limit(100))
        conn = db.connect_torndb()
        for item in items:
            try:
                full_name = item["requestVO"]["payload"]["fullName"]
                project_name = item["requestVO"]["payload"].get("projectName")
                if project_name is None:
                    project_name = ""
                product_desc = item["requestVO"]["payload"].get("productDesc")
                if product_desc is None:
                    product_desc = ""

                accesskeyid = item["requestVO"]["accesskeyid"]
                org = conn.get("select o.* from org_openapi_conf c join organization o"
                               " on c.organizationId=o.id"
                               " where accesskeyid=%s", accesskeyid)
            except:
                mongo.log.openapi_log.update_one({"_id": item["_id"]},
                                                 {"$set": {"checkedTime": datetime.datetime.utcnow()}})
                continue
            logger.info(full_name)
            companies = find_companies(conn, full_name)
            if len(companies) == 0:
                # 不存在！
                logger.info("Not exist! %s", full_name)
                insert_notfound_company(full_name, project_name, product_desc, org["name"], item["time"], mongo, conn)
                # exit()
            else:
                # unverfied_companies = find_unverified_companies(conn, companies)
                # for c in unverfied_companies:
                #     logger.info("Not verified! code: %s, name: %s", c["code"], c["name"])
                #     insert_audit_company(c, project_name, product_desc, org["name"], item["time"], mongo)
                #     # exit()
                for c in companies:
                    logger.info("may verify! code: %s, name: %s", c["code"], c["name"])
                    comments = "from ether\n%s\n%s\%s" % (project_name, full_name, product_desc)
                    send_message(c["id"], comments)

            mongo.log.openapi_log.update_one({"_id": item["_id"]}, {"$set":{"checkedTime": datetime.datetime.utcnow()}})

        conn.close()
        mongo.close()

        if len(items) == 0:
            logger.info("End.")
            time.sleep(60)
            logger.info("Start...")


if __name__ == '__main__':
    main()