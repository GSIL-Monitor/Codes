# -*- coding: utf-8 -*-
import os, sys
import datetime
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
import pymongo
from distutils.version import LooseVersion
import urllib

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, db, util, name_helper
import android

#logger
loghelper.init_logger("baidu", stream=True)
logger = loghelper.get_logger("baidu")

#mongo
mongo = db.connect_mongo()
collection_index = mongo.market.baidu_index

START = 0
LATEST = 0

class BaiduCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self,url, content):
        if url.find("shouji.baidu.com") >= 0:
            if content.find("请检查您所输入的URL地址是否有误") > 0:
                return True
            if content.find("请填写举报原因") > 0:
                return True
        if url.find("m.baidu.com") >= 0:
            try:
                data = json.loads(content)
                if data["status"] == "success":
                    return True
            except:
                pass

        return False


def process(url, key, content):
    global LATEST
    if content.find('请检查您所输入的URL地址是否有误') != -1:
        return

    record = collection_index.find_one({"key_int":key})
    if record:
        return

    record = collection_index.find_one({"docids.docid":key})
    if record:
        return

    #logger.info(content)

    d = pq(content)
    cate = d('div.nav> span >a').eq(1).text().strip()
    #if cate == "游戏":
    #    return

    sub_cate = d('div.nav> span >a').eq(2).text().strip()
    name = d('h1.app-name> span').text().strip()

    version = None
    version_str = d('span.version').text()
    if version_str:
        version = version_str.replace("版本:","").strip()

    #logger.info("%s-%s, %s, %s", cate, sub_cate, name, version)

    docids = []
    origin_items = d('li.origin-item')
    for item in origin_items:
        c =pq(item)
        href = c('a').attr("href")
        result = util.re_get_result("docid=(\d*)",href)
        origin = c('a').text().strip()
        if result:
            (docid,) = result
            #logger.info(docid)
            try:
                f = {"docid":long(docid),
                     "origin":origin}
                docids.append(f)
            except:
                pass

    item = {
        "link": url,
        "name": name,
        "cate": cate,
        "sub_cate": sub_cate,
        "version": version,
        "updates": None,
        "docids":docids,
        "key_int": key,
    }
    logger.info(json.dumps(item, ensure_ascii=False, cls=util.CJsonEncoder))

    android.save_baidu_index(collection_index, item)

    if LATEST < key:
        LATEST = key

def run():
    global START, LATEST

    crawler = BaiduCrawler()
    while True:
        if START > 8000000 and START > LATEST + 2000:
            return
        key = START
        START += 1
        url = "http://shouji.baidu.com/software/%s.html" % key
        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                #logger.info(result["content"])
                process(url, key, result['content'])
                break


def start_run(concurrent_num, flag):
    global START, LATEST
    while True:
        logger.info("baidu %s start...", flag)

        LATEST = 22
        if flag == "incr":
            item = collection_index.find_one(sort=[("key_int", pymongo.DESCENDING)], limit=1)
            if item:
                LATEST = item["key_int"] + 1
        START = LATEST

        threads = [gevent.spawn(run) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("baidu %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*30)         #30 minutes
        else:
            gevent.sleep(86400*0.5)       #1/2 day


if __name__ == "__main__":
    flag = "incr"
    concurrent_num = 10
    if len(sys.argv) > 1:
        flag = sys.argv[1]
    if flag == "all":
        concurrent_num = 50

    start_run(concurrent_num, flag)