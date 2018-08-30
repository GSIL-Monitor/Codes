# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
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

#logger
loghelper.init_logger("itunes_trends", stream=True)
logger = loghelper.get_logger("itunes_trends")

#mongo
mongo = db.connect_mongo()
collection = mongo.trend.itunes

collection_itunes = mongo.market.itunes


cnt = 0
total = 0


def request(url,callback):
    # proxy = {'type': 'https', 'anonymity':'high', 'ping':1, 'transferTime':5}
    proxy = {'type': 'http', 'anonymity':'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)

    #logger.info(proxy_ip)
    http_client.fetch(url, callback, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),request_timeout=10)


def handle_lookup_result(response, app):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        request(response.request.url, lambda r,app=app:handle_lookup_result(r, app))
        return
    else:
        try:
            data = json.loads(response.body)
            if data["resultCount"] > 0:
                for result in data["results"]:
                    if result.get("trackId") == int(app["domain"]):
                        score = result.get("averageUserRating")
                        comment = result.get("userRatingCount")
                        logger.info("companyId=%s, artifactId=%s, score=%s, comment=%s"
                                            % (app["companyId"],app["id"],score, comment))

                        if score is not None or comment is not None:
                            save_comment(app["trackId"],score, comment)
                        break
        except:
            traceback.print_exc()

    total -= 1
    if total <=0:
        begin()
        # exit(0)


def save_comment(trackId, score, comment):
    dt = datetime.date.today()
    today = datetime.datetime(dt.year, dt.month, dt.day)
    r = collection.find_one(({"trackId":trackId, "date": today}))

    if r is None:
        result = {
            "trackId": trackId,
            "date":today,
            "comment": comment,
            "score":score
        }
        collection.insert_one(result)
    else:
        result = {
            "comment": comment,
            "score":score
        }
        collection.update_one({"_id": r["_id"]}, {'$set': result})


@gen.engine
def begin():
    global total, cnt

    flag = False
    while flag is False:
        conn = db.connect_torndb()
        apps = conn.query("select * from artifact where type=4040 order by id desc limit %s,100", cnt)
        if len(apps) <= 0:
            while True:
                if total <= 0:
                    logger.info("Finish.")
                    #time.sleep(60*60*6)  # 6hours
                    exit()
                yield gen.Task(instance.add_timeout, time.time() + 10)

        for app in apps:

            cnt += 1

            if app["domain"] is None or app["domain"].strip() == "":
                continue

            trackId = int(app["domain"].strip())
            app["trackId"] = trackId
            dt = datetime.date.today()
            today = datetime.datetime(dt.year, dt.month, dt.day)

            m = collection_itunes.find_one({"trackId": trackId})
            if m is None:
                continue

            r = collection.find_one(({"trackId": trackId, "date": today}))
            if r is not None:
                continue
            logger.info("%s, %s", app["name"], trackId)

            total += 1
            url = "http://itunes.apple.com/cn/lookup?id=%s" % trackId
            request(url, lambda r,app=app:handle_lookup_result(r, app))
            flag = True
        conn.close()


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=20)
    instance=tornado.ioloop.IOLoop.instance()
    begin()
    instance.start()