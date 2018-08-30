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
loghelper.init_logger("myapp_trends", stream=True)
logger = loghelper.get_logger("myapp_trends")

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


def handle_app_result(response, app):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        if response.code == 302 or response.code==301 or response.code==500 or response.code==0:
            pass
        else:
            http_client.fetch(response.request.url, lambda r,app=app:handle_app_result(r, app),request_timeout=10)
            return
    else:
        logger.info(response.request.url)
        try:
            #html = unicode(response.body,encoding="utf-8",errors='replace')
            html = response.body
            (download, ) = util.re_get_result('downTimes:"(.*?)"',html)
            (score, ) = util.re_get_result('<div class="com-blue-star-num">(.*?)分</div>', html)
            score = float(score)
            save_download(app["companyId"],app["artifactId"],download,score)
            logger.info("download=%s, score=%s" % (download,score))
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
            data = json.loads(response.body)
            comment = data["obj"]["total"]
            save_comment(app["companyId"],app["artifactId"],comment)
            logger.info("comment=%s" % (comment))
        except:
            traceback.print_exc()

    total -= 1

    if total <=0:
        begin()
        #exit(0)

def save_download(company_id, artifact_id, download, score):
    t = datetime.date.today()
    conn = db.connect_torndb_crawler()
    table_id = aggregator_util.get_android_table_id(conn, company_id)
    a = conn.get("select * from android" + table_id + " where date=%s and artifactId=%s and type=%s",
                 t,artifact_id,TYPE
                 )
    if a is None:
        conn.insert("insert android" + table_id + "(companyId,artifactId,download,score,date,type) values(%s,%s,%s,%s,%s,%s)",
                    company_id, artifact_id, download, score,t,TYPE
                    )
    else:
        conn.update("update android" + table_id + " set download=%s, score=%s where id =%s",
                    download,score,a["id"]
                    )
    conn.close()


def save_comment(company_id, artifact_id, comment):
    t = datetime.date.today()
    conn = db.connect_torndb_crawler()
    table_id = aggregator_util.get_android_table_id(conn, company_id)
    a = conn.get("select * from android" + table_id + " where date=%s and artifactId=%s and type=%s",
                 t,artifact_id,TYPE
                 )
    if a is None:
        conn.insert("insert android" + table_id + "(companyId,artifactId,comment,date,type) values(%s,%s,%s,%s,%s)",
                    company_id, artifact_id, comment,t,TYPE
                    )
    else:
        conn.update("update android" + table_id + " set comment=%s where id =%s",
                    comment,a["id"]
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
        #url = "http://android.myapp.com/myapp/searchAjax.htm?kw=%s" % urllib.quote(app["name"].encode("utf-8"))
        #http_client.fetch(url, lambda r,app=app:handle_search_result(r, app),request_timeout=10)
        total += 1
        http_client.fetch(app["link"], lambda r,app=app:handle_app_result(r, app),request_timeout=10)
        total += 1
        url = "http://android.myapp.com/myapp/app/comment.htm?apkName=%s" % app["domain"]
        http_client.fetch(url, lambda r,app=app:handle_comment_result(r, app),request_timeout=10)
    conn.close()


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()