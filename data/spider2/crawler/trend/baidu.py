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

#logger
loghelper.init_logger("baidu_trends", stream=True)
logger = loghelper.get_logger("baidu_trends")

#mongo
mongo = db.connect_mongo()
collection = mongo.trend.android

collection_market = mongo.market.android_market

cnt = 0
total = 0
TYPE = 16020

def handle_app_result(response, app):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        http_client.fetch(response.request.url, lambda r,app=app:handle_app_result(r, app),request_timeout=10)
        return
    else:
        logger.info(response.request.url)
        try:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            #logger.info(html)
            if html.find("请检查您所输入的URL地址是否有误") >= 0:
                logger.info("pkgname=%s,  Not Exist!!!"
                            % (app["domain"]))
            else:
                d = pq(html)
                downloadstr = d("span.download-num").eq(0).text().replace("下载次数: ","").replace("+","")
                if downloadstr.endswith("千"):
                    download = float(downloadstr.replace("千","")) * 1000
                elif downloadstr.endswith("万"):
                    download = float(downloadstr.replace("万","")) * 10000
                elif downloadstr.endswith("亿"):
                    download = float(downloadstr.replace("亿","")) * 10000 * 10000
                else:
                    download = int(downloadstr)
                score = int(d("span.star-percent").attr("style").replace("width:","").replace("%",""))*0.05
                groupid = d("input[name='groupid']").attr("value")

                crawler_util.save_download(app["domain"],TYPE,download,score)
                logger.info("pkgname=%s, download=%s, score=%s, groupid=%s"
                            % (app["domain"],download,score,groupid))

                url = "http://m.baidu.com/mosug?wd=%s&type=soft" % urllib.quote(app["name"].encode("utf-8"))
                total += 1
                http_client.fetch(url, lambda r,app=app:handle_mosug_result(r, app),request_timeout=10)

                url = "http://shouji.baidu.com/comment?action_type=getCommentList&groupid=%s" % groupid
                total += 1
                app["groupid"] = groupid
                http_client.fetch(url, lambda r,app=app:handle_comment_result(r, app),request_timeout=10)
        except:
            traceback.print_exc()

    total -= 1

    if total <=0:
        begin()
        #exit(0)


def handle_mosug_result(response, app):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        http_client.fetch(response.request.url, lambda r,app=app:handle_mosug_result(r, app),request_timeout=10)
        return
    else:
        logger.info(response.request.url)
        try:
            data = json.loads(response.body)
            if data["result"].get("s") is not None:
                for dt in data["result"].get("s"):
                    if dt.get("package") is None:
                        continue
                    if dt["package"].strip() == app["domain"].strip():
                        download = int(dt["download_num"])
                        score = int(dt["score"]) * 0.05
                        crawler_util.save_download(app["domain"],TYPE,download,score)
                        logger.info("apkname=%s, download=%s, score=%s"
                                    % (app["domain"],download,score))
                        break
        except:
            traceback.print_exc()

    total -= 1

    if total <=0:
        begin()
        #exit(0)


def handle_comment_result(response, app):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        http_client.fetch(response.request.url, lambda r,app=app:handle_comment_result(r, app),request_timeout=10)
        return
    else:
        logger.info(response.request.url)
        try:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            #logger.info(html)
            d = pq(html)
            totalpage = int(d("input[name='totalpage']").attr("value"))
            comment = None
            if totalpage == 0:
                comment = 0
            elif totalpage == 1:
                comment = len(d("li.comment"))
            else:
                url = "http://shouji.baidu.com/comment?action_type=getCommentList&groupid=%s&pn=%s" % (app["groupid"],totalpage)
                total += 1
                http_client.fetch(url, lambda r,app=app:handle_lastpage_comment_result(r, app),request_timeout=10)

            if comment is not None:
                logger.info("apkname=%s, comment=%s"
                                    % (app["domain"],comment))
                crawler_util.save_comment(app["domain"],TYPE,comment)
        except:
            traceback.print_exc()

    total -= 1

    if total <=0:
        begin()
        #exit(0)


def handle_lastpage_comment_result(response, app):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        http_client.fetch(response.request.url, lambda r,app=app:handle_lastpage_comment_result(r, app),request_timeout=10)
        return
    else:
        logger.info(response.request.url)
        try:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            #logger.info(html)
            d = pq(html)
            totalpage = int(d("input[name='totalpage']").attr("value"))
            comment = len(d("li.comment")) + 10 * totalpage
            logger.info("apkname=%s, comment=%s"
                                    % (app["domain"],comment))
            crawler_util.save_comment(app["domain"],TYPE,comment)
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
                continue

            total += 1
            http_client.fetch(m["link"], lambda r,app=app:handle_app_result(r, app),request_timeout=10)
            flag = True


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=20)
    instance=tornado.ioloop.IOLoop.instance()
    begin()
    instance.start()