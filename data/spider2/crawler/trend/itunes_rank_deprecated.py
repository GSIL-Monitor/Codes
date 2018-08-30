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


#logger
loghelper.init_logger("appstore_rank", stream=True)
logger = loghelper.get_logger("appstore_rank")

#mongo

mongo = db.connect_mongo()
appstore_rank_collection = mongo.crawler_v2.appstore_rank

total = 0


def request(url,callback):
    #proxy = {'type': 'http', 'anonymity':'high', 'ping':1, 'transferTime':5}
    proxy = {'type': 'http', 'anonymity':'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)
    #logger.info(url)
    http_header = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36'}

    http_client.fetch(url, callback, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),request_timeout=60, headers=http_header)



types = [
    "free",
    #"charge",
    #"grossing"
]

genres = [
    {"name":"商务",       "id":6000,  "url":"https://itunes.apple.com/cn/genre/ios-shang-wu/id6000?mt=8"},
    {"name":"商品指南",    "id":6022,  "url":"https://itunes.apple.com/cn/genre/ios-shang-pin-zhi-nan/id6022?mt=8"},
    {"name":"教育",       "id":6017,  "url":"https://itunes.apple.com/cn/genre/ios-jiao-yu/id6017?mt=8"},
    {"name":"娱乐",       "id":6016,  "url":"https://itunes.apple.com/cn/genre/ios-yu-le/id6016?mt=8"},
    {"name":"财务",       "id":6015,  "url":"https://itunes.apple.com/cn/genre/ios-cai-wu/id6015?mt=8"},
    {"name":"美食佳饮",    "id":6023,   "url":"https://itunes.apple.com/cn/genre/ios-mei-shi-jia-yin/id6023?mt=8"},
    {"name":"健康健美",    "id":6013,   "url":"https://itunes.apple.com/cn/genre/ios-jian-kang-jian-mei/id6013?mt=8"},
    {"name":"生活",       "id":6012,  "url":"https://itunes.apple.com/cn/genre/ios-sheng-huo/id6012?mt=8"},
    {"name":"医疗",       "id":6020,  "url":"https://itunes.apple.com/cn/genre/ios-yi-liao/id6020?mt=8"},
    {"name":"音乐",       "id":6011,  "url":"https://itunes.apple.com/cn/genre/ios-yin-le/id6011?mt=8"},
    {"name":"导航",       "id":6010,  "url":"https://itunes.apple.com/cn/genre/ios-dao-hang/id6010?mt=8"},
    {"name":"新闻",       "id":6009,  "url":"https://itunes.apple.com/cn/genre/ios-xin-wen/id6009?mt=8"},
    {"name":"摄影与录像",  "id":6008,    "url":"https://itunes.apple.com/cn/genre/ios-she-ying-yu-lu-xiang/id6008?mt=8"},
    {"name":"效率",       "id":6007,  "url":"https://itunes.apple.com/cn/genre/ios-xiao-lu/id6007?mt=8"},
    {"name":"参考",       "id":6006,  "url":"https://itunes.apple.com/cn/genre/ios-can-kao/id6006?mt=8"},
    {"name":"购物",       "id":6024,  "url":"https://itunes.apple.com/cn/genre/ios-gou-wu/id6024?mt=8"},
    {"name":"社交",       "id":6005,  "url":"https://itunes.apple.com/cn/genre/ios-she-jiao/id6005?mt=8"},
    {"name":"体育",       "id":6004,  "url":"https://itunes.apple.com/cn/genre/ios-ti-yu/id6004?mt=8"},
    {"name":"旅游",       "id":6003,  "url":"https://itunes.apple.com/cn/genre/ios-lu-you/id6003?mt=8"},
    {"name":"工具",       "id":6002,  "url":"https://itunes.apple.com/cn/genre/ios-gong-ju/id6002?mt=8"},
    {"name":"天气",       "id":6001,  "url":"https://itunes.apple.com/cn/genre/ios-tian-qi/id6001?mt=8"}
]


def handle_result(response, data):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        request(response.request.url, lambda r,data=data:handle_result(r, data))
        return
    else:
        try:
            logger.info(response.request.url)
            #logger.info(response.body)
            dt = datetime.datetime.strptime(str(data["date"]),'%Y-%m-%d')
            html = unicode(response.body,encoding="utf-8",errors='replace')
            d = pq(html)
            divs = d('div.app-block> div> div.info> p')
            rank = 0
            for div in divs:
                rank += 1
                e = pq(div)
                name = e('a').attr("title")
                raw_id = e('a').attr("href").split("/")[4]
                #logger.info("%s, %s, %s, %s ,%s" % (data["type"], data["genre"], rank, raw_id, name))

                page_url = "http://www.ddashi.com/apps/view/appId/%s" % raw_id
                logger.info(page_url)
                total += 1
                request(page_url, lambda r, data_page=data,raw_id=raw_id,rank=rank: handle_app_page(r, data_page, raw_id, rank))

                # r = appstore_rank_collection.find_one({"date":dt, "type":data["type"], "genre":data["genre"], "appId":app_id})
                # if r is None:
                #     appstore_rank_collection.insert_one({"date":dt, "type":data["type"], "genre":data["genre"], "appId":app_id, "rank":rank})
                # else:
                #     appstore_rank_collection.replace_one({"_id":r["_id"]},{"date":dt, "type":data["type"], "genre":data["genre"], "appId":app_id, "rank":rank})
        except:
            traceback.print_exc()

    total -= 1
    if total <=0:
        exit(0)

def handle_app_page(response, data_page, raw_id, rank):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        request(response.request.url, lambda r,data_page=data_page,raw_id=raw_id,rank=rank:handle_app_page(r, data_page, raw_id, rank))
        return
    else:
        try:
            html_page = unicode(response.body, encoding="utf-8", errors='replace')
            d=pq(html_page)
            divs = d('div.panel-top> div> div> div.row')
            for div in divs:
                f = pq(div)
                if f('div.info-name').text().strip() == "APP ID":
                    app_id = f('div.info-value').text().strip()

                    logger.info("%s, %s, %s, %s ,%s, " % (data_page["type"], data_page["genre"], rank, raw_id, app_id))
                break
        except:
            traceback.print_exc()

    total -= 1
    if total <= 0:
        exit(0)

def begin():
    global total

    t = datetime.date.today()
    datestr = datetime.date.strftime(t,'%Y%m%d')

    for type in types:
        logger.info("Type: %s" % type)
        total += 1
        url = "http://www.ddashi.com/ranking/index/type/%s/date/%s.html" % (type, datestr)
        data = {"type":type, "genre": None, "date":t}
        request(url, lambda r,data=data:handle_result(r, data))
        #
        # for genre in genres:
        #     logger.info("Type: %s, Genre: %s" % (type,genre["id"]))
        #     total += 1
        #     url = "http://www.ddashi.com/ranking/index/type/%s/genre/%s/date/%s.html" % (type,genre["id"],datestr)
        #     data = {"type":type, "genre": genre["id"], "date":t}
        #     request(url, lambda r,data=data:handle_result(r, data))

if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()