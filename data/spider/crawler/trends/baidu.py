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
loghelper.init_logger("baidu_trends", stream=True)
logger = loghelper.get_logger("baidu_trends")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
market_collection = mongo.crawler_v2.market_baidu

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
                logger.info("companyId=%s, artifactId=%s,  Not Exist!!!"
                            % (app["companyId"],app["artifactId"]))

                key = int(response.request.url.replace("http://shouji.baidu.com/soft/item?docid=",""))
                market_collection.delete_one({"key":key})

                conn = db.connect_torndb()
                conn.execute("delete from artifact_market where artifactId=%s and type=%s",app["artifactId"], TYPE)
                conn.close()
            else:
                d = pq(html)
                downloadstr = d("span.download-num").text().replace("下载次数: ","").replace("+","")
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

                save_download(app["companyId"],app["artifactId"],download,score)
                logger.info("companyId=%s, artifactId=%s, download=%s, score=%s, groupid=%s"
                            % (app["companyId"],app["artifactId"],download,score,groupid))

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
                        save_download(app["companyId"],app["artifactId"],download,score)
                        logger.info("companyId=%s, artifactId=%s, download=%s, score=%s"
                                    % (app["companyId"],app["artifactId"],download,score))
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
                logger.info("companyId=%s, artifactId=%s, comment=%s"
                                    % (app["companyId"],app["artifactId"],comment))
                save_comment(app["companyId"],app["artifactId"],comment)
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
            logger.info("companyId=%s, artifactId=%s, comment=%s"
                                    % (app["companyId"],app["artifactId"],comment))
            save_comment(app["companyId"],app["artifactId"],comment)
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
        total += 1
        http_client.fetch(app["link"], lambda r,app=app:handle_app_result(r, app),request_timeout=10)

    conn.close()


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()