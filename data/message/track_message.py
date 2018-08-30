# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import json
import traceback
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)
from bson.objectid import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, config

#logger
loghelper.init_logger("track_message", stream=True)
logger = loghelper.get_logger("track_message")


# kafka
kafkaProducer = None
kafkaConsumer = None

def init_kafka():
    global kafkaConsumer, kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("track_message", group_id="track_message",
                bootstrap_servers=[url],
                auto_offset_reset='smallest')


def send_message(user_id, message_4_user_id):
    if kafkaProducer is None:
        init_kafka()

    msg = {"type":"user_notify",
           "userId": user_id,
           "message_4_user_id": str(message_4_user_id)}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("websocket", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)


def get_track(_id):
    mongo = db.connect_mongo()
    tm = mongo.track.track.find_one({"_id": ObjectId(_id)})
    mongo.close()
    return tm


def get_portfolio(company_id):
    conn = db.connect_torndb()
    deals = conn.query("select * from deal where companyId=%s and "
                       "status=19050 and declineStatus=18010", company_id)
    conn.close()
    return deals


def get_assigneesid(deals):
    assigneesid = []
    for deal in deals:
        conn = db.connect_torndb()
        assignees = conn.query("select * from deal_assignee where dealId=%s", deal["id"])
        conn.close()
        for a in assignees:
            assigneesid.append(a["userId"])
    return assigneesid


def get_collection(collection_id):
    conn = db.connect_torndb()
    collection = conn.get("select * from collection where (active is null or active='Y') and "
                          "id=%s", collection_id)
    conn.close()
    return collection


def get_collection_userids(collection_id):
    userids = []
    conn = db.connect_torndb()
    rels = conn.query("select * from collection_user_rel where (active is null or active='Y') and "
                      "collectionId=%s", collection_id)
    conn.close()
    for rel in rels:
        userids.append(rel["userId"])
    return userids


def save_message_4_deal(msg):
    mongo = db.connect_mongo()
    collection_m4d = mongo.message.message_4_deal
    item = collection_m4d.find_one({"deal_id": msg["deal_id"],"track_4_deal_id": msg["track_4_deal_id"]})
    if item is None:
        msg["createTime"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        collection_m4d.insert(msg)
        logger.info("Insert new message_4_deal for deal_id:%s, track_4_deal_id: %s", msg["deal_id"], msg["track_4_deal_id"])
    else:
        logger.info("Existed message_4_deal for deal_id:%s, track_4_deal_id: %s", msg["deal_id"], msg["track_4_deal_id"])
    mongo.close()


def save_message_4_user(msg):
    mongo = db.connect_mongo()
    collection_m4d = mongo.message.message_4_user
    item = collection_m4d.find_one({"receiver": msg["receiver"],"track_4_deal_id": msg["track_4_deal_id"]})
    if item is None:
        msg["read"] = "N"
        msg["createTime"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        message_4_user_id = collection_m4d.insert(msg)
        logger.info("Insert new message_4_user for receiver:%s, track_4_deal_id: %s", msg["receiver"], msg["track_4_deal_id"])
    else:
        message_4_user_id = item["_id"]
        logger.info("Existed message_4_user for receiver:%s, track_4_deal_id: %s", msg["receiver"], msg["track_4_deal_id"])
    mongo.close()
    return message_4_user_id


def save_collection_message_4_user(msg):
    mongo = db.connect_mongo()
    collection_m4d = mongo.message.message_4_user
    item = collection_m4d.find_one({"receiver": msg["receiver"],"collection_message_id": msg["collection_message_id"]})
    if item is None:
        msg["read"] = "N"
        msg["createTime"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        message_4_user_id = collection_m4d.insert(msg)
        logger.info("Insert new message_4_user for receiver:%s, collection_message_id: %s", msg["receiver"], msg["collection_message_id"])
    else:
        message_4_user_id = item["_id"]
        logger.info("Existed message_4_user for receiver:%s, collection_message_id: %s", msg["receiver"], msg["collection_message_id"])
    mongo.close()
    return message_4_user_id


def save_track_4_deal(msg):
    mongo = db.connect_mongo()
    c = mongo.track.track_4_deal
    item = c.find_one({"deal_id":msg["deal_id"], "track_id":msg["track_id"]})
    if item is None:
        msg["createTime"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        _id = c.insert(msg)
        logger.info("Insert new track_4_deal for deal_id: %s, track_id: %s", msg["deal_id"], msg["track_id"])
    else:
        _id = item["_id"]
        logger.info("Existed track_4_deal for deal_id: %s, track_id: %s", msg["deal_id"], msg["track_id"])
    mongo.close()
    return _id

def process_track(msg):
    topic_id = msg["topic_id"]
    if topic_id == 1:
        process_news(msg)
    elif topic_id == 3 or topic_id == 6:
        process_funding(msg)


def process_news(msg):
    _id = msg["id"]
    tm = get_track(_id)
    if tm is None:
        return

    company_id = tm["company_id"]

    # find all deals
    deals = get_portfolio(company_id)
    for deal in deals:
        data = {
            "topic_id": int(tm["topic_id"]),
            "deal_id": int(deal["id"]),
            "organization_id": int(deal["organizationId"]),
            "contents": tm["contents"],
            "track_id": tm["_id"]
        }
        track_4_deal_id = save_track_4_deal(data)

        data = {"deal_id": deal["id"],
                "track_4_deal_id": track_4_deal_id
                }
        save_message_4_deal(data)

        # find assignees
        assigneeids = get_assigneesid([deal])
        for user_id in assigneeids:
            data = {"receiver": int(user_id),
                    "track_4_deal_id": track_4_deal_id
                    }
            message_4_user_id = save_message_4_user(data)
            send_message(user_id, message_4_user_id)


def process_funding(msg):
    _id = msg["id"]
    tm = get_track(_id)
    if tm is None:
        return

    company_id = tm["company_id"]
    logger.info("companyId: %s", company_id)
    if tm["topic_id"] == 3:
        new_topic_id = int(8)
        conn = db.connect_torndb()
        funding = conn.get("select * from funding where (active is null or active='Y') and "
                             "companyId=%s order by fundingDate desc limit 1", company_id)
        if funding is None:
            conn.close()
            return
        contents = int(funding["id"])
        conn.close()
    elif tm["topic_id"] == 6:
        new_topic_id = int(7)
        contents = int(company_id)
    else:
        return


    conn = db.connect_torndb()
    comps = conn.query("select * from deal_comps where (active is null or active='Y') and companyId=%s", company_id)
    for comp in comps:
        deal_id = comp["dealId"]
        deal = conn.get("select * from deal where id=%s", deal_id)
        if deal and deal["status"]==19050 and deal["declineStatus"]==18010:
            data = {
                "topic_id": new_topic_id,
                "deal_id": int(deal["id"]),
                "organization_id": int(deal["organizationId"]),
                "contents": contents,
                "track_id": tm["_id"]
            }
            track_4_deal_id = save_track_4_deal(data)

            data = {"deal_id": int(deal["id"]),
                    "track_4_deal_id": track_4_deal_id
                    }
            save_message_4_deal(data)

            # find assignees
            assigneeids = get_assigneesid([deal])
            for user_id in assigneeids:
                data = {"receiver": int(user_id),
                        "track_4_deal_id": track_4_deal_id
                        }
                message_4_user_id = save_message_4_user(data)
                send_message(user_id, message_4_user_id)
    conn.close()


def get_deal_comps_ids(deal_id):
    deal_comps_ids = []
    conn = db.connect_torndb()
    deal_comps = conn.query("select * from deal_comps where dealId=%s", deal_id)
    for c in deal_comps:
        deal_comps_ids.append(c["companyId"])
    conn.close()
    return deal_comps_ids


def process_comps(msg):
    company_id = msg["id"]

    # find all deals
    deals = get_portfolio(company_id)
    for deal in deals:
        track_id = "" + str(deal["id"])
        for comp in msg["comps"]:
            track_id += "" + str(comp)

        deal_comps_ids = get_deal_comps_ids(deal["id"])
        new_comps_ids = list(set(msg["comps"]) -set(deal_comps_ids))
        if len(new_comps_ids) == 0:
            continue

        data = {
            "topic_id": int(9),
            "deal_id": int(deal["id"]),
            "organization_id": int(deal["organizationId"]),
            "contents": new_comps_ids,
            "track_id": track_id
        }
        track_4_deal_id = save_track_4_deal(data)

        data = {"deal_id": int(deal["id"]),
                "track_4_deal_id": track_4_deal_id
                }
        save_message_4_deal(data)

        # find assignees
        assigneeids = get_assigneesid([deal])
        for user_id in assigneeids:
            data = {"receiver": int(user_id),
                    "track_4_deal_id": track_4_deal_id
                    }
            message_4_user_id = save_message_4_user(data)
            send_message(user_id, message_4_user_id)


def process_collection(msg):
    collection_id = msg["id"]
    collection = get_collection(collection_id)
    if collection is None:
        return
    if collection["type"] != 39030:  # 自定义
        return

    collection_message = {
        "collection_id": int(collection_id),
        "new_count": int(msg["new_count"]),
        "createTime": datetime.datetime.now() - datetime.timedelta(hours=8)
    }

    mongo = db.connect_mongo()
    object_id = mongo.message.collection_message.insert(collection_message)
    mongo.close()

    userids = get_collection_userids(collection_id)
    for user_id in userids:
        data = {"receiver": int(user_id),
                "collection_message_id": object_id}
        message_4_user_id = save_collection_message_4_user(data)
        send_message(user_id, message_4_user_id)


def process_recommend(msg):
    pass


if __name__ == '__main__':
    init_kafka()
    while True:
        try:
            for message in kafkaConsumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                     message.offset, message.key,
                                                     message.value))
                    msg = json.loads(message.value)
                    if msg["type"] == "track":
                        if msg["topic_id"] == 3: #完成融资
                            process_track(msg)
                            kafkaConsumer.commit()
                        elif msg["topic_id"] == 6: #启动融资
                            process_track(msg)
                            kafkaConsumer.commit()
                        elif msg["topic_id"] == 1: #重要媒体报道
                            process_track(msg)
                            kafkaConsumer.commit()
                        else:
                            kafkaConsumer.commit()
                    elif msg["type"] == "collection":
                        process_collection(msg)
                        kafkaConsumer.commit()
                    elif msg["type"] == "comps":
                        if msg.get("comps") is None: # 错误的消息格式
                            kafkaConsumer.commit()
                        else:
                            process_comps(msg)
                            kafkaConsumer.commit()
                    elif msg["type"] == "recommend":
                        #process_recommend(msg)
                        exit()
                        # kafkaConsumer.commit()
                        pass
                    else:
                        # kafkaConsumer.commit()
                        exit()

                except Exception,e :
                    traceback.print_exc()
        except KeyboardInterrupt:
            exit(0)
        except Exception,e :
            logger.exception(e)
            traceback.print_exc()
            time.sleep(60)
            init_kafka()