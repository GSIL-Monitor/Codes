# -*- coding: utf-8 -*-
import os, sys
import datetime
import random
import json
import lxml.html
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer)

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import util

#logger
loghelper.init_logger("gen_messages", stream=True)
logger = loghelper.get_logger("gen_messages")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)

#kafka
(kafka_url) = config.get_kafka_config()
kafka = KafkaClient(kafka_url)
# HashedPartitioner is default
kafka_producer = SimpleProducer(kafka)

#
news_collection = mongo.crawler_v2.direct_news

if __name__ == "__main__":
    logger.info("Start...")
    if len(sys.argv) > 2:
        source = sys.argv[1]
        topic = sys.argv[2]
    else:
        print "usage: python gen_messages.py toutiao toutiao"
        exit(0)

    # companies = company_collection.find({"source":source}).sort("company_key_int", pymongo.DESCENDING)
    news_list = news_collection.find({"source":source})
    for news in news_list:
        msg = {"type":"direct_news", "source":source, "news_key":news["news_key"]}
        logger.info(json.dumps(msg))
        kafka_producer.send_messages(topic, json.dumps(msg))
