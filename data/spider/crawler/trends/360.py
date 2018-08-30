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
loghelper.init_logger("360_trends", stream=True)
logger = loghelper.get_logger("360_trends")

cnt = 0
total = 0
TYPE = 16010

def request(url,callback):
    # proxy = {'type': 'https', 'anonymity':'high', 'ping':1, 'transferTime':5}
    proxy = {'type': 'http', 'anonymity':'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)

    http_client.fetch(url, callback, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),request_timeout=10)

def handle_app_result(response, app):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        #http_client.fetch(response.request.url, lambda r,app=app:handle_app_result(r, app),request_timeout=10)
        request(response.request.url, lambda r,app=app:handle_app_result(r, app))
        return
    else:
        logger.info(response.request.url)
        try:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            #logger.info(html)
            d = pq(html)
            downloadstr = d("span.s-3").eq(0).text().replace("下载：","").replace("次","").replace("+","").strip()
            download = 0
            score = 0
            try:
                if downloadstr.endswith("千"):
                    download = float(downloadstr.replace("千","")) * 1000
                elif downloadstr.endswith("万"):
                    download = float(downloadstr.replace("万","")) * 10000
                elif downloadstr.endswith("亿"):
                    download = float(downloadstr.replace("亿","")) * 10000 * 10000
                else:
                    download = int(downloadstr)
                score = float(d("span.s-1").text().replace("分","").strip())*0.5
            except:
                pass

            r = "var detail = \(function \(\) \{\s*?return\s*?(.*?);\s*?\}\)"
            result = util.re_get_result(r,html)

            if result is not None:
                (b,) = result
                base = json.loads(b.replace("'",'"'),strict=False)
                baike_name = base["baike_name"].strip()
                save_download(app["companyId"],app["artifactId"],download,score)
                logger.info("companyId=%s, artifactId=%s, download=%s, score=%s, baike_name=%s"
                            % (app["companyId"],app["artifactId"],download,score,baike_name))

                url = "http://zhushou.360.cn/search/index/?kw=%s" % urllib.quote(app["name"].encode("utf-8"))
                total += 1
                #http_client.fetch(url, lambda r,app=app:handle_search_result(r, app),request_timeout=10)
                request(url, lambda r,app=app:handle_search_result(r, app))

                url = "http://intf.baike.360.cn/index.php?name=%s&c=message&a=getmessagenum" % urllib.quote(baike_name.encode("utf-8"))
                total += 1
                #http_client.fetch(url, lambda r,app=app:handle_comment_result(r, app),request_timeout=10)
                request(url, lambda r,app=app:handle_comment_result(r, app))
            else:
                logger.info(html)
        except:
            traceback.print_exc()


    total -= 1

    if total <=0:
        begin()
        #exit(0)


def handle_search_result(response, app):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        #http_client.fetch(response.request.url, lambda r,app=app:handle_search_result(r, app),request_timeout=10)
        request(response.request.url, lambda r,app=app:handle_search_result(r, app))
        return
    else:
        logger.info(response.request.url)
        try:
            sid = app["link"].replace("http://zhushou.360.cn/detail/index/soft_id/","").strip()
            html = unicode(response.body,encoding="utf-8",errors='replace')
            d = pq(html)

            lis = d('div.SeaCon> ul> li')
            for li in lis:
                l = pq(li)
                _sid = l("div.seaDown> div.download> a").attr("sid").strip()
                if sid == _sid:
                    #logger.info("sid=%s" % _sid)
                    download = int(l("div.seaDown> div.sdlft> p.downNum").text().replace("次下载",""))
                    score = int(l("div.seaDown> div.sdlft> p.stars> span").attr("style").replace("width:","")
                                .replace("%","")) * 0.05
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
        #http_client.fetch(response.request.url, lambda r,app=app:handle_comment_result(r, app),request_timeout=10)
        request(response.request.url, lambda r,app=app:handle_comment_result(r, app))
        return
    else:
        logger.info(response.request.url)
        try:
            data = json.loads(response.body)
            comment = data["mesg"]
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

    apps = conn.query("select a.companyId,m.* from artifact_market m join artifact a on a.id=m.artifactId where m.type=%s order by id desc limit %s,1000", TYPE, cnt)
    if len(apps) <= 0:
        logger.info("Finish.")
        exit()

    for app in apps:
        logger.info(app["name"])
        cnt += 1

        total += 1
        #http_client.fetch(app["link"], lambda r,app=app:handle_app_result(r, app),request_timeout=10)
        request(app["link"], lambda r,app=app:handle_app_result(r, app))
    conn.close()


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()