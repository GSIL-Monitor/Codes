# -*- coding: utf-8 -*-
import os, sys
import time
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
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
collection = mongo.market.android_market
collection_search = mongo.market.baidu_search

APPMARKET = 16020

APPS = []

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


def process(crawler, app, content):
    if content.find('请检查您所输入的URL地址是否有误') != -1:
        return

    key = app["key_int"]
    url = app["link"]

    d = pq(content)
    cate = d('div.nav> span >a').eq(1).text().strip()
    if cate == "游戏":
        return

    sub_cate = d('div.nav> span >a').eq(2).text().strip()
    name = d('h1.app-name> span').text().strip()
    downloadstr = d("span.download-num").eq(0).text().replace("下载次数:","").replace("+","").strip()
    if downloadstr.endswith("千"):
        download = float(downloadstr.replace("千","")) * 1000
    elif downloadstr.endswith("万"):
        download = float(downloadstr.replace("万","")) * 10000
    elif downloadstr.endswith("亿"):
        download = float(downloadstr.replace("亿","")) * 10000 * 10000
    else:
        download = int(downloadstr)
    logger.info("%s-%s, %s, %s", cate, sub_cate, name, download)


    mosug_url = "http://m.baidu.com/mosug?wd=%s&type=soft" % urllib.quote(name.encode("utf-8"))
    while True:
        result = crawler.crawl(mosug_url)
        if result['get'] == 'success':
            mosug_content = result["content"]
            break
    #logger.info(mosug_content)

    data = json.loads(mosug_content)
    if data["result"].get("s") is None:
        return

    found = False
    for dt in data["result"].get("s"):
        if dt.get("package") is None:
            continue
        if long(dt["docid"]) == key:
            download = int(dt["download_num"])
            score = int(dt["score"]) * 0.05
            break


    # screenshot
    screenshots = []
    imgs = d('img.imagefix')
    #logger.info(imgs)
    for img in imgs:
        surl = pq(img).attr("src")
        #logger.info(url)
        screenshots.append(surl)

    # content
    desc = d('p.content').text()
    #logger.info(desc)

    icon = d('div.app-pic> img').attr("src")
    #logger.info(icon)
    author = d('div.origin-wrap> span> span').eq(1).text()
    chinese, is_company = name_helper.name_check(author)
    if chinese and is_company:
        author = name_helper.company_name_normalize(author)
    #logger.info("author: %s", author)
    commentbyeditor = d('span.head-content').text()

    item = {
        "link": url,
        "apkname": app["apkname"],
        "appmarket": APPMARKET,
        "name": name,
        "brief": None,
        "website": None,
        "description": desc,
        "commentbyeditor": commentbyeditor,
        "updateDate": None,
        "language": None,
        "tags": sub_cate,
        "version": app["version"],
        "updates": None,
        "size": app["size"],
        "compatibility": None,
        "icon": icon,
        "author": author,
        "screenshots": screenshots,
        "type": app["type"],
        "key": str(key),
        "key_int": key,
        "download": download
    }
    logger.info(json.dumps(item, ensure_ascii=False, cls=util.CJsonEncoder))

    android.save(collection, APPMARKET, item)
    android.merge(item)


def run():
    crawler = BaiduCrawler()
    while True:
        if len(APPS) ==0:
            return

        app = APPS.pop(0)
        #logger.info(app["key_int"])

        if app["type"] != "soft":
            collection_search.update({"_id":app["_id"]},{"$set":{"processed": True}})
            continue

        key = app["key_int"]
        url = app["link"]
        item = collection.find_one({"appmarket":APPMARKET, "key_int":key}, projection={'histories': False})
        if item:
            collection_search.update({"_id":app["_id"]},{"$set":{"processed": True}})
            continue

        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                # logger.info(result["content"])
                process(crawler, app, result['content'])
                break

        collection_search.update({"_id":app["_id"]},{"$set":{"processed": True}})


def start_run(concurrent_num):
    while True:
        logger.info("start...")
        apps = list(collection_search.find({"processed": {"$ne": True}}, limit=1000))
        for app in apps:
            APPS.append(app)
        threads = [gevent.spawn(run) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("end.")

        if len(apps) == 0:
            gevent.sleep(1*60)

if __name__ == "__main__":
    start_run(10)