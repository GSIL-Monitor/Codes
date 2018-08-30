# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import json
import traceback
from kafka import (KafkaClient, KafkaConsumer, SimpleProducer)
from bson.objectid import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, config

#logger
loghelper.init_logger("track_message", stream=True)
logger = loghelper.get_logger("track_message")


# kafka
kafkaConsumer = None
kafkaProducer = None

def init_kafka():
    global kafkaConsumer
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("track", group_id="dealAtBroad_message",
                bootstrap_servers=[url],
                auto_offset_reset='smallest')

def send_message(receiver,id):
    #action: create, delete
    kmsg ={"type":"user_notify","userId": receiver, "message_4_user_id": str(id)}
    logger.info("Kafka msg sent for %s", kmsg)
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("websocket", json.dumps(kmsg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(6)


def get_assignees(deal_id):
    conn = db.connect_torndb()
    das = conn.query("select * from deal_assignee where dealId=%s", deal_id)
    assignees = [int(da["userId"]) for da in das if da.has_key("userId")]
    deal = conn.get("select * from deal where id=%s", deal_id)
    if deal is not None and deal["sponsor"] is not None and int(deal["sponsor"]) not in assignees:
        assignees.append(int(deal["sponsor"]))
    conn.close()
    return assignees

def get_organizationUsers(organizationId):
    conn = db.connect_torndb()
    uos = conn.query("select * from user_organization_rel where organizationId=%s", organizationId)
    users = [int(uo["userId"]) for uo in uos if uo.has_key("userId")]
    conn.close()
    return users


def save_message_4_deal(msg):
    mongo = db.connect_mongo()
    collection_m4d = mongo.message.message_4_deal
    item = collection_m4d.find_one({"deal_id": msg["deal_id"],"deal_log_id": msg["deal_log_id"]})
    if item is None:
        msg["createTime"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        collection_m4d.insert_one(msg)
        logger.info("Insert new message_4_deal for deal_id:%s, deal_log_id: %s", msg["deal_id"], msg["deal_log_id"])
    else:
        logger.info("Existed message_4_deal for deal_id:%s, deal_log_id: %s", msg["deal_id"], msg["deal_log_id"])
    mongo.close()

def save_message_4_user(msg):
    mongo = db.connect_mongo()
    collection_m4u = mongo.message.message_4_user
    msg["read"] = "N"
    msg["createTime"] = datetime.datetime.now() - datetime.timedelta(hours=8)
    id = collection_m4u.insert(msg)
    logger.info("Insert new message_4_user for: %s", msg)
    send_message(msg["receiver"], id)
    mongo.close()


def process_deal_log(msg):
    if msg.has_key("id") is False:
        return
    dealLogId = msg["id"]

    mongo = db.connect_mongo()
    collection_dealLog = mongo.log.deal_log
    item = collection_dealLog.find_one({"_id": ObjectId(dealLogId)})

    if item is not None:
        dealmsg = {"deal_log_id": str(item["_id"]), "deal_id": item["deal_id"]}
        save_message_4_deal(dealmsg)
        # logger.info(item)
        if item["type"] in [1,2,3,6,7]:
            collection_m4u = mongo.message.message_4_user
            item_m4u = collection_m4u.find_one({"deal_log_id": dealmsg["deal_log_id"]})
            if item_m4u is not None:
                logger.info("Existed message_4_user for deal_log_id: %s", dealmsg["deal_log_id"])

            assignees = get_assignees(dealmsg["deal_id"])
            logger.info(assignees)
            # deal_id is mysql id

            for assignee in assignees:
                if isinstance(assignee,int) is False or item["createUser"] == assignee:
                    continue
                dealmsg_user = {"deal_log_id": str(item["_id"]),
                                "sender": item["createUser"], "receiver": assignee}
                save_message_4_user(dealmsg_user)
    else:
        logger.info("Deal_log not found id: %s",dealLogId)
    mongo.close()

def process_at(msg):
    if msg.has_key("id") is False:
        return
    atMessageId = msg["id"]

    mongo = db.connect_mongo()
    collection_atMessage = mongo.log.at_message
    item = collection_atMessage.find_one({"_id": ObjectId(atMessageId)})

    if item is not None:
        atmsg = {"at_message_id": str(item["_id"]), "sender": item["sender"]}

        collection_m4u = mongo.message.message_4_user
        item_m4u = collection_m4u.find_one({"at_message_id": atmsg["at_message_id"]})
        if item_m4u is not None:
            logger.info("Existed message_4_user for at_message_id: %s", atmsg["at_message_id"])

        for receiver in item["receivers"]:
            if isinstance(receiver,int) is False:
                continue
            atmsg_user = {"at_message_id": str(item["_id"]), "sender": item["sender"],
                          "receiver": receiver}
            save_message_4_user(atmsg_user)
    else:
        logger.info("at_message not found id: %s", atMessageId)
    mongo.close()

def process_broadcast(msg):
    if msg.has_key("id") is False:
        return
    broadcastMessageId = msg["id"]

    mongo = db.connect_mongo()
    collection_atMessage = mongo.log.broad_mesaage
    item = collection_atMessage.find_one({"_id": ObjectId(broadcastMessageId)})

    if item is not None:
        broadcastmsg = {"broadcast_message_id": str(item["_id"]), "sender": item["user_id"]}

        collection_m4u = mongo.message.message_4_user
        item_m4u = collection_m4u.find_one({"broadcast_message_id": broadcastmsg["broadcast_message_id"]})
        if item_m4u is not None:
            logger.info("Existed message_4_user for broadcast_message_id: %s", broadcastmsg["broadcast_message_id"])

        receivers = get_organizationUsers(item["organizationId"])
        for receiver in receivers:
            if isinstance(receiver,int) is False or receiver == item["user_id"]:
                continue
            broadcastmsg_user = {"broadcast_message_id": str(item["_id"]), "sender": item["user_id"],
                          "receiver": receiver}
            save_message_4_user(broadcastmsg_user)
    else:
        logger.info("broadcast_message not found id: %s", broadcastMessageId)
    mongo.close()



if __name__ == '__main__':
    init_kafka()
    while True:
        try:
            logger.info("start")
            # logger.info(kafkaConsumer)
            for message in kafkaConsumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                     message.offset, message.key,
                                                     message.value))
                    msg = json.loads(message.value)
                    #msg: type:XXXX, id :xxxx
                    if msg["type"] == "deal_log":
                        process_deal_log(msg)
                    elif msg["type"] == "at":
                        process_at(msg)
                    elif msg["type"] == "broadcast":
                        process_broadcast(msg)
                    else:
                        logger.info("Message: %s not deal or at or broadcast", msg)
                    kafkaConsumer.commit()
                except Exception,e :
                    traceback.print_exc()
                break
        except KeyboardInterrupt:
            logger.info("break1")
            exit(0)
        except Exception,e :
            logger.exception(e)
            traceback.print_exc()
            time.sleep(60)
            init_kafka()