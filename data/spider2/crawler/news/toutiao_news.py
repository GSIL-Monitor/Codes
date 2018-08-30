# -*- coding: utf-8 -*-
import sys, os
import datetime, time
import json
import traceback
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import db
import loghelper
import proxy_pool
import util

#logger
loghelper.init_logger("toutiao_news", stream=True)
logger = loghelper.get_logger("toutiao_news")

#mongo
mongo = db.connect_mongo_local()
collection = mongo.raw.news

cnt = 0
total = 0
SOURCE = 'toutiao'

def request(url, callback):
    global total
    logger.info(url)
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
        #logger.info("Error: %s, %s" % (response.error,response.request.url))
        request(response.request.url, lambda r,company=company:handle_result(r, company))
        return
    # logger.info(response.request.url)
    try:
        #logger.info(company['name'])
        result = json.loads(response.body)
    except:
        #traceback.print_exc()
        request(response.request.url, lambda r,company=company:handle_result(r, company))
        return

    if result['message'] == 'success':
        # logger.info(result)
        if 'data' in result:
            data = result['data']
            cnt = 0
            for news in data:
                cnt += 1
                if cnt > 5:
                    break
                if collection.find_one({"source":SOURCE, "news_key":news["id"], "company_id":int(company['id'])}) is None:
                    url = news['share_url']
                    total += 1
                    request(url, lambda r,company=company,summary=news:handle_news_result(r, company, summary))
    else:
        request(response.request.url, lambda r,company=company:handle_result(r, company))
        return

    total -= 1
    if total <= 0:
        begin()
        #exit()


def handle_news_result(response, company, summary):
    global total
    if response.error:
        # logger.info("Error: %s, %s" % (response.error,response.request.url))
        if response.code == 404:
            content = response.body
            if content.find("404.jpg") > 0:
                total -= 1
                if total <= 0:
                    begin()
        request(response.request.url, lambda r,company=company:handle_news_result(r, company, summary))
        # logger.info('erroring .....')
        return

    logger.info(summary["title"])


    content_from_toutiao = True
    if response.effective_url != response.request.url:
        if 'toutiao.com' not in response.effective_url:
            #logger.info(response.effective_url)
            logger.info(response.request.url)
            logger.info('url changed .....')
            content_from_toutiao = False

    try:
        content = util.html_encode(response.body)
        if content_from_toutiao:
            if content.find(u"京ICP备12025439号") > 0:
                save_news(company, response.request.url, summary, content, content_from_toutiao)
            else:
                request(response.request.url, lambda r,company=company:handle_news_result(r, company, summary))
                return
        else:
            save_news(company, response.request.url, summary, content, content_from_toutiao)
    except:
        traceback.print_exc()

    total -= 1
    if total <= 0:
        begin()
        #exit()


def save_news(company, url, summary, content, content_from_toutiao):
    news_key = summary["id"]
    #logger.info(news_key)
    news_content ={
                    "news_key":news_key,
                    "company_id": int(company['id']),
                    "publish_time":summary["publish_time"],
                    "title":summary["title"],
                    "share_url":summary["share_url"],
                    "url":summary["url"],
                    "create_time":datetime.datetime.now(),
                    "source":SOURCE,
                    "search_name": company['name'],
                    "summary":summary,
                    "content":content,
                    "content_from_toutiao": content_from_toutiao}

    # save
    if collection.find_one({"source":SOURCE, "news_key":news_key}) is None:
        collection.insert_one(news_content)


def begin():
    global total, cnt
    conn = db.connect_torndb()

    companies = conn.query("select * from company order by id limit %s,100", cnt)
    #companies = conn.query("select * from company where id in (881, 152766) order by id limit %s,100", cnt)
    if len(companies) == 0:
        logger.info("Finish.")
        total = 0
        cnt = 0

        time.sleep(60)
        logger.info("Start...")
        companies = conn.query("select * from company order by id desc limit %s,100", cnt)
        #exit()

    for company in companies:
        cnt += 1
        if company["active"] == 'N':
            continue

        if company["id"] % total_part == current_part - 1:
            if company['name'] is None or company["name"].strip() == "":
                continue
            logger.info(company['name'])
            total += 1
            url = 'http://toutiao.com/search_content/?offset=0&format=json&keyword=' + company['name'] + '&autoload=true&count=20'
            logger.info(url)
            request(url, lambda r,company=company:handle_result(r, company))

    conn.close()


if __name__ == "__main__":
    #toutiao_news.py 4 1
    logger.info("Start...")

    total_part  = 1
    current_part = 1
    if len(sys.argv) > 2:
        total_part = int(sys.argv[1])
        current_part = int(sys.argv[2])
    logger.info("total_part=%s, current_part=%s", total_part, current_part)
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=20)
    begin()
    tornado.ioloop.IOLoop.instance().start()