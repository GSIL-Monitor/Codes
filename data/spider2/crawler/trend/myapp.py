# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
from pymongo import MongoClient
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
import market.myapp as myapp_parser


#logger
loghelper.init_logger("myapp_trends", stream=True)
logger = loghelper.get_logger("myapp_trends")

#mongo
mongo = db.connect_mongo()
collection = mongo.trend.android

collection_market = mongo.market.android_market #TODO

cnt = 0
total = 0
TYPE = 16040
# def handle_search_result(response, app):
#     global total
#     global notfound
#
#     if response.error:
#         logger.info("Error: %s, %s" % (response.error,response.request.url))
#         http_client.fetch(response.request.url, lambda r,app=app:handle_search_result(r, app),request_timeout=10)
#         return
#     else:
#         flag = False
#         try:
#             logger.info("%s %s" % (app["name"],app["domain"]))
#             data = json.loads(response.body)
#             for p in data["obj"]["appDetails"]:
#                 if p["pkgName"].strip() == app["domain"].strip():
#                     download = p["appDownCount"]
#                     score = p["averageRating"]
#                     score_count = p["appRatingInfo"]["ratingCount"]
#                     logger.info("download=%s" % download)
#                     flag = True
#                     break
#             if flag == False:
#                 logger.info("Not Found!")
#                 notfound += 1
#         except:
#             traceback.print_exc()
#
#         total -= 1
#
#         if flag == False:
#             http_client.fetch(app["link"], lambda r,app=app:handle_app_result(r, app),request_timeout=10)
#             total += 1
#
#         if total <=0:
#             #begin()
#             exit(0)


def handle_app_result(response, app, url, apkname, retry=0):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        if response.code == 302 or response.code==301 or response.code==500 or response.code==0 or response.code==403:
            logger.info("herereere")
            pass
        else:
            retry += 1
            if response.code == 403:
                if retry<20:
                    http_client.fetch(response.request.url, lambda r, app=app, url=url, apkname=apkname, retry=retry: handle_app_result(r, app, url, apkname,retry),request_timeout=10)
                    return
                else:
                    pass
            else:
                http_client.fetch(response.request.url, lambda r,app=app,url=url,apkname=apkname, retry=retry:handle_app_result(r, app, url, apkname, retry),request_timeout=10)
                return
    else:
        logger.info(response.request.url)
        try:
            # Parser data for newupdates:
            #logger.info("%s->%s", apkname, url)
            myapp_parser.process(None, url, apkname, response.body)

            #html = unicode(response.body,encoding="utf-8",errors='replace')
            html = response.body
            (download, ) = util.re_get_result('downTimes:"(.*?)"',html)
            (score, ) = util.re_get_result('<div class="com-blue-star-num">(.*?)分</div>', html)
            score = float(score)
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
            http_client.fetch(response.request.url, lambda r,app=app:handle_comment_result(r, app),request_timeout=10)
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
        conn = db.connect_torndb_proxy()
        apps = conn.query("select * from artifact where type=4050 and id>%s order by id limit 1000", cnt)
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
            logger.info(app["name"])
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
                #pass
                continue

            #url = "http://android.myapp.com/myapp/searchAjax.htm?kw=%s" % urllib.quote(app["name"].encode("utf-8"))
            #http_client.fetch(url, lambda r,app=app:handle_search_result(r, app),request_timeout=10)
            total += 1
            http_client.fetch(m["link"], lambda r,app=app,url=m["link"],apkname=domain:handle_app_result(r, app, url, apkname),request_timeout=10)
            total += 1
            url = "http://android.myapp.com/myapp/app/comment.htm?apkName=%s" % app["domain"]
            http_client.fetch(url, lambda r,app=app:handle_comment_result(r, app),request_timeout=10)

            flag = True


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=20)
    instance=tornado.ioloop.IOLoop.instance()
    begin()
    instance.start()