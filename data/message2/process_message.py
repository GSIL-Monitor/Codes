# -*- coding: utf-8 -*-
import os, sys
import time
import json
import traceback
from kafka import (KafkaConsumer, KafkaClient, SimpleProducer)
import process_topic_message
import process_topic_company
import process_company_message
import process_investor_message

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, config

#logger
loghelper.init_logger("process_message", stream=True)
logger = loghelper.get_logger("process_message")


# kafka
kafkaConsumer = None
kafkaProducer = None

def init_kafka():
    global kafkaConsumer
    global kafkaProducer
    (url) = config.get_kafka_config()
    # HashedPartitioner is default
    kafkaConsumer = KafkaConsumer("track_message_v2", group_id="process_topic_message",
                bootstrap_servers=[url],
                auto_offset_reset='smallest',
                enable_auto_commit=False,
                max_poll_records=5,
                session_timeout_ms=60000,
                request_timeout_ms=70000)
    kafka = KafkaClient(url)
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
                    kafkaConsumer.commit()
                    msg = json.loads(message.value)

                    type = msg["type"]
                    action = msg["action"]
                    if type == "topic_message":
                        topic_message_id = msg["id"]
                        if action == 'create':
                            process_topic_message.process(topic_message_id)
                            pass
                        elif action == 'delete':
                            process_topic_message.delete(topic_message_id)
                    elif type == "topic_company":
                        topic_company_id = msg["id"]
                        if action == 'create':
                            process_topic_company.process(topic_company_id)
                            pass
                        elif action == 'delete':
                            process_topic_company.delete(topic_company_id)
                    elif type == "company_message":
                        company_message_id = msg["id"]
                        if action == 'create':
                            process_company_message.process(company_message_id)
                            pass
                        elif action == 'delete':
                            process_company_message.delete(company_message_id)
                    elif type == "investor_message":
                        investor_message_id = msg["id"]
                        if action == 'create':
                            process_investor_message.process(investor_message_id)
                            pass
                        elif action == 'delete':
                            process_investor_message.delete(investor_message_id)
                        # exit(0) # Test
                    logger.info("Over.")
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