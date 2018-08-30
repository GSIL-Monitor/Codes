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
import extract
from pyquery import PyQuery as pq


source = 'toutiao'
def parse_news(news_key):
    news = fromdb.direct_news.find_one({"source": source, "news_key":news_key})
    if news == None:
        return

    content = news["content"]

    try:
        article = pq(content)('.article-detail')
        d = pq(article)
        title= d('div.title > h1').text()
        news_time = d('.subtitle > .time').text()

        #content = d('.article-content').text()
        print title
        print news_time
        #print content

        contents = extract.extractContents(news["url"], content)

        news_content = {"date":datetime.datetime.now(),
                        "news_key":news_key,
                        "source":source,
                        "url":news['url'],
                        "title" : title,
                        "news_time": news_time,
                        "contents":contents,
                        "company_id": news['company_id'],
                        "search_name": news['search_name']
                        }

        if news_collection.find_one({"source":source, "news_key":news_key}) != None:
            news_collection.delete_one({"source":source, "news_key":news_key})
        news_collection.insert_one(news_content)

        msg = {"type":"direct_news_parser", "news_key": news_key}
        logger.info(msg)
        kafka_producer.send_messages("news_parser", json.dumps(msg))

    except:
        traceback.print_exc()




if __name__ == '__main__':
    (logger, fromdb, kafka_producer, kafka_consumer, news_collection) = parser_util.parser_news_init("toutiao", "toutiao")

    i = 0
    threads = []
    msgs = []
    while True:
        try:
            for message in kafka_consumer:
                try:
                    # logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                    #                                            message.offset, message.key,
                    #                                            message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    news_key = msg["news_key"]

                    if type == "direct_news":
                        parse_news(news_key)

                    # kafka_consumer.task_done(message)
                    # kafka_consumer.commit()
                except Exception,e :
                    logger.error(e)
                    traceback.print_exc()
        except Exception,e :
            logger.error(e)
            traceback.print_exc()
            time.sleep(60)
            (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("toutiao", "toutiao")
