# -*- coding: utf-8 -*-
import os, sys,datetime
import pymongo
from pymongo import MongoClient
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db
import loghelper
import util, name_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler
import android

#logger
loghelper.init_logger("crawler_myapp", stream=True)
logger = loghelper.get_logger("crawler_myapp")

#mongo
mongo = db.connect_mongo()
collection = mongo.market.android_market
collection_android = mongo.market.android


APKS=[]
APPMARKET=16040

class MyappCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if title.find("应用宝") >= 0:
            return True

        return False


def has_content(content,apkname):
    d = pq(html.fromstring(content))
    #logger.info("title: " + title)
    if content.find(apkname) == -1:
        return False
    return True

def process(crawler, url, apkname, content):
    #logger.info(content)
    if has_content(content,apkname):

        if content.find(r'</br>') >0:
            content=content.replace(r'</br>', "")

        d = pq(html.fromstring(content.decode("utf-8")))

        name = d('div.det-name-int').text()
        #logger.info("name: %s",name)

        icon = d('div.det-icon> img').attr("src")

        screenshots = []
        imgs = d('span.pic-turn-img-box> div> img')
        # logger.info(imgs)
        for img in imgs:
            imgurl = pq(img).attr("data-src")
            #logger.info("url: %s", imgurl)
            screenshots.append(imgurl)

        desc = d('div.det-app-data-info').eq(0).text().replace("\r","")
        #logger.info("desc: %s", desc)

        updates = d('div.det-app-data-info').eq(1).text().replace("\r","")
        #logger.info("updates: %s",updates)

        size = d('div.det-size').text()
        try:
            size =float(size.replace("M",""))
            size = str(round(size*1024*1024))
        except:
            pass

        #logger.info("size: %s",size)

        tag = d('a#J_DetCate').text()
        #logger.info("tag: %s", tag)

        (datestr,) = util.re_get_result('data-apkPublishTime=\"(.*?)\"', content)
        #logger.info("datastr=%s" % datestr)
        updatedate = datetime.datetime.fromtimestamp(int(datestr))
        #logger.info("updatedate=%s" % updatedate)

        versionname = None
        try:
            versionname = d('div.det-othinfo-container> div.det-othinfo-data').eq(0).text()
            #logger.info("versionname: %s", versionname)
            if versionname.startswith("V"):
                versionname = versionname.replace("V", "")
                #logger.info("versionname: %s", versionname)
        except:
            pass

        author = None
        try:
            author = d('div.det-othinfo-container> div.det-othinfo-data').eq(2).text()
            chinese, is_company = name_helper.name_check(author)
            if chinese and is_company:
                author = name_helper.company_name_normalize(author)
            #logger.info("author: %s", author)
        except:
            pass

        (download, ) = util.re_get_result('downTimes:"(.*?)"', content)
        download = float(download)

        item = {
            "link": url,
            "apkname": apkname,
            "appmarket": APPMARKET,
            "name": name,
            "brief": None,
            "website": None,
            "description": desc,
            "commentbyeditor": None,
            "updateDate": updatedate,
            "language": None,
            "tags": tag,
            "version": versionname,
            "updates": updates,
            "size": size,
            "compatibility": None,
            "icon": icon,
            "author": author,
            "screenshots": screenshots,
            "type": None,
            "key": apkname,
            "key_int": None,
            "download":download,
        }
        logger.info(json.dumps(item, ensure_ascii=False, cls=util.CJsonEncoder))

        android.save(collection, APPMARKET, item)
        android.merge(item)
        collection_android.update_one({"apkname": apkname}, {"$set": {"myappprocessed": True, "myappfound": True}})
    else:
        logger.info("App: %s has no content", apkname)
        collection_android.update_one({"apkname": apkname}, {"$set": {"myappprocessed": True, "myappfound": False}})



def run(crawler):
    while True:
        if len(APKS) ==0:
            return
        apkname = APKS.pop(0)

        url = "http://android.myapp.com/myapp/detail.htm?apkName=%s" % apkname
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    process(crawler, url, apkname, result['content'])
                except Exception,ex:
                    logger.exception(ex)
                break
            elif result['get'] == 'fail' and result['content'] is not None:
                #logger.info(result['content'])
                if result['content'].find("java.lang.NullPointerException") > 0 and result['content'].find("500 Servlet Exception") > 0:
                    logger.info("App: %s is not found", apkname)
                    collection_android.update_one({"apkname": apkname}, {"$set": {"myappprocessed": True, "myappfound": False}})

                    break


def start_run(concurrent_num):
    while True:
        logger.info("myapp %s start...")
        #run(appmkt, MyappCrawler(), "com.tencent.mm")

        apps = list(collection_android.find({"myappprocessed": None}, {"apkname": 1}, limit=1000))
        for app in apps:
            apkname = app["apkname"]
            if apkname is None:
                continue
            APKS.append(apkname)
        # APKS.append("com.xingin.xhs")

        threads = [gevent.spawn(run, MyappCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("myapp end.")

        if len(apps) == 0:
            gevent.sleep(30 * 60)


if __name__ == "__main__":
    start_run(5)