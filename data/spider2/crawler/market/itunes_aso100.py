# -*- coding: utf-8 -*-
import os, sys, re
import datetime
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
import pymongo


reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, db, util

#logger
loghelper.init_logger("itunes_aso100", stream=True)
logger = loghelper.get_logger("itunes_aso100")

linkPattern = "/app/rank/appid/\d+"
#不收录图书，游戏, 报刊杂志
cates = [
    {"name":"商务",       "url": "6000"},
    {"name":"商品指南",    "url": "6022"},
    {"name":"教育",       "url": "6017"},
    {"name":"娱乐",       "url": "6016"},
    {"name":"财务",       "url": "6015"},
    {"name":"美食佳饮",    "url": "6023"},
    {"name":"健康健美",    "url": "6013"},
    {"name":"生活",       "url": "6012"},
    {"name":"医疗",       "url": "6020"},
    {"name":"音乐",       "url": "6011"},
    {"name":"导航",       "url": "6010"},
    {"name":"新闻",       "url": "6009"},
    {"name":"摄影与录像",  "url": "6008"},
    {"name":"效率",       "url": "6007"},
    {"name":"参考",       "url": "6006"},
    {"name":"购物",       "url": "6024"},
    {"name":"社交",       "url": "6005"},
    {"name":"体育",       "url": "6004"},
    {"name":"贴纸",       "url": "6025"},
    {"name":"旅游",       "url": "6003"},
    {"name":"工具",       "url": "6002"},
    {"name":"天气",       "url": "6001"}
]

class asoCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
           return False

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("App Store") >= 0:
            return True
        return False


def save(id, name):
    # check mongo data if link is existed
    mongo = db.connect_mongo()
    collection = mongo.market.itunes_index
    item = collection.find_one({"trackId": int(id)})
    if item is None:
        logger.info("new one!!!!!")
        item = {
            "trackId": int(id),
            "trackName": name,
            "trackViewUrl": "https://itunes.apple.com/cn/app/id%s?mt=8" % id,
            "createTime": datetime.datetime.now(),
            # "modifyTime": datetime.datetime.now(),
        }
        collection.insert_one(item)
    mongo.close()



def process_page(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    for a in d('div.rank-list> div.row> div.col-md-2> div.thumbnail> a'):
        try:
            link = d(a).attr("href").strip()
            name = d(a)('div.caption> h5').eq(0).text()
            if re.search(linkPattern, link):
                logger.info("Link: %s|%s is right news link", link, name)

                id = link.split("/")[-1]
                save(id,name)
            else:
                # logger.info(link)
                pass
        except:
            logger.info("cannot get link")

def start_run():

    while True:
        logger.info("aso100 check start...")

        crawler = asoCrawler()
        for cate in cates:
            logger.info("crawler aso100 for :%s", cate["name"])
            page_url = "https://aso100.com/rank/release/country/cn/device/iphone/brand/free/genre/%s" % cate["url"]

            while True:
                result = crawler.crawl(page_url, agent=True)
                if result['get'] == 'success':

                    process_page(result["content"])

                    break


        logger.info("aso100 check end.")

        gevent.sleep(60*180)        #10 minutes



if __name__ == "__main__":
    start_run()

