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


cnt = 0
total = 0

SOURCE = 'toutiao'

def request(url, callback):
    global total
    proxy = {'type': 'http', 'anonymity':'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)

    http_client.fetch(url, callback, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),request_timeout=10)

def handle_result(response, company):
    global total
    if response.error:
        # logger.info("Error: %s, %s" % (response.error,response.request.url))
        url = 'http://toutiao.com/search_content/?offset=0&format=json&keyword='+company['name']+'&autoload=true&count=20'
        request(url, lambda r,company=company:handle_result(r, company))
        # logger.info('erroring .....')
        return
    # logger.info(response.request.url)
    try:
        logger.info(company['name'])
        result = json.loads(response.body)
        if result['message'] == 'success':
            # logger.info(result)
            if 'data' in result:
                data = result['data']
                for news in data:
                    url = news['share_url']
                    request(url, lambda r,company=company:handle_news_result(r, company))
    except:
        traceback.print_exc()

    total -= 1
    if total <= 0:
        begin()


def handle_news_result(response, company):
    if response.effective_url != response.request.url:
        if 'toutiao.com' not in response.effective_url:
            logger.info(response.effective_url)
            logger.info(response.request.url)
            logger.info('url changed .....')
            return

    if response.error:
        # logger.info("Error: %s, %s" % (response.error,response.request.url))
        url = 'http://toutiao.com/search_content/?offset=0&format=json&keyword='+company['name']+'&autoload=true&count=20'
        request(url, lambda r,company=company:handle_result(r, company))
        # logger.info('erroring .....')
        return
    try:
        content = response.body
        save_news(company, response.request.url, content)
    except:
        traceback.print_exc()


def save_news(company, url, content):
    group_id = url.split('/group/')[1].split('/')[0]
    iid = url.split('?iid=')[1].split('&')[0]
    news_key = group_id+'-'+iid
    news_content ={"date":datetime.datetime.now(),
                   "source":SOURCE,
                   "url":url,
                   "news_key":news_key,
                   "company_id": int(company['id']),
                   "search_name": company['name'],
                   "content":content}
    logger.info(news_key)
    # save
    if news_collection.find_one({"source":SOURCE, "news_key":news_key}) is None:
        news_collection.insert_one(news_content)

    # msg = {"type":"direct_news", "source":SOURCE, "news_key":news_key}
    # logger.info(json.dumps(msg))
    # kafka_producer.send_messages("toutiao", json.dumps(msg))


def begin():
    global total, cnt
    conn = db.connect_torndb()

    companies = conn.query("select * from company order by id desc limit %s,1000", cnt)
    if len(companies) == 0:
        logger.info("Finish.")
        exit()

    for company in companies:
        cnt += 1
        total += 1
        url = 'http://toutiao.com/search_content/?offset=0&format=json&keyword='+company['name']+'&autoload=true&count=20'
        request(url, lambda r,company=company:handle_result(r, company))
    conn.close()


if __name__ == "__main__":
    (logger, mongo, kafka_producer, news_collection) \
        = spider_util.spider_direct_news_init('toutiao')
    logger.info("Start...")

    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()