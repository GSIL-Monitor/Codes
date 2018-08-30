#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import datetime
import json
import pymongo
from pymongo import MongoClient


reload(sys)
sys.setdefaultencoding("utf-8")
import my_request
import util
import spider_util

from kafka import (KafkaClient, SimpleProducer)
import config
import db
import loghelper


def fetch(url):
    (key, ) = util.re_get_result("https://itjuzi.com/album/(\d+)", url)
    logger.info("key=%s" % key)

    (flag, r) = my_request.get(logger, url)
    logger.info("flag=%d", flag)

    if flag == -1:
        return -1

    if r.status_code == 404:
        logger.info("Page Not Found!!!")
        return r.status_code

    if r.status_code != 200:
        return r.status_code

    if r.url != url:
        logger.info("Page Redirect <--")
        return 302


    content = { "date":datetime.datetime.now(),
                "url":url,
                "key":key,
                "content":r.text}


    # save
    if collection.find_one({"key":key}) != None:
        collection.delete_one({"key":key})
    collection.insert_one(content)

    # msg = {"type":"itjuzi_album", "key":key}
    # logger.info(json.dumps(msg))
    # kafka_producer.send_messages("itjuzi_album", json.dumps(msg))

    return 200

if __name__ == "__main__":

    loghelper.init_logger("spider(itjuzi_album)", stream=True)
    logger = loghelper.get_logger("spider(itjuzi_album)")

    mongo = db.connect_mongo()
    kafka_producer = spider_util.kafka_init()

    #
    collection = mongo.crawler_v2.itjuzi_album
    collection.create_index([("key", pymongo.DESCENDING)], unique=True)


    type = 'incr'
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            type = 'all'
        else:
            type = 'incr'

    cnt = 0
    latest_album = []
    if type == 'incr':
        latest_album = collection.find({}).sort("key", pymongo.DESCENDING).limit(1)
    if latest_album.count() == 0:
        i = 0
    else:
        i = int(latest_album[0]["key"])

    latest = i
    logger.info("From: %d" % i)

    while True:
        i += 1
        url = "https://itjuzi.com/album/%d" % (i)

        if cnt <= 0:
            my_request.get_https_session()
            cnt = 100

        status = -1
        retry_times = 0
        while status != 200 and status !=404 and status != 302:
            try:
                status = fetch(url)
            except Exception,ex:
                logger.exception(ex)

            if status == -1:
                my_request.get_http_session(new=True, agent=False)
                cnt = 100

            retry_times += 1
            if retry_times >= 3:
                break

        cnt -= 1

        if status == 200:
            latest = i

        if latest < i - 100:
            break

