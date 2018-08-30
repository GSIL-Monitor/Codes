# -*- coding: utf-8 -*-
import os, sys
import datetime
import traceback
from bson.objectid import ObjectId
import umeng

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("process_util", stream=True)
logger = loghelper.get_logger("process_util")

def get_badge(user_id, _conn=None, _mongo=None):
    if _conn is None:
        conn = db.connect_torndb_proxy()
    else:
        conn = _conn
    if _mongo is None:
        mongo = db.connect_mongo()
    else:
        mongo = _mongo
    user_behavior = conn.get("select * from user_behavior where userId=%s order by id desc limit 1", user_id)
    last_user_message_id = None
    last_user_message_createtime = None
    if user_behavior is not None:
        last_user_message_id = user_behavior["lastUserMessageId"]
        last_user_message_createtime = user_behavior["lastUserMessageCreateTime"]
        if last_user_message_createtime is not None:
            last_user_message_createtime += datetime.timedelta(hours=-8)

    badge = 0
    if last_user_message_createtime is not None:
        badge = mongo.message.user_message.find(
            {"userId": user_id, "createTime": {"$gt": last_user_message_createtime}}).count()
    else:
        if last_user_message_id is None:
            badge = mongo.message.user_message.find({"userId": user_id}).count()
        else:
            badge = mongo.message.user_message.find(
                {"userId": user_id, "_id": {"$gt": ObjectId(last_user_message_id)}}).count()
    if _mongo is None:
        mongo.close()
    if _conn is None:
        conn.close()
    return badge


def get_company(company_id, _conn=None):
    if _conn is None:
        conn = db.connect_torndb_proxy()
    else:
        conn = _conn
    company = conn.get("select * from company where id=%s", int(company_id))
    if _conn is None:
        conn.close()
    return company


def get_investor(investor_id, _conn=None):
    if _conn is None:
        conn = db.connect_torndb_proxy()
    else:
        conn = _conn
    investor = conn.get("select * from investor where id=%s", int(investor_id))
    if _conn is None:
        conn.close()
    return investor


def audit_company_from_topic_company(company_id, topic_id, detect_time, _mongo=None):
    if _mongo is None:
        mongo = db.connect_mongo()
    else:
        mongo = _mongo
    company = get_company(company_id)
    if company is not None and company["active"] != "N" and company["verify"] != "Y":
        audit = mongo.task.audit_company.find_one({"companyId":company_id})
        if audit is None:
            mongo.task.audit_company.insert_one({
                "companyId": int(company_id),
                "type": "topic",
                "topicId": int(topic_id),
                "detectTime": detect_time,
                "processStatus": 0,
                "createUser": None,
                "modifyUser": None,
                "createTime": datetime.datetime.utcnow(),
                "modifyTime": datetime.datetime.utcnow()
            })
    if _mongo is None:
        mongo.close()


def audit_company_from_company_message(company_id, track_dimension, company_message_id, relate_type, detect_time,
                                       comps=False, _mongo=None, _conn=None):
    if relate_type is not None:
        relate_type = int(relate_type)
    if _mongo is None:
        mongo = db.connect_mongo()
    else:
        mongo = _mongo
    company = get_company(company_id, _conn=_conn)
    if company is not None and company["active"] != "N" and company["verify"] != "Y":
        audit = mongo.task.audit_company.find_one({"companyId":company_id})
        if audit is None:
            mongo.task.audit_company.insert_one({
                "companyId": int(company_id),
                "type": "company",
                "trackDimension": int(track_dimension),
                "companyMessageId": int(company_message_id),
                "relateType": relate_type,
                "detectTime": detect_time,
                "comps": comps,
                "processStatus": 0,
                "createUser": None,
                "modifyUser": None,
                "createTime": datetime.datetime.utcnow(),
                "modifyTime": datetime.datetime.utcnow()
            })
    if _mongo is None:
        mongo.close()


def audit_companies(str, track_dimension, company_message_id, relate_type, detect_time, _mongo=None, _conn=None):
    if _conn is None:
        conn = db.connect_torndb_proxy()
    else:
        conn = _conn
    if _mongo is None:
        mongo = db.connect_mongo()
    else:
        mongo = _mongo
    ss = str.split(",")
    for s in ss:
        try:
            company_id = int(s)
            audit_company_from_company_message(company_id, track_dimension, company_message_id, relate_type,
                                               detect_time, comps=True, _mongo=mongo, _conn=_conn)
        except:
            continue
    if _mongo is None:
        mongo.close()
    if _conn is None:
        conn.close()


def regenerate_audit_company():
    id = -1
    conn = db.connect_torndb_proxy()
    while True:
        cs = conn.query(
            "select * from topic_company where id>%s order by id limit 1000", id)
        if len(cs) == 0:
            break
        for c in cs:
            if c["id"] > id:
                id = c["id"]
            audit_company_from_topic_company(c["companyId"], c["topicId"], c["createTime"])

    while True:
        cs = conn.query(
            "select * from company_message where id>%s order by id limit 1000", id)
        if len(cs) == 0:
            break
        for c in cs:
            if c["id"] > id:
                id = c["id"]
            audit_company_from_company_message(c["companyId"], c["trackDimension"], c["id"], c["relateType"], c["createTime"])

    conn.close()


def get_test_users():
    #周玉彬3142，arthur 1078
    return []


def adjust_createTime(user_id, createTime, _mongo):
    mongo = _mongo
    while True:
        m = mongo.message.user_message.find_one({"userId": user_id, "createTime": createTime})
        if m is not None:
            createTime += datetime.timedelta(milliseconds=1)
        else:
            break
    return createTime


def insert_user_message(user_id, createTime, company_message_id=None, topic_message_id=None, investor_message_id=None, _mongo=None):
    # if user_id in [1078, 3142, 1140]:
    #     insert_user_message1(user_id, createTime, company_message_id, topic_message_id, _conn=None, _mongo=_mongo)
    #     return

    insert_user_message1(user_id, createTime, company_message_id, topic_message_id, investor_message_id, _conn=None, _mongo=_mongo)
    return

    send = False
    if _mongo is None:
        mongo = db.connect_mongo()
    else:
        mongo = _mongo

    createTime = adjust_createTime(user_id, createTime, mongo)
    if company_message_id is not None:
        company_message_id = int(company_message_id)
        user_message = mongo.message.user_message.find_one({"userId": user_id, "companyMessageId": company_message_id})
        if user_message is None:
            data = {
                "userId": user_id,
                "type": 5010,
                "companyMessageId": company_message_id,
                "createTime": createTime,
                "active": "Y"
            }
            mongo.message.user_message.insert_one(data)
            send = True

    if topic_message_id is not None:
        topic_message_id = int(topic_message_id)
        user_message = mongo.message.user_message.find_one({"userId": user_id, "topicMessageId": topic_message_id})
        if user_message is None:
            data = {
                "userId": user_id,
                "type": 5020,
                "topicMessageId": topic_message_id,
                "createTime": createTime,
                "active": "Y"
            }
            mongo.message.user_message.insert_one(data)
            send = True
            logger.info("insert topic message for user, userId: %s, topicMessageId: %s", user_id, topic_message_id)

    if investor_message_id is not None:
        investor_message_id = int(investor_message_id)
        user_message = mongo.message.user_message.find_one({"userId": user_id, "investorMessageId": investor_message_id})
        if user_message is None:
            data = {
                "userId": user_id,
                "type": 5030,
                "investorMessageId": investor_message_id,
                "createTime": createTime,
                "active": "Y"
            }
            mongo.message.user_message.insert_one(data)
            send = True
            logger.info("insert investor message for user, userId: %s, investorMessageId: %s", user_id, investor_message_id)

    if _mongo is None:
        mongo.close()
    return send


def insert_user_message1(user_id, createTime, company_message_id=None, topic_message_id=None, investor_message_id=None, _conn=None, _mongo=None):
    user_id = int(user_id)
    send = False
    if _mongo is None:
        mongo = db.connect_mongo()
    else:
        mongo = _mongo
    if _conn is None:
        conn = db.connect_torndb_proxy()
    else:
        conn = _conn

    createTime = adjust_createTime(user_id, createTime, mongo)
    if company_message_id is not None:
        company_message_id = int(company_message_id)
        user_message = mongo.message.user_message.find_one({"userId": user_id, "companyMessageId": company_message_id})
        if user_message is None:
            m = conn.get("select * from company_message where id=%s", company_message_id)
            need_folder = False
            exist_in_other_messages = False
            if m["relateType"] == 10:
                local_create_time = createTime + datetime.timedelta(hours=8)
                thatday = datetime.datetime(local_create_time.year, local_create_time.month, local_create_time.day) - datetime.timedelta(hours=8)
                logger.info("thatday: %s", thatday)
                last_user_message = mongo.message.user_message.find_one(
                        {"userId": user_id,
                         "companyId": int(m["companyId"]),
                         "relateType": int(m["relateType"]),
                         "createTime": {"$gte": thatday, "$lt": thatday + datetime.timedelta(days=1)},
                         "active": "Y"
                         },sort=[("createTime", -1)],limit=1)
                if last_user_message is not None:
                    logger.info(last_user_message)
                    need_folder = True
                    if last_user_message.get("otherMessages") is not None:
                        for _m in last_user_message.get("otherMessages"):
                            if _m["companyMessageId"] == company_message_id:
                                exist_in_other_messages = True
                                break
            # exit()
            if need_folder is True:
                if exist_in_other_messages is False:
                    if createTime > last_user_message["createTime"]:
                        # 最新消息，创建新的user_message, 将源user_message添加到otherMessages中
                        otherMessages = []
                        otherMessages.append(
                            {
                            "type": 5010,
                            "companyMessageId": int(last_user_message["companyMessageId"]),
                            "createTime": last_user_message["createTime"],
                            "active": "Y",
                            "companyId": int(last_user_message["companyId"]),
                            "relateType": int(last_user_message["relateType"])
                            }
                        )
                        if last_user_message.get("otherMessages") is not None:
                            otherMessages.extend(last_user_message.get("otherMessages"))

                        data = {
                            "userId": user_id,
                            "type": 5010,
                            "companyMessageId": company_message_id,
                            "createTime": createTime,
                            "active": "Y",
                            "companyId": int(m["companyId"]),
                            "relateType": int(m["relateType"]),
                            "otherMessages": otherMessages
                        }
                        mongo.message.user_message.insert_one(data)
                        mongo.message.user_message.delete_one({"_id": last_user_message["_id"]})
                        send = True
                    else:
                        # 老消息，直接添加到otherMessages中
                        mongo.message.user_message.update({"_id": last_user_message["_id"]},
                                                          {"$addToSet":{'otherMessages':{
                                                              "type": 5010,
                                                              "companyMessageId": company_message_id,
                                                              "createTime": createTime,
                                                              "active": "Y",
                                                              "companyId": int(m["companyId"]),
                                                              "relateType": int(m["relateType"])
                                                          }}})
            else:
                data = {
                    "userId": user_id,
                    "type": 5010,
                    "companyMessageId": company_message_id,
                    "createTime": createTime,
                    "active": "Y",
                    "companyId": int(m["companyId"]),
                    "relateType": int(m["relateType"])
                }
                mongo.message.user_message.insert_one(data)
                send = True

    if topic_message_id is not None:
        topic_message_id = int(topic_message_id)
        user_message = mongo.message.user_message.find_one({"userId": user_id, "topicMessageId": topic_message_id})
        if user_message is None:
            data = {
                "userId": user_id,
                "type": 5020,
                "topicMessageId": topic_message_id,
                "createTime": createTime,
                "active": "Y"
            }
            mongo.message.user_message.insert_one(data)
            send = True
            logger.info("insert topic message for user, userId: %s, topicMessageId: %s", user_id, topic_message_id)

    if investor_message_id is not None:
        investor_message_id = int(investor_message_id)
        user_message = mongo.message.user_message.find_one({"userId": user_id, "investorMessageId": investor_message_id})
        if user_message is None:
            data = {
                "userId": user_id,
                "type": 5030,
                "investorMessageId": investor_message_id,
                "createTime": createTime,
                "active": "Y"
            }
            mongo.message.user_message.insert_one(data)
            send = True
            logger.info("insert investor message for user, userId: %s, investorMessageId: %s", user_id, investor_message_id)

    if _conn is None:
        conn.close()
    if _mongo is None:
        mongo.close()
    return send


def send_iOS_message(user_id, message, message_type, _conn=None):
    # 发送iOS push message
    badge = get_badge(user_id)
    if _conn is None:
        conn = db.connect_torndb_proxy()
    else:
        conn = _conn
    user_tokens = get_tokens(conn, user_id)
    if _conn is None:
        conn.close()
    for user_token in user_tokens:
        device_id = user_token["deviceId"]
        if device_id is None or device_id.strip() == "":
            continue
        logger.info("sendIOSUnicast, userId:%s , device_id:%s", user_id, device_id)

        for i in range(3):
            try:
                umeng.sendIOSUnicast(message["message"], badge, device_id, message_type, test=False)
                break
            except Exception, e:
                traceback.print_exc()

def send_iOS_message1(user_id, badge, message, message_type, conn, test=False):
    # 发送iOS push message
    user_tokens = get_tokens(conn, user_id)
    for user_token in user_tokens:
        device_id = user_token["deviceId"]
        if device_id is None or device_id.strip() == "":
            continue
        logger.info("sendIOSUnicast, userId:%s , device_id:%s", user_id, device_id)

        for i in range(3):
            try:
                umeng.sendIOSUnicast(message, badge, device_id, messageType=message_type, test=test)
                break
            except Exception, e:
                traceback.print_exc()


def send_iOS_content_available(user_id, message_type, _conn=None):
    # 发送iOS push message
    if _conn is None:
        conn = db.connect_torndb_proxy()
    else:
        conn = _conn
    user_tokens = get_tokens(conn, user_id)
    if _conn is None:
        conn.close()
    for user_token in user_tokens:
        device_id = user_token["deviceId"]
        if device_id is None or device_id.strip() == "":
            continue
        logger.info("sendIOSUnicast, userId:%s , device_id:%s", user_id, device_id)

        for i in range(3):
            try:
                umeng.sendContentAvailableIOSUnicast(device_id, message_type, test=False)
                break
            except Exception, e:
                traceback.print_exc()


def get_tokens(conn, user_id):
    user_tokens = conn.query("select deviceId from ("
                             "select deviceId,max(id) id from user_token "
                             "where deviceId is not null and deviceId !='' and "
                             "userId=%s group by deviceId) a "
                             "order by id desc limit 2",
                             user_id)
    return user_tokens


def test():
    user_id = 3142  # 玉彬
    # company_id = 131894 # 摩拜单车
    company_id = 13371 # ofo
    conn = db.connect_torndb_proxy()
    ms = conn.query("select * from company_message where companyId=%s order by id", company_id)
    conn.close()
    for m in ms:
        insert_user_message1(user_id, m["publishTime"] + datetime.timedelta(hours=-8), company_message_id=m["id"])


if __name__ == '__main__':
    test()
    pass
