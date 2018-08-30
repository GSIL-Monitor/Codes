# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
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
loghelper.init_logger("wandoujia_trends", stream=True)
logger = loghelper.get_logger("wandoujia_trends")

cnt = 0
total = 0
TYPE = 16030

def handle_app_result(response, app):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        if response.code == 302 or response.code==301 or response.code==500 or response.code==404:
            pass
        else:
            http_client.fetch(response.request.url, lambda r,app=app:handle_app_result(r, app),request_timeout=10)
            return
    else:
        logger.info(response.request.url)
        try:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            d = pq(html)
            download = int(d("i[itemprop='interactionCount']").attr("content").split(":")[1])
            score = int(d("meta[itemprop='ratingValue']").attr("content"))
            comment = int(d("a.comment-open> i").text())
            save(app["companyId"],app["artifactId"],download,score,comment)
            logger.info("companyId=%s, artifactId=%s, download=%s, score=%s, comment=%s"
                        % (app["companyId"],app["artifactId"],download,score,comment))
        except:
            traceback.print_exc()

    total -= 1

    if total <=0:
        begin()
        #exit(0)


def save(company_id, artifact_id, download, score, comment):
    t = datetime.date.today()
    conn = db.connect_torndb_crawler()
    table_id = aggregator_util.get_android_table_id(conn, company_id)
    a = conn.get("select * from android" + table_id + " where date=%s and artifactId=%s and type=%s",
                 t,artifact_id,TYPE
                 )
    if a is None:
        conn.insert("insert android" + table_id + "(companyId,artifactId,download,score,comment,date,type) \
                                        values(%s,%s,%s,%s,%s,%s,%s)",
                    company_id, artifact_id, download, score, comment, t, TYPE
                    )
    else:
        conn.update("update android" + table_id + " set download=%s, score=%s, comment=%s where id =%s",
                    download,score,comment,a["id"]
                    )
    conn.close()

def begin():
    global total, cnt
    conn = db.connect_torndb()

    apps = conn.query("select a.companyId,m.* from artifact_market m join artifact a on a.id=m.artifactId where m.type=%s order by id limit %s,1000", TYPE, cnt)
    if len(apps) <= 0:
        logger.info("Finish.")
        exit()

    for app in apps:
        logger.info(app["name"])
        cnt += 1
        total += 1
        http_client.fetch(app["link"], lambda r,app=app:handle_app_result(r, app),request_timeout=10)

    conn.close()


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()