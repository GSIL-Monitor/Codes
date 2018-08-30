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
loghelper.init_logger("patch", stream=True)
logger = loghelper.get_logger("patch")

c1 = 0
c2 = 0
def save_message_4_deal(msg):
    global  c1
    global  c2
    mongo = db.connect_mongo()
    collection_m4d = mongo.message.message_4_deal
    item = collection_m4d.find_one({"deal_id": msg["deal_id"],"deal_log_id": msg["deal_log_id"]})
    if item is None:
        collection_m4d.insert_one(msg)
        logger.info("Insert new message_4_deal for deal_id:%s, deal_log_id: %s", msg["deal_id"], msg["deal_log_id"])
        c1 += 1
    else:
        logger.info("Existed message_4_deal for deal_id:%s, deal_log_id: %s", msg["deal_id"], msg["deal_log_id"])
        c2 += 1
    mongo.close()


if __name__ == '__main__':

    mongo = db.connect_mongo()
    collection_dealLog = mongo.log.deal_log
    items = list(collection_dealLog.find({}))
    for item in items:
        dealmsg = {"deal_log_id": str(item["_id"]), "deal_id": item["deal_id"], "createTime":item["createTime"]}
        save_message_4_deal(dealmsg)

    logger.info("%s, %s", c1, c2)


