# -*- coding: utf-8 -*-
import os, sys
import time, datetime

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db

#logger
loghelper.init_logger("user_abnormal_log", stream=True)
logger = loghelper.get_logger("user_abnormal_log")

block_ips = ["139.196.82.224",
             "218.4.167.70",
             "39.155.188.22"]

def aggregate(minutes, quota):
    # urls = ["/api-company/api/company/list",
    #         "/api-company/api/company/collection/company/list",
    #         "/api-company/api/company/basic",
    #         "/api-company/api/company/track/getByTag"]
    urls = ["/api-company/api/company/basic",
            "/api-company/api/company/list",
            "/xiniudata-api/api2/service/company/basic",
            "/api2/service/company/basic",
            "/xiniudata-api/api2/service/gongshang/list_by_corporate",
            "/api2/service/gongshang/list_by_corporate",
            "/xiniudata-api/api2/service/company/list",
            "/api2/service/company/list"]

    mongo = db.connect_mongo()
    items = list(mongo.log.user_log.aggregate([
        {
            "$match": {
                "code": 0,
                "time": {"$gte": datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)},
                "requestURL": {"$in": urls}
            }
        },
        {
            "$group": {
                "_id": "$userId",
                "cnt": {"$sum": 1}
            }
        },
        {
            "$match": {
                "cnt": {"$gte": quota}
            }
        },
        {
            "$sort": {
                "cnt": -1
            }
        }
    ]))
    mongo.close()
    return items


def aggregate_all(minutes, quota):
    mongo = db.connect_mongo()
    items = list(mongo.log.user_log.aggregate([
        {
            "$match": {
                "code": 0,
                "time": {"$gte": datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)}
            }
        },
        {
            "$group": {
                "_id": "$userId",
                "cnt": {"$sum": 1}
            }
        },
        {
            "$match": {
                "cnt": {"$gte": quota}
            }
        },
        {
            "$sort": {
                "cnt": -1
            }
        }
    ]))
    mongo.close()
    return items


def run():
    # 一分钟
    logger.info("*** 1m ***")
    items = aggregate(1, 15)
    mongo = db.connect_mongo()
    for item in items:
        logger.info(item)
        if should_block(item["_id"]):
            # if item["cnt"] >= 20:
            #     block_user(item["_id"])
            log = mongo.log.user_abnormal_log.find_one({"userId":item["_id"], "processed":"N"})
            if log is None:
                mongo.log.user_abnormal_log.insert({
                    "userId": item["_id"],
                    "type": "1m",
                    "visit_times": item["cnt"],
                    "createTime": datetime.datetime.utcnow(),
                    "modifyTime": datetime.datetime.utcnow(),
                    "processed": "N"
                })
    mongo.close()

    # 一小时
    logger.info("*** 60m ***")
    items = aggregate(60, 100)
    mongo = db.connect_mongo()
    for item in items:
        logger.info(item)
        if should_block(item["_id"]):
            if item["cnt"] >= 150:
                block_user(item["_id"])
            log = mongo.log.user_abnormal_log.find_one({"userId": item["_id"], "processed": "N"})
            if log is None:
                log = mongo.log.user_abnormal_log.find_one({"userId": item["_id"], "processed": "Y"}, sort=[("_id", -1)])
                if log is None or log["modifyTime"] < datetime.datetime.utcnow() - datetime.timedelta(minutes=10):
                    mongo.log.user_abnormal_log.insert({
                        "userId": item["_id"],
                        "type": "60m",
                        "visit_times": item["cnt"],
                        "createTime": datetime.datetime.utcnow(),
                        "modifyTime": datetime.datetime.utcnow(),
                        "processed": "N"
                    })
    mongo.close()


    # 一天
    logger.info("*** 1day ***")
    items = aggregate(60*24, 300)
    mongo = db.connect_mongo()
    for item in items:
        logger.info(item)
        if should_block(item["_id"]):
            if item["cnt"] >= 400:
                block_user(item["_id"])
            log = mongo.log.user_abnormal_log.find_one({"userId": item["_id"], "processed": "N"})
            if log is None:
                log = mongo.log.user_abnormal_log.find_one({"userId": item["_id"], "processed": "Y"}, sort=[("_id", -1)])
                if log is None or log["modifyTime"] < datetime.datetime.utcnow() - datetime.timedelta(minutes=10):
                    mongo.log.user_abnormal_log.insert({
                        "userId": item["_id"],
                        "type": "1day",
                        "visit_times": item["cnt"],
                        "createTime": datetime.datetime.utcnow(),
                        "modifyTime": datetime.datetime.utcnow(),
                        "processed": "N"
                    })
    mongo.close()


def should_block(user_id):
    conn = db.connect_torndb()
    rel = conn.get("select * from user_organization_rel where userId=%s and (active is null or active='Y')", user_id)
    organization_id = rel["organizationId"]
    if organization_id in [7, 51]:
        conn.close()
        return False
    org = conn.get("select * from organization where id=%s", organization_id)
    if org["type"] == 17020:
        conn.close()
        return False
    return True


def block_user(user_id):
    #return
    if user_id is None:
        return

    conn = db.connect_torndb()
    rel = conn.get("select * from user_organization_rel where userId=%s and (active is null or active='Y')", user_id)
    organization_id = rel["organizationId"]
    if organization_id in [7,51]:
        conn.close()
        return
    org = conn.get("select * from organization where id=%s", organization_id)
    if org["type"] == 17020:
        conn.close()
        return

    user = conn.get("select * from user where id=%s", user_id)
    if user["active"] != 'D' and user["verifiedInvestor"] != 'Y':
        logger.info("Block: %s, %s, %s, %s", user_id, user["username"], user["phone"], user["loginIP"])
        conn.update("update user set active='D', modifyTime=now() where id=%s", user_id)
        logger.info("")

    conn.close()


def block_by_ips():
    conn = db.connect_torndb()
    users = conn.query("select * from user where active is null or active !='D' order by id desc")
    for user in users:
        ip = user["loginIP"]
        if ip in block_ips:
            logger.info("Block ip!")
            logger.info(user)
            conn.update("update user set active='D', modifyTime=now() where id=%s", user["id"])

    conn.close()


def calc_ips_cnt(logs):
    ips = {}
    for log in logs:
        ip = log["ip"]
        if ips.has_key(ip):
            ips[ip] += 1
        else:
            ips[ip] = 1
    return len(ips.keys())


def block_by_ip_statistic():
    items = aggregate_all(60, 10)
    mongo = db.connect_mongo()
    for item in items:
        if item["_id"] is None:
            continue
        logs = list(mongo.log.user_log.find({"userId":item["_id"],
                "time": {"$gte": datetime.datetime.utcnow() - datetime.timedelta(minutes=60)}}))
        logs_cnt = len(logs)
        ips_cnt = calc_ips_cnt(logs)
        if ips_cnt>5:
            logger.info("userId: %s, logs count: %s, ip count: %s", item["_id"], logs_cnt, ips_cnt)
            block_user(item["_id"])
    mongo.close()


if __name__ == '__main__':
    while True:
        logger.info("Begin...")
        run()
        block_by_ips()
        block_by_ip_statistic()
        logger.info("End.")
        time.sleep(60)
