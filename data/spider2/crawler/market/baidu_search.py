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
collection_search = mongo.market.baidu_search
collection_market = mongo.market.android_market

NAMES = []

class BaiduSearchCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self,url, content):
        if content.find("模板帮助函数") > 0:
            return True
        return False


def process(search_name, from_doc_id, content):
    d = pq(util.html_encode(content))

    divs = d('div.app')
    for div in divs:
        e = pq(div)
        a = e('a.app-name')
        name = a.text().strip()
        #logger.info(name)
        href = a.attr("href")
        #logger.info(href)
        result = util.re_get_result("docid=(\d*)",href)
        if result:
            (docid_str,) = result
            try:
                docid = long(docid_str)
            except:
                continue
        else:
            continue

        data = e('a.inst-btn')
        if len(data) == 0:
            data = e('a.inst-btn-big')
        if len(data) == 0:
            continue
        type = data.attr("data_detail_type")
        apkname = data.attr("data_package")
        version = data.attr("data_versionname")
        size = None
        try:
            size = long(data.attr("data_size"))
        except:
            pass

        item = {
            "key_int": docid,
            "search_name": search_name,
            "name": name,
            "link": "http://shouji.baidu.com/software/%s.html" % docid,
            "type": type,
            "apkname": apkname,
            "version": version,
            "size": size
        }
        #logger.info(json.dumps(item, ensure_ascii=False, cls=util.CJsonEncoder))

        try:
            android.save_baidu_search(collection_search, item)
        except Exception,e:
            logger.info(e)

def run():
    crawler = BaiduSearchCrawler()

    while True:
        if len(NAMES) ==0:
            return

        app = NAMES.pop(0)
        search_name = app["name"]

        if app["cate"] == "游戏":
            logger.info("游戏: %s", search_name)
            collection_index.update({"_id":app["_id"]},{"$set":{"processed": True}})
            continue

        logger.info("*****search: %s - %s", search_name, app["key_int"])

        found = False
        item = collection_market.find_one({"appmarket":16020,"key_int":app["key_int"]})
        if item:
            logger.info("key_int exist in market_android: %s - %s", search_name, item["key_int"])
            found = True

        if found is False:
            item = collection_search.find_one({"key_int":app["key_int"]})
            if item:
                logger.info("key_int exist in baidu_search: %s", search_name)
                found = True

        if found is False:
            if search_name is None or search_name == "":
                found = True

        if found is False:
            item = collection_search.find_one({"search_name":search_name})
            if item:
                logger.info("searched before: %s", search_name)
                found = True

        if found is False:
            finish = False
            page = 0
            while True:
                url = "http://shouji.baidu.com/s?data_type=app&multi=0&ajax=1&wd=%s&page=%s" % (urllib.quote(search_name.encode("utf-8")),page)
                #logger.info(url)
                while True:
                    result = crawler.crawl(url)
                    if result['get'] == 'success':
                        content = result["content"]
                        #logger.info(content)
                        if content.find('<div class="clear"></div>') == -1:
                            finish = True
                        else:
                            process(search_name, app["key_int"], content)
                        break
                if finish:
                    break
                page += 1

        collection_index.update({"_id":app["_id"]},{"$set":{"processed": True}})

def start_run(concurrent_num):
    while True:
        logger.info("start...")
        apps = list(collection_index.find({"processed": {"$ne": True}}, limit=1000))
        #apps = [{"name":"teambition"}]
        for app in apps:
            NAMES.append(app)
        threads = [gevent.spawn(run) for i in xrange(concurrent_num)]
        gevent.joinall(threads)


        logger.info("end.")

        if len(apps) == 0:
            gevent.sleep(5*60)


if __name__ == "__main__":
    start_run(30)