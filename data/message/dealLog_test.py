# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import json
import traceback
from kafka import (KafkaClient, SimpleProducer)
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


def init_kafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)

init_kafka()

def send_message():
    #action: create, delete
    msg = {"type":"dddd", "id":"58216c254e39ee481ce99234"}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("track", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)

if __name__ == '__main__':
    send_message()