# -*- coding: utf-8 -*-
import os, sys
import traceback
import time
import json

from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import config
import loghelper

#logger
loghelper.init_logger("kafka_test", stream=True)
logger = loghelper.get_logger("kafka_test")


# kafka
kafkaProducer = None
kafkaConsumer = None

def init_kafka():
    global kafkaProducer, kafkaConsumer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("test", group_id="test2",
                bootstrap_servers=[url],
                auto_offset_reset='smallest')

def send_message(message):
    if kafkaProducer is None:
        init_kafka()

    #action: create, delete
    msg = {"type":"user_notify",
           "userId":1,
           "message":message}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("websocket", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)


if __name__ == '__main__':
    init_kafka()
    send_message("_id from monogodb")
    exit()

    while True:
        try:
            for message in kafkaConsumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                     message.offset, message.key,
                                                     message.value))
                    kafkaConsumer.commit()
                except Exception,e :
                    traceback.print_exc()
        except KeyboardInterrupt:
            exit(0)
        except Exception,e :
            logger.exception(e)
            traceback.print_exc()
            time.sleep(60)
            init_kafka()