# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
from pymongo import MongoClient
import pymongo
import datetime, time
import re

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import config
import util
import proxy_pool

#logger
loghelper.init_logger("itunes_crawler", stream=True)
logger = loghelper.get_logger("itunes_crawler")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)

itunes_collection = mongo.crawler_v2.market_itunes
itunes_collection.create_index([("appId", pymongo.DESCENDING)], unique=True)

cates1 = [
    {"name":"商务",       "url":"https://itunes.apple.com/cn/genre/ios-shang-wu/id6000?mt=8"},
]

cates = [
    {"name":"商务",       "url":"https://itunes.apple.com/cn/genre/ios-shang-wu/id6000?mt=8"},
    {"name":"商品指南",    "url":"https://itunes.apple.com/cn/genre/ios-shang-pin-zhi-nan/id6022?mt=8"},
    {"name":"教育",       "url":"https://itunes.apple.com/cn/genre/ios-jiao-yu/id6017?mt=8"},
    {"name":"娱乐",       "url":"https://itunes.apple.com/cn/genre/ios-yu-le/id6016?mt=8"},
    {"name":"财务",       "url":"https://itunes.apple.com/cn/genre/ios-cai-wu/id6015?mt=8"},
    {"name":"美食佳饮",    "url":"https://itunes.apple.com/cn/genre/ios-mei-shi-jia-yin/id6023?mt=8"},
    {"name":"健康健美",    "url":"https://itunes.apple.com/cn/genre/ios-jian-kang-jian-mei/id6013?mt=8"},
    {"name":"生活",       "url":"https://itunes.apple.com/cn/genre/ios-sheng-huo/id6012?mt=8"},
    {"name":"医疗",       "url":"https://itunes.apple.com/cn/genre/ios-yi-liao/id6020?mt=8"},
    {"name":"音乐",       "url":"https://itunes.apple.com/cn/genre/ios-yin-le/id6011?mt=8"},
    {"name":"导航",       "url":"https://itunes.apple.com/cn/genre/ios-dao-hang/id6010?mt=8"},
    {"name":"新闻",       "url":"https://itunes.apple.com/cn/genre/ios-xin-wen/id6009?mt=8"},
    {"name":"摄影与录像",  "url":"https://itunes.apple.com/cn/genre/ios-she-ying-yu-lu-xiang/id6008?mt=8"},
    {"name":"效率",       "url":"https://itunes.apple.com/cn/genre/ios-xiao-lu/id6007?mt=8"},
    {"name":"参考",       "url":"https://itunes.apple.com/cn/genre/ios-can-kao/id6006?mt=8"},
    {"name":"购物",       "url":"https://itunes.apple.com/cn/genre/ios-gou-wu/id6024?mt=8"},
    {"name":"社交",       "url":"https://itunes.apple.com/cn/genre/ios-she-jiao/id6005?mt=8"},
    {"name":"体育",       "url":"https://itunes.apple.com/cn/genre/ios-ti-yu/id6004?mt=8"},
    {"name":"旅游",       "url":"https://itunes.apple.com/cn/genre/ios-lu-you/id6003?mt=8"},
    {"name":"工具",       "url":"https://itunes.apple.com/cn/genre/ios-gong-ju/id6002?mt=8"},
    {"name":"天气",       "url":"https://itunes.apple.com/cn/genre/ios-tian-qi/id6001?mt=8"}
]

letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T",
           "U","V","W","X","Y","Z","*"]
hzs = []
total = 0

def request(url,callback):
    # proxy = {'type': 'https', 'anonymity':'high', 'ping':1, 'transferTime':5}
    proxy = {'type': 'https', 'anonymity':'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)

    http_client.fetch(url, callback, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]))

def startCrawl():
    global total
    for cate in cates:
        logger.info(cate["name"])
        logger.info(cate["url"])
        total += 1
        request(cate["url"], handle_page)

        for letter in letters:
            #break
            url = cate["url"] + "&letter=" + letter + "&page=1#page"
            logger.info(url)
            total += 1
            request(url, handle_page)

            url = cate["url"] + "&letter=" + letter.lower() + "&page=1#page"
            logger.info(url)
            total += 1
            request(url, handle_page)
            #break

        for letter in hzs:
            url = cate["url"] + "&letter=" + letter + "&page=1#page"
            logger.info(url)
            total += 1
            request(url, handle_page)
            #break
        #break


def handle_page(response):
    global total

    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        request(response.request.url, handle_page)
    else:
        #logger.info(response.body)
        d = pq(response.body)
        apps = d('div#selectedcontent> div> ul> li')
        for app in apps:
            name = pq(app).text()
            app_url = pq(app)('a').attr('href')
            (app_id,) = util.re_get_result(r"id(\d*)",app_url)

            logger.info("%s %s %s" % (app_id, name, app_url))
            item = itunes_collection.find_one({"appId":app_id})
            if item is None:
                data = {
                    "appId":app_id,
                    "name":name,
                    "url":app_url,
                    "date":datetime.datetime.now()
                }
                itunes_collection.insert_one(data)

            if re.match(u'[\u4e00-\u9fa5]+',name):
                if item is None or item.has_key("html")==False:
                    total += 1
                    request(app_url, handle_html)

                if item is None or item.has_key("json")==False:
                    total += 1
                    api_url = "https://itunes.apple.com/cn/lookup?id=%s" % app_id
                    request(api_url, handle_json)

        if len(apps) > 10:
            #logger.info(response.request.url)
            result = util.re_get_result(r"page=(\d*)",response.request.url)
            if result != None:
                (strPage,) = result
                #logger.info(strPage)
                nextPage = str(int(strPage) + 1)
                url = response.request.url
                url = url.replace("page="+strPage, "page=" + nextPage)
                logger.info(url)
                total += 1
                request(url, handle_page)

        total -= 1
        if total <=0:
            exit(0)

def handle_html(response):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        request(response.request.url, handle_html)
    else:
        (app_id,) = util.re_get_result(r"id(\d*)",response.request.url)
        itunes_collection.update_one({"appId":app_id},{'$set':{'html':response.body}})

        total -= 1
        if total <=0:
            exit(0)


def handle_json(response):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        request(response.request.url, handle_json)
    else:
        (app_id,) = util.re_get_result(r"id=(\d*)",response.request.url)
        itunes_collection.update_one({"appId":app_id},{'$set':{'json':response.body}})

        total -= 1
        if total <=0:
            exit(0)


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=50)

    flag = ""
    if len(sys.argv) > 1:
        flag = sys.argv[1]

    if flag == "content":
        # db.market_itunes.find({"name":/[一-龥]+/,"html":{$ne:null}},{"html":0,"json":0}).count()
        rexExp = re.compile(r"[一-龥]+")
        apps = itunes_collection.find({"name":rexExp, "$or":[{"html":None},{"json":None}]})
        for app in apps:
            logger.info(app["name"])
            if app.has_key("html")==False:
                total += 1
                request(app["url"], handle_html)

            if app.has_key("json")==False:
                total += 1
                api_url = "https://itunes.apple.com/cn/lookup?id=%s" % app["appId"]
                request(api_url, handle_json)
            #break
    else:
        lines = open('hanzi.txt').readlines( )
        for line in lines:
            line = unicode(line.strip(), "utf-8")
            for hz in line:
                if hz == "":
                    continue
                if hz >= 'A' and hz <= 'Z':
                    continue
                hzs.append(hz)

        startCrawl()

    tornado.ioloop.IOLoop.instance().start()