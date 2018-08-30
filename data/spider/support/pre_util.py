#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-

import sys,os
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)



reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import config
import db
import loghelper

import gridfs


def pre_init(logger_name, parser_name, group_name):
    #logger
    loghelper.init_logger("pre("+logger_name+")", stream=True)
    logger = loghelper.get_logger("pre("+logger_name+")")

    mongo = db.connect_mongo()
    (kafka_producer, kafka_consumer) = kafka_init(parser_name, group_name)



    return logger, mongo, kafka_producer, kafka_consumer


def kafka_init(parser_name, group_name):
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    kafka_producer = SimpleProducer(kafka)
    kafka_consumer = KafkaConsumer(parser_name, group_id= group_name,
                metadata_broker_list=[url],
                auto_offset_reset='smallest')


    return kafka_producer, kafka_consumer


