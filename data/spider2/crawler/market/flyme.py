# -*- coding: utf-8 -*-
import os, sys, datetime
import pymongo
from pymongo import MongoClient
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey;

monkey.patch_all()
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

# logger
loghelper.init_logger("crawler_flyme", stream=True)
logger = loghelper.get_logger("crawler_flyme")

# mongo
mongo = db.connect_mongo()
collection = mongo.market.android_market
collection_android = mongo.market.android

APKS = []
APPMARKET = 16060


class MyappCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)

        # 实现
        # def is_crawl_success(self, url, content):
        #     if content.find("</html>") == -1:
        #         return False
        #     d = pq(html.fromstring(content))
        #     title = d('head> title').text().strip()
        #     logger.info("title: " + title + " " + url)
        #
        #     if title.find("应用宝") >= 0:
        #         return True
        #
        #     return False


def has_content(content, apkname):
    d = pq(html.fromstring(content))
    # logger.info("title: " + title)
    if content.find(u'应用简介：') == -1:
        return False
    return True


def process(crawler, url, apkname, content):
    # logger.info(content)
    if has_content(content, apkname):

        if content.find(r'</br>') > 0:
            content = content.replace(r'</br>', "")

        d = pq(html.fromstring(content.decode("utf-8")))

        name = d('.detail_top h3').text()
        # logger.info("name: %s",name)

        icon = d('.app_download .app_img').attr("src")

        screenshots = []
        imgs = d('.detail_img')
        # logger.info(imgs)
        for img in imgs:
            imgurl = pq(img).attr("href")
            # logger.info("url: %s", imgurl)
            screenshots.append(imgurl)

        desc = d('.description_detail').eq(0).text().replace("\r", "")
        logger.info("desc: %s", desc)

        updates = d('.description_detail').eq(1).text().replace("\r", "")
        logger.info("updates: %s", updates)

        size = d('span:contains("大      小：")+ div').text().strip()

        try:
            size = float(size.replace("MB", ""))
            size = str(round(size * 1024 * 1024))
        except:
            pass

        tag = d('span:contains("类      别：")+ div').text().strip()
        logger.info("tag: %s", tag)

        # (datestr,) = util.re_get_result('data-apkPublishTime=\"(.*?)\"', content)
        datestr = d('span:contains("更新时间：")+ div').text()
        # logger.info("datastr=%s" % datestr)
        # updatedate = datetime.datetime.fromtimestamp(int(datestr))
        updatedate = datetime.datetime.strptime(datestr, '%Y-%m-%d')
        # logger.info("updatedate=%s" % updatedate)

        versionname = None
        try:
            versionname = d('span:contains("版      本：")+ div').text().strip()
            logger.info("versionname: %s", versionname)
            if versionname.startswith("V"):
                versionname = versionname.replace("V", "")
                # logger.info("versionname: %s", versionname)
        except:
            pass

        author = None
        try:
            author = d('span:contains("开 发 者 ")+ div').text()
            chinese, is_company = name_helper.name_check(author)
            if chinese and is_company:
                author = name_helper.company_name_normalize(author)
                # logger.info("author: %s", author)
        except:
            pass

        # (download,) = util.re_get_result('downTimes:"(.*?)"', content)
        download = d('span:contains("下      载：")+ div').text().strip()
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
            "download": download,
        }
        logger.info(json.dumps(item, ensure_ascii=False, cls=util.CJsonEncoder))

        android.save(collection, APPMARKET, item)
        android.merge(item)
        collection_android.update_one({"apkname": apkname}, {"$set": {"flymeprocessed": True, "flymefound": True}})
    else:
        logger.info("App: %s has no content", apkname)
        collection_android.update_one({"apkname": apkname}, {"$set": {"flymeprocessed": True, "flymefound": False}})


def run(crawler):
    while True:
        if len(APKS) == 0:
            return
        apkname = APKS.pop(0)

        url = "http://app.flyme.cn/apps/public/detail?package_name=%s" % apkname
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success' and result['content'].find(u'很抱歉，您要访问的页面无法正常显示，可能是因为如下原因') < 0:
                # logger.info(result["content"])
                try:
                    process(crawler, url, apkname, result['content'])
                except Exception, ex:
                    logger.exception(ex)
                break
            elif result['get'] == 'success' and result['content'].find(u'很抱歉，您要访问的页面无法正常显示，可能是因为如下原因') >= 0:
                # logger.info(result['content'])
                logger.info("App: %s is not found", apkname)
                collection_android.update_one({"apkname": apkname},
                                              {"$set": {"flymeprocessed": True, "flymefound": False}})

                break


def start_run(concurrent_num):
    while True:
        logger.info("flyme %s start...")
        # run(appmkt, MyappCrawler(), "com.tencent.mm")

        apps = list(collection_android.find({"flymeprocessed": None}, {"apkname": 1}, limit=1000))
        # apps = [{'apkname': 'com.sankuai.meituan'}]
        for app in apps:
            apkname = app["apkname"]
            if apkname is None:
                continue
            APKS.append(apkname)
        # APKS.append("com.samapp.excelsms.excelsmslite")

        threads = [gevent.spawn(run, MyappCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("flyme end.")

        if len(apps) == 0:
            gevent.sleep(30 * 60)


if __name__ == "__main__":
    start_run(5)
