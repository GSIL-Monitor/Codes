# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html

from bson.objectid import ObjectId
from pyquery import PyQuery as pq
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../nlp/score'))
import requests
import util
import parser_util
from relatedness import RelatednessScorer
rs = RelatednessScorer()

import loghelper
import config
from pymongo import MongoClient
import gridfs
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)



#logger
loghelper.init_logger("news_aggregator", stream=True)
logger = loghelper.get_logger("news_aggregator")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
crawlerdb = mongo.crawler_v2
parserdb = mongo.parser_v2
imgfs = gridfs.GridFS(mongo.gridfs)

#mysql
conn = None

# kafka
kafkaProducer = None
kafkaConsumer = None


def initKafka():
    global kafkaProducer
    global kafkaConsumer

    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("news_parser", group_id="news_aggregator",
                metadata_broker_list=[url],
                auto_offset_reset='smallest')


def merge_news(news_key):
    parser_news = parserdb.direct_news.find_one({"news_key":news_key})
    if parser_news == None:
        return

    content = parser_news["content"]
    title =  parser_news["title"]
    name = parser_news['search_name']
    companyId = parser_news['company_id']

    flag = rs.compare(companyId, name=name, title=title, content=content)
    print flag


    # try:
    #     article = pq(content)('.article-detail')
    #     d = pq(article)
    #     title= d('div.title > h1').text()
    #     news_time = d('.subtitle > .time').text()
    #
    #     content = d('.article-content').text()

    #     news_content = {"date":datetime.datetime.now(),
    #                     "news_key":news_key,
    #                     "source":source,
    #                     "url":news['url'],
    #                     "title" : title,
    #                     "news_time": news_time,
    #                     "content":content,
    #                     "company_id": news['companyId']}
    #
    #     if news_collection.find_one({"source":source, "news_key":news_key}) != None:
    #         news_collection.delete_one({"source":source, "news_key":news_key})
    #     news_collection.insert_one(news_content)
    #
    #     msg = {"type":"direct_news", "news_key": news_key}
    #     logger.info(msg)
    #     kafka_producer.send_messages("news_parser", json.dumps(msg))
    #
    # except:
    #     traceback.print_exc()



if __name__ == '__main__':
    logger.info("news aggregator start")
    initKafka()
    while True:
        try:
            for message in kafkaConsumer:
                try:
                    # logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                    #                                            message.offset, message.key,
                    #                                            message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    news_key = msg["news_key"]

                    if type == "direct_news_parser":
                        merge_news(news_key)

                    # kafka_consumer.task_done(message)
                    # kafka_consumer.commit()
                except Exception,e :
                    logger.error(e)
                    traceback.print_exc()
        except Exception,e :
            logger.error(e)
            traceback.print_exc()
            time.sleep(60)
            initKafka()
