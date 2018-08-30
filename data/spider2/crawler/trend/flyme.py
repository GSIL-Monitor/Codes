# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
from pymongo import MongoClient
from lxml import html
import pymongo
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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import crawler_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import market.flyme as flyme_parser


#logger
loghelper.init_logger("flyme_trends", stream=True)
logger = loghelper.get_logger("flyme_trends")

#mongo
mongo = db.connect_mongo()
collection = mongo.trend.android

collection_market = mongo.market.android_market #TODO

cnt = 0
total = 0
TYPE = 16060

headers = {}
headers[
    "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"


def request(url,callback):
    #proxy = {'type': 'http', 'anonymity':'high', 'ping':1, 'transferTime':5}
    proxy = {'type': 'http', 'anonymity':'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)
    logger.info("crawler: %s",url)

    http_client.fetch(url, callback, headers=headers, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),
                      request_timeout=10, connect_timeout=10)


def has_content(content, apkname):
    # d = pq(html.fromstring(content.decode("utf-8")))
    if content.find(u'很抱歉，您要访问的页面无法正常显示，可能是因为如下原因') >= 0:
        logger.info('404 for %s', apkname)
        return True
    elif content.find(u'魅友评分') >= 0:
        return True
    else:
        return False

def handle_app_result(response, app, url, apkname, retry=0):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        if response.code == 302 or response.code==301 or response.code==500 or response.code==0:
            logger.info("herereere")
            pass
        else:
            retry += 1
            if response.code == 403:
                if retry<10:
                    request(response.request.url, lambda r, app=app, url=url, apkname=apkname, retry=retry: handle_app_result(r, app, url, apkname,retry))
                    return
                else:
                    pass
            else:
                request(response.request.url, lambda r,app=app,url=url,apkname=apkname, retry=retry:handle_app_result(r, app, url, apkname, retry))
                return
    elif has_content(response.body, apkname) is False:
        retry += 1
        logger.info("**********************************")
        logger.info(response.body)
        if retry < 10:
            request(response.request.url, lambda r, app=app,url=url,apkname=apkname,retry=retry:handle_app_result(r, app, url, apkname, retry))
            return
    else:
        logger.info(response.request.url)
        try:
            # Parser data for newupdates:
            #logger.info("%s->%s", apkname, url)
            flyme_parser.process(None, url, apkname, response.body)

            #html = unicode(response.body,encoding="utf-8",errors='replace')
            content = response.body

            d = pq(html.fromstring(content.decode("utf-8")))
            download = d('span:contains("下      载：")+ div').text().strip()
            score = d('span:contains("魅友评分")+ div > div').attr('data-num').strip()

            score = float(score)/10
            download = float(download)
            crawler_util.save_download(app["domain"],TYPE, download,score)
            logger.info("apkname=%s, download=%s, score=%s" % (app["domain"], download,score))

        except:
            traceback.print_exc()

    total -= 1
    logger.info("total: %s", total)

    if total <=0:
        begin()
        #exit(0)


def handle_comment_result(response, app):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        if response.code == 302 or response.code == 301 or response.code == 500 or response.code == 0 or response.code == 403:
            pass
        else:
            request(response.request.url, lambda r,app=app:handle_comment_result(r, app))
            return
    else:
        logger.info(response.request.url)
        try:
            data = json.loads(response.body)
            if data["obj"] is not None:
                comment = data["obj"]["total"]
                #有时obj为None, 刷一下会好. 无法区别.
                crawler_util.save_comment(app["domain"],TYPE, comment)
                logger.info("apkname=%s, comment=%s" % (app["domain"], comment))
        except:
            traceback.print_exc()

    total -= 1

    if total <=0:
        begin()
        #exit(0)

@gen.engine
def begin():
    global total, cnt

    flag = False
    while flag is False:
        conn = db.connect_torndb()
        apps = conn.query("select * from artifact where type=4050 and id>%s order by id limit 1000", cnt)
        # apps = conn.query("select * from artifact where type=4050 and domain ='so.ofo.labofo' and id>%s order by id limit 1", cnt)
        # apps = conn.query("select * from artifact where id>371210 and id<371250")

        conn.close()

        if len(apps) <= 0:
            while True:
                if total <= 0:
                    logger.info("Finish.")
                    #time.sleep(60*60*6)  # 6hours
                    exit()
                yield gen.Task(instance.add_timeout, time.time() + 10)

        for app in apps:
            # logger.info(app["name"])
            if app["id"] > cnt:
                cnt = app["id"]

            if app["domain"] is None or app["domain"].strip() == "":
                continue

            domain = app["domain"].strip()
            app["domain"] = domain
            dt = datetime.date.today()
            today = datetime.datetime(dt.year, dt.month, dt.day)

            m = collection_market.find_one({"appmarket":TYPE, "apkname": domain})
            if m is None:
                continue

            r = collection.find_one(({"appmarket":TYPE, "apkname": domain, "date": today}))
            if r is not None:
                # pass
                continue
            logger.info(app["name"])
            logger.info(m["link"])
            #url = "http://android.flyme.com/flyme/searchAjax.htm?kw=%s" % urllib.quote(app["name"].encode("utf-8"))
            #http_client.fetch(url, lambda r,app=app:handle_search_result(r, app),request_timeout=10)
            total += 1
            request(m["link"], lambda r,app=app,url=m["link"],apkname=domain:handle_app_result(r, app, url, apkname))
            # total += 1
            # url = "http://app.flyme.cn/apps/public/detail?package_name=%s" % app["domain"]
            # http_client.fetch(url, lambda r,app=app:handle_comment_result(r, app),request_timeout=10)

            flag = True


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=10)
    instance=tornado.ioloop.IOLoop.instance()
    begin()
    instance.start()