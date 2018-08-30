# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html

from bson.objectid import ObjectId
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import requests
import util
import parser_util
from pyquery import PyQuery as pq


source = 'pencil_news'
def parse_news(news_key):
    news = fromdb.direct_news.find_one({"source": source, "news_key":news_key})
    if news == None:
        return

    content = news["content"]

    main = pq(content)('main.single > section > article')
    d = pq(main)
    title = d('h1 > a').text()
    url = d('h1 > a').attr('href')
    news_time = d('.details > .date').text()
    content = d('.content > section').text()

    if content is None or content == '':
        return

    # print title
    # print url
    # print news_time
    # print content


    news_content = {"date":datetime.datetime.now(),
                    "news_key":news_key,
                    "source":source,
                    "url":url,
                    "title" : title,
                    "news_time": news_time,
                    "content":content}


    # save
    if news_collection.find_one({"source":source, "news_key":news_key}) != None:
        news_collection.delete_one({"source":source, "news_key":news_key})
    news_collection.insert_one(news_content)

    # msg = {"type":"direct_news", "id":source_company_id}
    # logger.info(msg)
    # kafka_producer.send_messages("parser_v2", json.dumps(msg))


if __name__ == '__main__':
    (logger, fromdb, kafka_producer, kafka_consumer, news_collection) = parser_util.parser_news_init("pencil_news", "pencil_news")

    i = 0
    threads = []
    msgs = []
    while True:
        try:
            for message in kafka_consumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                               message.offset, message.key,
                                                               message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    news_key = msg["news_key"]

                    if type == "direct_news":
                        parse_news(news_key)

                    kafka_consumer.task_done(message)
                    kafka_consumer.commit()
                except Exception,e :
                    logger.error(e)
                    traceback.print_exc()
        except Exception,e :
            logger.error(e)
            traceback.print_exc()
            time.sleep(60)
            (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("pencil_news", "pencil_news")
