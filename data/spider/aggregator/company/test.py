# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html
from pymongo import MongoClient
import gridfs
import pymongo
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)
from tld import get_tld
from urlparse import urlsplit
import tldextract
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import util
import db
import extract
import aggregator_util
import trends_tool

#logger
loghelper.init_logger("itjuzi_parser", stream=True)
logger = loghelper.get_logger("itjuzi_parser")


# kafka
kafkaProducer = None
kafkaConsumer = None


def initKafka():
    global kafkaProducer
    global kafkaConsumer

    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaConsumer = KafkaConsumer("aggregator_v2", group_id="test",
                metadata_broker_list=[url],
                auto_offset_reset='smallest')

if __name__ == '__main__':
    logger.info("test start")
    initKafka()

    while True:
        try:
            for message in kafkaConsumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                     message.offset, message.key,
                                                     message.value))
                    msg = json.loads(message.value)

                except Exception,e :
                    logger.exception(e)
                finally:
                    #kafkaConsumer.task_done(message)
                    #kafkaConsumer.commit()
                    pass

        except KeyboardInterrupt:
            exit(0)
        except Exception,e :
            logger.exception(e)
            time.sleep(60)
            initKafka()