# -*- coding: utf-8 -*-
import sys, os
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

from pyquery import PyQuery as pq

from lxml import html
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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import crawler_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import market.flyme as flyme_parser

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler


#logger
loghelper.init_logger("flyme_trends", stream=True)
logger = loghelper.get_logger("flyme_trends")

#mongo
mongo = db.connect_mongo()
collection = mongo.trend.android

collection_market = mongo.market.android_market #TODO

cnt = 0
total = 0
TYPE = 16060
SC=[]

headers = {}
headers[
    "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"


class LagouCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=20):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8","ignore")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if title.find("魅族") >= 0:
            return True

        return False


def has_content(content, apkname):
    # d = pq(html.fromstring(content.decode("utf-8")))
    if content.find(u'很抱歉，您要访问的页面无法正常显示，可能是因为如下原因') >= 0:
        logger.info('404 for %s', apkname)
        return True
    elif content.find(u'魅友评分') >= 0:
        return True
    else:
        return False

def process(crawler, url, apkname, content):


    try:
        # Parser data for newupdates:
        #logger.info("%s->%s", apkname, url)
        flyme_parser.process(None, url, apkname, content)

        #html = unicode(response.body,encoding="utf-8",errors='replace')


        d = pq(html.fromstring(content.decode("utf-8")))
        download = d('span:contains("下      载：")+ div').text().strip()
        score = d('span:contains("魅友评分")+ div > div').attr('data-num').strip()

        score = float(score)/10
        download = float(download)
        crawler_util.save_download(apkname,TYPE, download,score)
        logger.info("apkname=%s, download=%s, score=%s" % (apkname, download,score))

    except:
        traceback.print_exc()


        #exit(0)


def run(crawler):
    while True:
        if len(SC) == 0:
            return
        info = SC.pop(0)
        url = info["link"]
        apkname = info["apkname"]
        retry_times = 0
        while True:
            result = crawler.crawl(url, agent=True, headers=headers)
            if result['get'] == 'success':
                # logger.info(result["content"])
                if has_content(result["content"], apkname):
                    try:
                        process(crawler, url, apkname, result['content'])
                    except Exception, ex:
                        logger.exception(ex)
                    break
            retry_times += 1
            if retry_times > 10:
                break



def begin(concurrent_num):
    global total, cnt

    flag = False
    while flag is False:
         # conn = db.connect_torndb()
        conn = db.connect_torndb_proxy()
        apps = conn.query("select * from artifact where type=4050 and id>%s order by id limit 10000", cnt)
        # apps = conn.query("select * from artifact where type=4050 and domain ='so.ofo.labofo' and id>%s order by id limit 1", cnt)
        # apps = conn.query("select * from artifact where id>371210 and id<371250")

        conn.close()

        if len(apps) <= 0:
           break


        for app in apps:
            # logger.info(app["name"])
            if app["id"] > cnt:
                cnt = app["id"]

            if app["domain"] is None or app["domain"].strip() == "":
                continue

            domain = app["domain"].strip()
            app["domain"] = domain
            dt = datetime.date.today()
            today = datetime.datetime(dt.year, dt.month, dt.day)

            m = collection_market.find_one({"appmarket":TYPE, "apkname": domain})
            if m is None:
                continue

            r = collection.find_one(({"appmarket":TYPE, "apkname": domain, "date": today}))
            if r is not None:
                # pass
                continue
            logger.info(app["name"])
            logger.info(m["link"])
            info = {
                "link": m["link"],
                "apkname": app["domain"],
            }
            SC.append(info)

        threads = [gevent.spawn(run, LagouCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)


if __name__ == "__main__":
    while True:
        begin(10)
        break