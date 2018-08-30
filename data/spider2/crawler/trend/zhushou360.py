# -*- coding: utf-8 -*-
import sys, os, random
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
import market.zhushou360 as zhushou360_parser

#logger
loghelper.init_logger("360_trends", stream=True)
logger = loghelper.get_logger("360_trends")

#mongo
mongo = db.connect_mongo()
collection = mongo.trend.android


collection_market = mongo.market.android_market #TODO

cnt = 0
total = 0
TYPE = 16010

PS = []


headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"}

def get_ps():
    rule = {'type': 'HTTP', 'anonymous': 'high'}
    proxy_ips = proxy_pool.get_single_proxy_x(rule, 5000)
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

def handle_app_result(response, app, url, key):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        request(response.request.url, lambda r,app=app, url=url, key=key:handle_app_result(r, app, url, key))
        return
    else:
        logger.info(response.request.url)
        try:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            #logger.info(html)
            if html.find("获取应用内容失败") >= 0:
                pass
            else:
                # Parser data for newupdates:
                # logger.info(html)
                zhushou360_parser.process(url, key, response.body)

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
                    logger.info(url)
                    logger.info("str: %s", downloadstr)
                    traceback.print_exc()

                r = "var detail = \(function \(\) \{\s*?return\s*?(.*?);\s*?\}\)"
                result = util.re_get_result(r,html)

                if result is not None:
                    (b,) = result
                    base = json.loads(b.replace("'",'"'),strict=False)
                    baike_name = base["baike_name"].strip()
                    crawler_util.save_download(app["domain"],TYPE,download,score)
                    logger.info("apkname=%s, download=%s, score=%s, baike_name=%s"
                                % (app["domain"],download,score,baike_name))

                    # 无法获得准确数量
                    # url = "http://zhushou.360.cn/search/index/?kw=%s" % urllib.quote(app["name"].encode("utf-8"))
                    # total += 1
                    # request(url, lambda r,app=app:handle_search_result(r, app))

                    # Correct url: "http://comment.mobilem.360.cn/comment/getComments?baike=360%E6%89%8B%E6%9C%BA%E5%8D%AB%E5%A3%AB&c=message&a=getmessage&start=0&count=10"
                    # url = "http://intf.baike.360.cn/index.php?name=%s&c=message&a=getmessagenum" % urllib.quote(baike_name.encode("utf-8"))
                    # total += 1
                    # request(url, lambda r,app=app:handle_comment_result(r, app))
                else:
                    logger.info("can't find baike name. %s", response.request.url)
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
        #http_client.fetch(response.request.url, lambda r,app=app:handle_comment_result(r, app),request_timeout=10)
        request(response.request.url, lambda r,app=app:handle_comment_result(r, app))
        return
    else:
        logger.info(response.request.url)
        try:
            data = json.loads(response.body)
            comment = data["mesg"]
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
        conn = db.connect_torndb_proxy()
        apps = conn.query("select * from artifact where type=4050 and id>%s order by id limit 500", cnt)
        # apps = conn.query("select * from artifact where type=4050 and id=181666", cnt)
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
                #continue

            total += 1
            app["link"] = m["link"]
            request(m["link"], lambda r,app=app,url=m["link"],key=m["key_int"]:handle_app_result(r, app,url,key))

            flag = True


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=15)
    instance=tornado.ioloop.IOLoop.instance()
    begin()
    instance.start()