# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
from pymongo import MongoClient
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

#logger
loghelper.init_logger("itunes_trends", stream=True)
logger = loghelper.get_logger("itunes_trends")

cnt = 0
total = 0
TYPE = 16100


def request(url,callback):
    # proxy = {'type': 'https', 'anonymity':'high', 'ping':1, 'transferTime':5}
    proxy = {'type': 'https', 'anonymity':'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)

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
                            save_comment(app["companyId"],app["id"],score, comment)
                        break
        except:
            traceback.print_exc()

    total -= 1
    if total <=0:
        begin()
        # exit(0)


def save_comment(company_id, artifact_id, score, comment):
    t = datetime.date.today()
    conn = db.connect_torndb_crawler()
    table_id = aggregator_util.get_ios_table_id(conn, company_id)
    a = conn.get("select * from ios" + table_id + " where date=%s and artifactId=%s and type=%s",
                 t,artifact_id,TYPE
                 )
    if a is None:
        conn.insert("insert ios" + table_id + "(companyId,artifactId,score,comment,date,type) values(%s,%s,%s,%s,%s,%s)",
                    company_id, artifact_id, score, comment,t,TYPE
                    )
    else:
        conn.update("update ios" + table_id + " set score=%s, comment=%s where id =%s",
                    score, comment,a["id"]
                    )
    conn.close()


def begin():
    global total, cnt
    conn = db.connect_torndb()

    apps = conn.query("select * from artifact where type=4040 and domain is not null order by id limit %s,1000", cnt)
    if len(apps) <= 0:
        logger.info("Finish.")
        exit()

    for app in apps:
        logger.info(app["name"])
        cnt += 1

        total += 1
        url = "https://itunes.apple.com/cn/lookup?id=%s" % app["domain"]
        request(url, lambda r,app=app:handle_lookup_result(r, app))

    conn.close()


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()