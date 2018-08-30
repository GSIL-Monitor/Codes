# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import json
import traceback
from kafka import (KafkaConsumer, KafkaClient, SimpleProducer)
import process_util
import umeng

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, config, db

#logger
loghelper.init_logger("push_hot_news", stream=True)
logger = loghelper.get_logger("push_hot_news")


# kafka
kafkaConsumer = None
kafkaProducer = None

def init_kafka():
    global kafkaConsumer
    global kafkaProducer
    (url) = config.get_kafka_config()
    # HashedPartitioner is default
    kafkaConsumer = KafkaConsumer("track_message_v2", group_id="push_hot_news",
                bootstrap_servers=[url],
                auto_offset_reset='smallest',
                enable_auto_commit=False)
    kafka = KafkaClient(url)
    kafkaProducer = SimpleProducer(kafka)


def process(topic_message_id):
    if topic_message_id is None:
        return

    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    m = conn.get("select * from topic_message where id=%s", topic_message_id)
    if m is not None and m["active"] == 'Y' and m["topicId"] == 55:
        publish_time = m["publishTime"]
        now = datetime.datetime.now()
        if publish_time > now - datetime.timedelta(hours=8):
            message = m["message"]
            logger.info(message)
            data = {"newsId": m["relateId"]}

            log = mongo.log.ios_push_log.find_one({"topicMessageId": topic_message_id})
            if log is None:
                umeng.sendIOSBroadcast("", message, 0, messageType="hot_news", test=False, data=data)
                umeng.sendIOSBroadcast("personal", message, 0, messageType="hot_news", test=False, data=data)
                mongo.log.ios_push_log.insert(
                    {"topicMessageId":topic_message_id,
                      "time":datetime.datetime.utcnow()
                     }
                )

            # user_ids = conn.query("select distinct userId from user_token where deviceId is not null and deviceId !=''")
            # for _user_id in user_ids:
            #     user_id = _user_id["userId"]
            #     # if user_id not in [1078, 3142, 1091, 1092]:
            #     #     continue
            #     # if user_id not in [1078, 3142]:
            #     #     continue
            #     user_tokens = process_util.get_tokens(conn, user_id)
            #     for user_token in user_tokens:
            #         device_id = user_token["deviceId"]
            #         if device_id is None or device_id.strip() == "":
            #             continue
            #         log = mongo.log.ios_push_log.find_one({"topicMessageId":topic_message_id, "deviceId": device_id})
            #         if log is None:
            #             logger.info("sendIOSUnicast, userId:%s , device_id:%s", user_id, device_id)
            #             umeng.sendIOSUnicast(message, 0, device_id, messageType="hot_news", test=False, data=data)
            #             mongo.log.ios_push_log.insert(
            #                 {"topicMessageId":topic_message_id,
            #                  "deviceId": device_id,
            #                  "time":datetime.datetime.utcnow()})
        # exit(0)
    mongo.close()
    conn.close()


def main():
    init_kafka()
    while True:
        try:
            logger.info("start")
            for message in kafkaConsumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                               message.offset, message.key,
                                                               message.value))
                    msg = json.loads(message.value)
                    kafkaConsumer.commit()
                    type = msg["type"]
                    action = msg["action"]
                    if type == "topic_message":
                        topic_message_id = msg.get("id")
                        if action == 'create':
                            process(topic_message_id)
                except Exception, e:
                    traceback.print_exc()
                    # exit(0) # Test
        except KeyboardInterrupt:
            exit(0)
        except Exception, e:
            logger.exception(e)
            traceback.print_exc()
            time.sleep(60)
            init_kafka()


if __name__ == '__main__':
    main()