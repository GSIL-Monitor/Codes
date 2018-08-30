# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
import json
import traceback
from kafka import KafkaConsumer
import process_topic_message
import process_company_message
import process_investor_message

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, config, db

#logger
loghelper.init_logger("init_user_message", stream=True)
logger = loghelper.get_logger("init_user_message")


# kafka
kafkaConsumer = None

def init_kafka():
    global kafkaConsumer
    (url) = config.get_kafka_config()
    # HashedPartitioner is default
    kafkaConsumer = KafkaConsumer("init_user_message", group_id="init_user_message",
                bootstrap_servers=[url],
                auto_offset_reset='smallest',
                enable_auto_commit=False)


def init_user_message(user_id):
    mongo = db.connect_mongo()
    conn = db.connect_torndb()
    logger.info("topic message")
    topics = conn.query("select * from user_topic_subscription"
                                " where userId=%s and active='Y'", user_id)
    for s in topics:
        logger.info("topicId: %s", s["topicId"])
        process_topic_message.subscribe(user_id, s["topicId"])

    logger.info("company message")
    companies = conn.query("select * from user_company_subscription"
                           " where userId=%s and active='Y' and companyId is not null", user_id)
    for c in companies:
        logger.info("companyId: %s", c["companyId"])
        process_company_message.subscribe(user_id, c["companyId"])

    logger.info("investor message")
    investors = conn.query("select * from user_investor_subscription"
                           " where userId=%s and active='Y'", user_id)
    for v in investors:
        logger.info("investorId: %s", v["investorId"])
        # process_investor_message.subscribe(user_id, v["investorId"]) # TODO test

    conn.close()
    mongo.close()

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
                    user_id = msg["userId"]
                    kafkaConsumer.commit()
                    time.sleep(10)  # 避免和订阅处理并发
                    init_user_message(user_id)
                except Exception, e:
                    traceback.print_exc()
        except KeyboardInterrupt:
            exit(0)
        except Exception, e:
            logger.exception(e)
            traceback.print_exc()
            init_kafka()


if __name__ == '__main__':
    main()