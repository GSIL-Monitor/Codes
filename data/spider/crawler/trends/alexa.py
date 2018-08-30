# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
from pymongo import MongoClient
from kafka import KafkaClient, KafkaConsumer, SimpleProducer
import datetime, time
import json
import urllib
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import config
import util
import proxy_pool
import db
import aggregator_util

# logger
loghelper.init_logger("alexa_trends", stream=True)
logger = loghelper.get_logger("alexa_trends")

# mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
alexa_collection = mongo.crawler_v2.trends_alexa


#kafka
(url) = config.get_kafka_config()
kafka = KafkaClient(url)
kafka_producer = SimpleProducer(kafka)

cnt = 0
total = 0


def get_proxy():
    proxy = {'type': 'http', 'anonymity': 'high', 'ping': 1, 'transferTime': 1, 'country': 'cn'}
    # proxy = {'type': 'http', 'anonymity':'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)
    return proxy_ip


def request(url, callback, body=None, proxy_ip=None):
    if proxy_ip is None:
        proxy_ip = get_proxy()

    if body is None:
        http_client.fetch(url, callback, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),
                          request_timeout=30)
    else:
        http_client.fetch(url, callback, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),
                          request_timeout=30,
                          method='POST', body=body)


def handle_alexa_com_result(response, app):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error, response.request.url))
        request(response.request.url, lambda r, app=app: handle_alexa_com_result(r, app))
        return
    else:
        try:
            html = unicode(response.body, encoding="utf-8", errors='replace')
            d = pq(html)
            datas = d('strong.metrics-data')
            data_len = len(datas)

            global_rank = None
            country_rank = None
            bounce_rate = None
            daily_pageviews_per_visitor = None
            daily_time_on_site = None
            search_visits = None

            if data_len == 6:
                global_rank = pq(datas[0]).text()
                country_rank = pq(datas[1]).text()
                bounce_rate = pq(datas[2]).text()
                daily_pageviews_per_visitor = pq(datas[3]).text()
                daily_time_on_site = pq(datas[4]).text()
                search_visits = pq(datas[5]).text()
            elif data_len == 5:
                global_rank = pq(datas[0]).text()
                country_rank = ''
                bounce_rate = pq(datas[1]).text()
                daily_pageviews_per_visitor = pq(datas[2]).text()
                daily_time_on_site = pq(datas[3]).text()
                search_visits = pq(datas[4]).text()

            global_rank_value = None
            try:
                global_rank_value = int(global_rank.replace(",", ""))
            except:
                pass
            country_rank_value = None
            try:
                country_rank_value = int(country_rank.replace(",", ""))
            except:
                pass
            search_visits_value = None
            try:
                search_visits_value = float(search_visits.replace("%", "")) / 100
            except:
                pass

            dt = datetime.date.today()
            today = datetime.datetime(dt.year, dt.month, dt.day)

            result = {
                'date': today,
                'domain': app["domain"],
                'global_rank': global_rank,
                'country_rank': country_rank,
                'search_visits': search_visits,
                'global_rank_value': global_rank_value,
                'country_rank_value': country_rank_value,
                'search_visits_value': search_visits_value,
                'parser': 'wait'
                # 'page_view': page_view
            }
            logger.info(result)

            r = alexa_collection.find_one({"domain": app["domain"], "date": today})
            if r is None:
                alexa_collection.insert_one(result)
            else:
                alexa_collection.update_one({"_id": r["_id"]}, {'$set': result})

        except:
            traceback.print_exc()

    total -= 1
    if total <= 0:
        begin()
        # exit(0)


def handle_alexa_cn_result(response, app):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error, response.request.url))
        request(response.request.url, lambda r, app=app: handle_alexa_cn_result(r, app))
        return
    else:
        try:
            html = unicode(response.body, encoding="utf-8", errors='replace')
            d = pq(html)
            data = d('script').text()
            data = ''.join(data)
            try:
                (ids,) = util.re_get_result("showHint\('(\S*)'\);", data)
            except:
                # logger.info(html)
                request(response.request.url, lambda r, app=app: handle_alexa_cn_result(r, app))
                return

            id_arr = ids.split(',')

            data = {"url": id_arr[0],
                    "sig": id_arr[1],
                    "keyt": id_arr[2]
                    }
            body = urllib.urlencode(data)
            url = "http://www.alexa.cn/api_150710.php"
            total += 1
            # proxy_ip = get_proxy()
            proxy_ip = None
            request(url, lambda r, app=app, body=body, proxy_ip=proxy_ip: handle_api_result(r, app, body, proxy_ip),
                    body, proxy_ip)
        except:
            traceback.print_exc()

    total -= 1
    if total <= 0:
        begin()
        # exit(0)


def handle_api_result(response, app, body, proxy_ip):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error, response.request.url))
        request(response.request.url,
                lambda r, app=app, body=body, proxy_ip=proxy_ip: handle_api_result(r, app, body, proxy_ip), body,
                proxy_ip)
        return
    else:
        try:
            dt = datetime.date.today()
            today = datetime.datetime(dt.year, dt.month, dt.day)
            domain = app["domain"]

            pv = response.body
            info = pv.split('*')

            page_view = []
            for i in xrange(0, len(info)):
                if i > 7 and i < 16:
                    page_view.append(info[i])

            result = {
                'date': today,
                'domain': domain,
                "page_view": page_view,
                'parser': 'wait'
            }
            logger.info(result)

            r = alexa_collection.find_one({"domain": domain, "date": today})
            if r is None:
                alexa_collection.insert_one(result)
            else:
                alexa_collection.update_one({"_id": r["_id"]}, {'$set': result})

        except:
            traceback.print_exc()

    total -= 1
    if total <= 0:
        begin()
        # exit(0)


def begin():
    global total, cnt
    conn = db.connect_torndb()

    apps = conn.query("select * from artifact where type=4010 and domain is not null order by id limit %s,1000", cnt)
    if len(apps) <= 0:
        logger.info("Finish.")
        msg = {"type":"alexa_trends"}
        logger.info(json.dumps(msg))
        kafka_producer.send_messages("alexa_trends", json.dumps(msg))
        exit()

    for app in apps:
        logger.info(app["name"])
        if app["domain"].strip() == "":
            continue

        cnt += 1

        total += 1
        url = "http://www.alexa.com/siteinfo/%s" % app["domain"]
        request(url, lambda r, app=app: handle_alexa_com_result(r, app))

        total += 1
        url = "http://www.alexa.cn/index.php?url=%s" % app["domain"]
        request(url, lambda r, app=app: handle_alexa_cn_result(r, app))

    conn.close()


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=50)
    begin()
    tornado.ioloop.IOLoop.instance().start()
