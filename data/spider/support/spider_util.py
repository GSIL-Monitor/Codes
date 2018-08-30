#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-

import sys,os
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer)


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import config
import db
import loghelper

import gridfs

#mongo
mongo = db.connect_mongo()
fromdb = mongo.crawler_v2
filefs = gridfs.GridFS(mongo.gridfs)

def spider_init(spider_name):
    #logger
    loghelper.init_logger("spider("+spider_name+")", stream=True)
    logger = loghelper.get_logger("spider("+spider_name+")")

    mongo = db.connect_mongo()
    kafka_producer = kafka_init()

    #
    company_collection = mongo.crawler_v2.company
    company_collection.create_index([("source", pymongo.DESCENDING), ("company_key", pymongo.DESCENDING)], unique=True)
    member_collection = mongo.crawler_v2.member
    member_collection.create_index([("source", pymongo.DESCENDING), ("member_key", pymongo.DESCENDING)], unique=True)
    news_collection = mongo.crawler_v2.news
    news_collection.create_index([("source", pymongo.DESCENDING),("company_key", pymongo.DESCENDING),("news_key", pymongo.DESCENDING)], unique=True)
    investor_collection = mongo.crawler_v2.investor
    investor_collection.create_index([("source", pymongo.DESCENDING), ("investor_key", pymongo.DESCENDING)], unique=True)


    return logger, mongo, kafka_producer, company_collection, member_collection, news_collection, investor_collection


def spider_recruit_init(spider_name):
    #logger
    loghelper.init_logger("spider("+spider_name+")", stream=True)
    logger = loghelper.get_logger("spider("+spider_name+")")

    mongo = db.connect_mongo()
    kafka_producer = kafka_init()

    #
    company_collection = mongo.crawler_v2.company
    company_collection.create_index([("source", pymongo.DESCENDING), ("company_key", pymongo.DESCENDING)], unique=True)
    member_collection = mongo.crawler_v2.member
    member_collection.create_index([("source", pymongo.DESCENDING), ("member_key", pymongo.DESCENDING)], unique=True)
    news_collection = mongo.crawler_v2.news
    news_collection.create_index([("source", pymongo.DESCENDING),("company_key", pymongo.DESCENDING),("news_key", pymongo.DESCENDING)], unique=True)
    job_collection = mongo.crawler_v2.job
    job_collection.create_index([("source", pymongo.DESCENDING), ("company_key", pymongo.DESCENDING), ("job_key", pymongo.DESCENDING)], unique=True)

    return logger, mongo, kafka_producer, company_collection, member_collection, news_collection, job_collection


def spider_cf_init(spider_name):
    #logger
    loghelper.init_logger("spider("+spider_name+")", stream=True)
    logger = loghelper.get_logger("spider("+spider_name+")")

    mongo = db.connect_mongo()
    kafka_producer = kafka_init()

    #
    company_collection = mongo.crawler_v2.company
    company_collection.create_index([("source", pymongo.DESCENDING), ("company_key", pymongo.DESCENDING)], unique=True)
    member_collection = mongo.crawler_v2.member
    member_collection.create_index([("source", pymongo.DESCENDING), ("member_key", pymongo.DESCENDING)], unique=True)
    news_collection = mongo.crawler_v2.news
    news_collection.create_index([("source", pymongo.DESCENDING),("company_key", pymongo.DESCENDING),("news_key", pymongo.DESCENDING)], unique=True)
    cf_collection = mongo.crawler_v2.cf
    cf_collection.create_index([("source", pymongo.DESCENDING), ("company_key", pymongo.DESCENDING), ("cf_key", pymongo.DESCENDING)], unique=True)

    return logger, mongo, kafka_producer, company_collection, member_collection, news_collection, cf_collection




def spider_market_init(spider_name):
    loghelper.init_logger("spider("+spider_name+")", stream=True)
    logger = loghelper.get_logger("spider("+spider_name+")")

    mongo = db.connect_mongo()
    kafka_producer = kafka_init()

    return logger, mongo, kafka_producer


def spider_trends_init(spider_name):
    #logger
    loghelper.init_logger("spider("+spider_name+")", stream=True)
    logger = loghelper.get_logger("spider("+spider_name+")")

    mongo = db.connect_mongo()
    mysql = db.connect_torndb()
    kafka_producer = kafka_init()

    alexa_collection = mongo.crawler_v2.trends_alexa
    alexa_collection.create_index([("domain", pymongo.DESCENDING), ("date", pymongo.DESCENDING)], unique=True)

    return logger, mongo, mysql, kafka_producer, alexa_collection


def spider_direct_news_init(spider_name):
    #logger
    loghelper.init_logger("spider("+spider_name+")", stream=True)
    logger = loghelper.get_logger("spider("+spider_name+")")

    mongo = db.connect_mongo()
    kafka_producer = kafka_init()

    #
    news_collection = mongo.crawler_v2.direct_news
    news_collection.create_index([("source", pymongo.DESCENDING),("news_key", pymongo.DESCENDING)], unique=True)

    return logger, mongo, kafka_producer, news_collection



def kafka_init():
    (kafka_url) = config.get_kafka_config()
    kafka = KafkaClient(kafka_url)
    kafka_producer = SimpleProducer(kafka)

    return kafka_producer


def save_pdf(value, source, cf_key):
    file_id = filefs.put(value, content_type='application/pdf', filename='%s_%s.pdf' % (source, cf_key))
    return file_id



if __name__ == '__main__':
    spider_name = 'recurit_lagou'
    print spider_init(spider_name)
