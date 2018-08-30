# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
from pymongo import MongoClient
import pymongo
import datetime, time


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import config
import util
import proxy_pool

#logger
loghelper.init_logger("myapp_crawler", stream=True)
logger = loghelper.get_logger("myapp_crawler")

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
    logger.info(response.request.url)
    (package,) = util.re_get_result(r"http://android\.myapp\.com/myapp/detail\.htm\?apkName=(.*)",response.request.url)

    if response.error:
        if response.code == 302 or response.code==301 or response.code==500 or response.code==0:
            logger.info("%s not found!" % package)
            market_collection.update_one({"package":package},{'$set':{'myapp':None,'myapp_parsed':True}})
        else:
            logger.info("Error: %s, %s" % (response.error,response.request.url))
            request(response.request.url, handle_response)
            return
    else:
        #logger.info("%s found!" % package)
        #logger.info(response.body)
        #util.html_encode(response.body)
        if response.body.find("没有找到相关结果") > 0:
            market_collection.update_one({"package":package},{'$set':{'myapp':None,'myapp_parsed':True}})
        else:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            d = pq(html)
            name = d('div.det-name-int').text()
            logger.info(name)

            icon = d('div.det-icon> img').attr("src")

            screenshots = []
            imgs = d('span.pic-turn-img-box> div> img')
            #logger.info(imgs)
            for img in imgs:
                url = pq(img).attr("data-src")
                screenshots.append(url)

            desc = d('div.det-app-data-info').eq(0).text()

            update_desc = d(':contains("更新内容")').next().text()

            file_size = d('div.det-size').text()

            tags = []
            tag = d('a#J_DetCate').text()
            tags.append(tag)

            #datestr = d('div#J_ApkPublishTime').attr("data-apkPublishTime")
            (datestr, ) = util.re_get_result('data-apkPublishTime=\"(.*?)\"', html)
            #logger.info("datastr=%s" % datestr)
            update_date = datetime.datetime.fromtimestamp(int(datestr))
            versionname = d(':contains("版本")').next().text()
            if versionname.startswith("V"):
                versionname = versionname.replace("V","")
            author = d(':contains("开发商")').next().text()

            data = {"name": name,
                    "icon": icon,
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
            market_collection.update_one({"package":package},{'$set':{'myapp':data,'myapp_parsed':True}})
            #exit(0)

    total -= 1
    if total <=0:
        begin()


stop = 0
def begin():
    global total
    global stop
    apps = market_collection.find({"myapp_parsed":{"$ne":True}}).limit(1000)
    if apps.count() < 500:
        stop += 1
        if stop >= 2:
            logger.info("Finish.")
            exit(0)

    for app in apps:
        logger.info(app["package"])
        total += 1
        api_url = "http://android.myapp.com/myapp/detail.htm?apkName=%s" % app["package"].strip()
        request(api_url, handle_response)


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()