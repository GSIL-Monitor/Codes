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
import db

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
company_collection = mongo.crawler_v2.company

if __name__ == "__main__":
    logger.info("Start...")
    if len(sys.argv) > 2:
        source = int(sys.argv[1])
        topic = sys.argv[2]
    else:
        print "usage: python gen_messages.py 13020 beian_v2"
        exit(0)

    conn = db.connect_torndb()
    companies = conn.query("select * from source_company where source=%s", source)
    conn.close()
    for c in companies:
        msg = {"type":"company", "id":c["id"]}
        logger.info(msg)
        kafka_producer.send_messages(topic, json.dumps(msg))
