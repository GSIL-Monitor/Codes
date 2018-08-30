# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
from pymongo import MongoClient
import pymongo
import datetime, time
from lxml import etree
import traceback


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import config
import util
import proxy_pool

#logger
loghelper.init_logger("wandoujia_crawler", stream=True)
logger = loghelper.get_logger("wandoujia_crawler")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)

market_collection = mongo.crawler_v2.market_other

total = 0

def request(url,callback):
    # proxy = {'type': 'http', 'anonymity':'high', 'ping':1, 'transferTime':5}
    #
    # #proxy = {'type': 'http', 'anonymity':'high'}
    # proxy_ip = None
    # while proxy_ip is None:
    #     proxy_ip = proxy_pool.get_single_proxy(proxy)
    #     if proxy_ip is None:
    #         time.sleep(60)
    #
    # http_client.fetch(url, callback, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]), follow_redirects=False)
    http_client.fetch(url, callback, follow_redirects=False)

def handle_response(response):
    global total
    (package,) = util.re_get_result(r"http://www.wandoujia.com/apps/(.*)",response.request.url)

    logger.info(package)
    if response.error:
        if response.code == 302 or response.code==301 or response.code==500 or response.code==404:
            #logger.info("%s not found!" % package)
            market_collection.update_one({"package":package},{'$set':{'wdj':None,'wdj_parsed':True}})
        else:
            logger.info("Error: %s, %s" % (response.error,response.request.url))
            request(response.request.url, handle_response)
            return
    else:
        try:
            #logger.info("%s found!" % package)
            #logger.info(response.body)
            html = unicode(response.body,encoding="utf-8",errors='replace')
            d = pq(html)
            name = d('span.title').text()
            logger.info(name)

            icon = d('div.app-icon> img').attr("src")

            brief = d('p.tagline').text()
            #logger.info(brief)

            editor_comment = d('div.editorComment> div').text()
            #logger.info(editor_comment)

            screenshots = []
            imgs = d('div.overview> img')
            #logger.info(imgs)
            for img in imgs:
                url = pq(img).attr("src")
                screenshots.append(url)

            desc = d('div.desc-info> div').text()
            #logger.info(desc)
            update_desc = d('div.change-info> div').text()
            #logger.info(update_desc)
            file_size = int(d('meta[itemprop="fileSize"]').attr("content"))

            ts = d('dd.tag-box >a')
            tags = []
            for t in ts:
                tag = pq(t).text()
                tags.append(tag)

            datestr = d('time#baidu_time').text()
            update_date = datetime.datetime.strptime(datestr,"%Y年%m月%d日")
            versionname = d(':contains("版本")').next().text()
            author = d('span.dev-sites').text()

            data = {"name": name,
                    "icon": icon,
                    "brief": brief,
                    "editorComment": editor_comment,
                    "screenshots": screenshots,
                    "desc": desc,
                    "updateDesc": update_desc,
                    "fileSize": file_size,
                    "tags":tags,
                    "updateDate": update_date,
                    "versionname": versionname,
                    "author": author,
                    "date":datetime.datetime.now()}

            #logger.info(data)
            market_collection.update_one({"package":package},{'$set':{'wdj':data,'wdj_parsed':True}})
        except KeyboardInterrupt:
            exit(0)
        except Exception,e :
            logger.error(e)
            traceback.print_exc()
            market_collection.update_one({"package":package},{'$set':{'wdj':None,'wdj_parsed':True}})
            #exit(0)
    total -= 1
    if total <=0:
        begin()


def begin():
    global total

    apps = market_collection.find({"wdj_parsed":{"$ne":True}}).limit(1000)
    if apps.count() == 0:
        exit(0)

    for app in apps:
        logger.info(app["package"])
        total += 1
        api_url = "http://www.wandoujia.com/apps/%s" % app["package"].strip()
        request(api_url, handle_response)

if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()