# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer)

from pyquery import PyQuery as pq
import datetime, time
import json, re
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import spider_util, util
import proxy_pool
import db, config
from pyquery import PyQuery as pq


cnt = 0
total = 0

def request(url, callback):
    logger.info(url)
    http_client.fetch(url, callback,request_timeout=10)


def handle_result(response, website):
    global total
    if response.error:
        # url = website['link']
        delete(website)
    else:
        try:
            if response.code != 200:
                delete(website)
            else:
                # html = unicode(response.body,encoding="utf-8",errors='replace')
                html = util.html_encode(response.body)
                doc = pq(html)
                metas = doc('meta')
                description = None
                keywords = None
                for meta in metas:
                    name =  pq(meta).attr('name')
                    content =  pq(meta).attr('content')
                    if name == 'keywords':
                        keywords = content
                    if name == 'description':
                        description = content

                update(description, keywords, website)

        except:
            traceback.print_exc()

    total -= 1
    if total <= 0:
        begin()


def update(description, keywords, website):
    logger.info("updating ...  id=%s", website['id'])
    if keywords is not None:
        if len(keywords) > 200:
            keywords = keywords[:199]

    logger.info(description)
    logger.info(keywords)

    conn = db.connect_torndb()
    if description is None and keywords is None:
        update_sql = "update artifact set active='Y' where id=%s"
        conn.update(update_sql, website['id'])
    else:
        if website['description'] is not None:
            update_sql = "update artifact set tags=%s, active='Y' where id=%s"
            conn.update(update_sql, keywords, website['id'])
        else:
            update_sql = "update artifact set description=%s, tags=%s, active='Y' where id=%s"
            conn.update(update_sql, description, keywords, website['id'])
    conn.close()



def delete(website):
    logger.info("deleting ...  id=%s", website['id'])
    conn = db.connect_torndb()
    update_sql = "update artifact set verify = 'N', active='N' where id=%s"
    conn.update(update_sql, website['id'])
    conn.close()

def begin():
    global cnt
    global total
    conn = db.connect_torndb()

    websites = conn.query("select * from artifact where type = 4010 and active='Y' limit %s,1000", cnt)
    logger.info('Done count = %s', cnt)
    if len(websites) == 0:
        logger.info("Finish.")
        exit()
    for website in websites:
        cnt += 1
        total += 1
        url = website['link']
        request(url, lambda r, website=website:handle_result(r, website))
    conn.close()


if __name__ == "__main__":
    (logger, mongo, kafka_producer, news_collection) \
        = spider_util.spider_direct_news_init('website_verify')
    logger.info("Start...")

    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()

