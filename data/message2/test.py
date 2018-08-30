# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
import json
from kafka import (KafkaClient, SimpleProducer)
from bson.code import Code

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, config

#logger
loghelper.init_logger("test", stream=True)
logger = loghelper.get_logger("test")


# kafka
kafkaProducer = None

def init_kafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)


def send_message(userId, type):
    if kafkaProducer is None:
        init_kafka()

    msg = {"action":"notify_new_message", "userId": userId, "type": type}
    while True:
        try:
            kafkaProducer.send_messages("websocket_app", json.dumps(msg))
            logger.info(msg)
            break
        except Exception,e :
            logger.exception(e)
            time.sleep(60)
            init_kafka()


if __name__ == '__main__':
    # user_id = int(sys.argv[1])
    # type = sys.argv[2]
    # send_message(user_id, type)
    mongo = db.connect_mongo()
    # items = mongo.message.user_message.find({"topicMessageId":39658}).sort("_id", 1)
    # for item in items:
    #     logger.info("%s - %s", item["_id"].generation_time.strftime("%Y/%m/%d %H:%M:%S"), item["userId"])

    mapper_topic_message = Code("""
        function () {
            if(!!this.topicMessageId){
                emit(this.userId + "-" + this.topicMessageId, 1);
            }
        }
    """)

    mapper_company_message = Code("""
            function () {
                if(!!this.companyMessageId){
                    emit(this.userId + "-" + this.companyMessageId, 1);
                }
            }
        """)

    reducer = Code("""
        function (key, values) {
            var total = 0;
            for (var i = 0; i < values.length; i++) {
                total += values[i];
            }
            return total;
        }
    """)

    result = mongo.message.user_message.map_reduce(mapper_topic_message, reducer, out="dup_topic_message",
                                                  full_response=True, query={})
    # result = mongo.message.user_message.map_reduce(mapper_company_message, reducer, out="dup_company_message",
    #                                                full_response=True, query={})
    items = list(mongo.message.dup_topic_message.find({"value":{"$gt":1}}))
    for item in items:
        logger.info(item)
        r = item["_id"].split("-")
        user_id = int(r[0])
        topic_message_id = int(r[1])

        ms = list(mongo.message.user_message.find({"topicMessageId": topic_message_id, "userId": user_id}))
        for m in ms[1:]:
            logger.info(m)
            mongo.message.user_message.remove({"_id":m["_id"]})
        # exit()
    #
    # items = list(mongo.message.dup_company_message.find({"value":{"$gt":1}}))
    # for item in items:
    #     logger.info(item)
    #     r = item["_id"].split("-")
    #     user_id = int(r[0])
    #     company_message_id = int(r[1])
    #
    #     ms = list(mongo.message.user_message.find({"companyMessageId": company_message_id, "userId": user_id}))
    #     for m in ms[1:]:
    #         logger.info(m)
    #         mongo.message.user_message.remove({"_id":m["_id"]})
    #     # exit()
