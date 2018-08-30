# -*- coding: utf-8 -*-
import os, sys
import datetime
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
import pymongo
from distutils.version import LooseVersion
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, db, util

#logger
loghelper.init_logger("itunes_index", stream=True)
logger = loghelper.get_logger("itunes_index")

#mongo
mongo = db.connect_mongo()
collection = mongo.market.itunes_index

#不收录图书，游戏, 报刊杂志
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
    {"name":"贴纸",       "url":"https://itunes.apple.com/cn/genre/ios-贴纸/id6025?mt=8"},
    {"name":"旅游",       "url":"https://itunes.apple.com/cn/genre/ios-lu-you/id6003?mt=8"},
    {"name":"工具",       "url":"https://itunes.apple.com/cn/genre/ios-gong-ju/id6002?mt=8"},
    {"name":"天气",       "url":"https://itunes.apple.com/cn/genre/ios-tian-qi/id6001?mt=8"}
]

letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T",
           "U","V","W","X","Y","Z","*"]
hzs = []
hzs2 = []
page_urls = []
nn = 0

class ItunesCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self,url, content):
        if content.find('400-666-8800') > 0:
            return True
        return False


def process_page(url, content):
    global page_urls

    d = pq(content)
    apps = d('div#selectedcontent> div> ul> li')
    for app in apps:
        name = pq(app).text()
        app_url = pq(app)('a').attr('href')
        (app_id,) = util.re_get_result(r"id(\d+)",app_url)
        try:
            trackId = int(app_id)
        except Exception,e:
            logger.info(traceback.format_exc())
            logger.info(app_url)

        logger.info("%s %s %s" % (trackId, name, app_url))

        #if util.isChineseString(name):
        if 1==1:
            item = collection.find_one({"trackId":trackId})
            if item is None:
                data = {
                    "trackId":trackId,
                    "trackName":name,
                    "trackViewUrl":app_url,
                    "createTime":datetime.datetime.now()
                }
                collection.insert_one(data)
            else:
                data = {
                    "trackName":name,
                    "trackViewUrl":app_url,
                    "modifyTime":datetime.datetime.now()
                }
                collection.update_one({"trackId":trackId},{'$set':data})

    if len(apps) > 10:
        result = util.re_get_result(r"page=(\d*)",url)
        if result is not None:
            (strPage,) = result
            nextPage = str(int(strPage) + 1)
            url = url.replace("page="+strPage, "page="+nextPage)
            logger.info(url)
            page_urls.append(url)


def run():
    global page_urls
    crawler = ItunesCrawler()
    while True:
        if len(page_urls) == 0:
            return
        url = page_urls.pop(0)

        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                #logger.info(result["content"])
                process_page(url, result['content'])
                break


def start_run(concurrent_num):
    global hzs, page_urls, nn

    lines = open('hanzi.txt').readlines( )
    for line in lines:
        line = unicode(line.strip(), "utf-8")
        for hz in line:
            if hz == "":
                continue
            if hz >= 'A' and hz <= 'Z':
                continue
            hzs.append(hz)

    lines2 = open('hanzi2.txt').readlines()
    for line in lines2:
        line = unicode(line.strip(), "utf-8")
        for hz in line:
            if hz == "":
                continue
            if hz >= 'A' and hz <= 'Z':
                continue
            if hz in hzs:
                continue
            hzs2.append(hz)

    while True:
        nn += 1


        for cate in cates:
            logger.info(cate["name"])
            logger.info(cate["url"])
            page_urls.append(cate["url"])

            for letter in letters:
                url = cate["url"] + "&letter=" + letter + "&page=1#page"
                logger.info(url)
                page_urls.append(url)

                if letter != "*":
                    url = cate["url"] + "&letter=" + letter.lower() + "&page=1#page"
                    logger.info(url)
                    page_urls.append(url)

            for letter in hzs:
                url = cate["url"] + "&letter=" + letter + "&page=1#page"
                logger.info(url)
                page_urls.append(url)

            if nn%3 == 1:
                for letter in hzs2:
                    url = cate["url"] + "&letter=" + letter + "&page=1#page"
                    logger.info(url)
                    page_urls.append(url)


        logger.info("itunes index start...")

        threads = [gevent.spawn(run) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("itunes index end.")

        #break

        gevent.sleep(86400*0.5)       #1/2 day


if __name__ == "__main__":
    start_run(20)