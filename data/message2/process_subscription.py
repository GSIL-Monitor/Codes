# -*- coding: utf-8 -*-
import os, sys
import time
import json
import traceback
from kafka import KafkaConsumer
import process_topic_message
import process_company_message
import process_investor_message

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, config

#logger
loghelper.init_logger("process_subscription", stream=True)
logger = loghelper.get_logger("process_subscription")


# kafka
kafkaConsumer = None

def init_kafka():
    global kafkaConsumer
    (url) = config.get_kafka_config()
    # HashedPartitioner is default
    kafkaConsumer = KafkaConsumer("subscription", group_id="process_subscription",
                bootstrap_servers=[url],
                auto_offset_reset='smallest',
                enable_auto_commit=False)


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
                    try:
                        msg = json.loads(message.value)
                    except:
                        kafkaConsumer.commit()
                        continue

                    type = msg["type"]
                    action = msg["action"]
                    user_id = msg["userId"]
                    if type == "topic":
                        topic_id = msg["id"]
                        if action == 'create':
                            process_topic_message.subscribe(user_id, topic_id)
                            pass
                        elif action == 'delete':
                            process_topic_message.unsubscribe(user_id, topic_id)
                    elif type == "company":
                        company_id = msg["id"]
                        if action == 'create':
                            process_company_message.subscribe(user_id, company_id)
                            pass
                        elif action == 'delete':
                            process_company_message.unsubscribe(user_id, company_id)
                    elif type == "investor":
                        investor_id = msg["id"]
                        if action == 'create':
                            process_investor_message.subscribe(user_id, investor_id)
                            pass
                        elif action == 'delete':
                            process_investor_message.unsubscribe(user_id, investor_id)
                            pass
                    kafkaConsumer.commit()
                except Exception, e:
                    traceback.print_exc()
                    # exit(0)
        except KeyboardInterrupt:
            exit(0)
        except Exception, e:
            logger.exception(e)
            traceback.print_exc()
            time.sleep(60)
            init_kafka()


if __name__ == '__main__':
    main()