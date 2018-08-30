# -*- coding: utf-8 -*-
import sys, os, random
import tornado.ioloop
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
from pymongo import MongoClient
import pymongo
import datetime, time
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
import market.wandoujia as wandoujia_parser

#logger
loghelper.init_logger("wandoujia_trends", stream=True)
logger = loghelper.get_logger("wandoujia_trends")

#mongo
mongo = db.connect_mongo()
collection = mongo.trend.android

collection_market = mongo.market.android_market

cnt = 0
total = 0
TYPE = 16030

PS = []


headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"}

def get_ps():
    rule = {'type': 'HTTP', 'anonymous': 'high'}
    proxy_ips = proxy_pool.get_single_proxy_x(rule, 7000)
    # PS = proxy_ips
    del PS[:]
    for pi in proxy_ips:
        PS.append(pi)
    # logger.info(len(PS))
    # return len(PS)

def request(url,callback):
    # proxy = {'type': 'https', 'anonymity':'high', 'ping':1, 'transferTime':5}
    # proxy = {'type': 'http', 'anonymity':'high'}
    # proxy_ip = None
    # while proxy_ip is None:
    #     proxy_ip = proxy_pool.get_single_proxy(proxy)
    #     if proxy_ip is None:
    #         time.sleep(60)
    rint = random.randint(0, len(PS) - 1)
    proxy_ip = PS[rint]

    http_client.fetch(url, callback, headers=headers, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),request_timeout=10)

def handle_app_result(response, app, url, apkname):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        if response.code == 302 or response.code==301 or response.code==500 or response.code==404:
            pass
        else:
            # http_client.fetch(response.request.url, lambda r,app=app,url=url,apkname=apkname:handle_app_result(r, app, url, apkname),request_timeout=10)
            request(response.request.url, lambda r, app=app, url=url, apkname=apkname: handle_app_result(r, app, url, apkname))
            return
    else:
        logger.info(response.request.url)
        try:
            # Parser data for newupdates:
            # logger.info(html)
            wandoujia_parser.process(None, url, apkname, response.body)

            html = unicode(response.body,encoding="utf-8",errors='replace')
            d = pq(html)
            download = None
            try:
                dnum = d("i[itemprop='interactionCount']").attr("content").split(":")[1]

                try:
                    download = int(dnum)
                except:
                    if dnum.find("万") >= 0:
                        download = int(float(dnum.replace("万","").strip())* 10000)
                    elif dnum.find("亿") >= 0:
                        download = int(float(dnum.replace("亿","").strip())* 10000 * 10000)
                    else:
                        logger.info("********download :%s cannot get", dnum)

                # score = int(d("meta[itemprop='ratingValue']").attr("content"))
                score = None
                comment = int(d("a.comment-open> i").text())
            except: score = None; comment = None

            if download is not None:
                crawler_util.save_download_comment(app["domain"],TYPE, download,score,comment)
                logger.info("apkname=%s, download=%s, score=%s, comment=%s"
                            % (app["domain"],download,score,comment))

        except:
            logger.info("wrong: %s", response.request.url)
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
        apps = conn.query("select * from artifact where type=4050 and (active is null or active='Y') and id>%s order by id limit 1000", cnt)
        conn.close()

        get_ps()
        if len(PS) >= 2000:
            logger.info("here %s proxies", len(PS))
        else:
            logger.info("here wrong %s proxies", len(PS))
            continue

        if len(apps) <= 0:
            while True:
                if total <= 0:
                    logger.info("Finish.")
                    #time.sleep(60*60*6)  # 6hours
                    exit()
                yield gen.Task(instance.add_timeout, time.time() + 10)

        for app in apps:
            logger.info("%s - %s", app["domain"],app["name"])
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
                logger.info("%s not Found!", domain)
                continue
            t = collection.find_one(({"appmarket":TYPE, "apkname": domain, "date": today}))
            if t is not None:
                logger.info("%s has data!", domain)
                continue
            logger.info(m["link"])
            total += 1
            # http_client.fetch(m["link"], lambda r,app=app,url=m["link"],apkname=domain:handle_app_result(r, app, url, apkname),request_timeout=10)
            request(m["link"],lambda r, app=app, url=m["link"], apkname=domain: handle_app_result(r, app, url, apkname))
            flag = True


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=20)
    instance=tornado.ioloop.IOLoop.instance()
    begin()
    instance.start()