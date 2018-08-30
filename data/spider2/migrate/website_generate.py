# -*- coding: utf-8 -*-
import os, sys
import datetime
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config, util, db, url_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../crawler/website'))
import website

#logger
loghelper.init_logger("website_generate", stream=True)
logger = loghelper.get_logger("website_generate")

#mongo
mongo = db.connect_mongo()
collection = mongo.info.website

beian_collection = mongo.info.beian

raw_urls = []


def run():
    global raw_urls
    while True:
        if len(raw_urls) == 0:
            return
        url = raw_urls.pop(0)
        item = collection.find_one({"url":url})
        if item is not None:
            continue

        flag,domain = url_helper.get_domain(url)

        result = website.get_meta_info(url)
        logger.info(url)
        logger.info(json.dumps(result, ensure_ascii=False, cls=util.CJsonEncoder))
        if result is None:
            result = {
                "url":url,
                "httpcode": 404
            }
        else:
            if result["url"] != result["redirect_url"]:
                new_url = url_helper.url_normalize(result["redirect_url"])
                flag1, domain1 = url_helper.get_domain(new_url)
                if domain != domain1:
                    raw_urls.append(new_url)
        result["createTime"] = datetime.datetime.now()
        result["modifyTime"] = result["createTime"]
        try:
            collection.insert(result)
        except:
            pass



def start_run(concurrent_num):
    global raw_urls

    logger.info("website start...")

    items = beian_collection.find({})
    for item in items:
        if item["domain"] is None or item["domain"] == "":
            continue

        url = "http://www." + item["domain"]
        logger.info(url)
        raw_urls.append(url)

    conn =db.connect_torndb()
    items = conn.query("select * from artifact where type=4010")
    for item in items:
        url = item["link"]
        if url is None or url == "":
            continue
        url = url_helper.url_normalize(url)
        logger.info(url)
        raw_urls.append(url)
    conn.close()


    threads = [gevent.spawn(run) for i in xrange(concurrent_num)]
    gevent.joinall(threads)

    logger.info("website end.")


if __name__ == "__main__":
    start_run(50)