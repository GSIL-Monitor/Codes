# -*- coding: utf-8 -*-
import os, sys,random, datetime
import urllib2
import urllib
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues,crawler_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,util,db

#logger
loghelper.init_logger("crawler_boss_company", stream=True)
logger = loghelper.get_logger("crawler_boss_company")

cnt = 0

class LagouCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=15):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if title.find("访问验证") >= 0:
            #logger.info(content)
            return False
        if title.find("BOSS直聘") >= 0:
            return True
        #logger.info(content)
        return False


def has_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    temp = title.split("-")

    if len(temp) < 2:
        return False
    if temp[0].strip() == "BOSS直聘":
        return False
    return True


def process(g, crawler, url, key, content):
    global cnt
    #logger.info(content)
    if has_content(content):
        logger.info(key)
        crawler.save(g.SOURCE, g.TYPE, url, key, content)
        # g.latestIncr()
        cnt += 1

def crawl(crawler, key, g):
    url = "https://www.zhipin.com/gongsi/%s.html?ka=company-intro" % key
    retry_times = 0
    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            # logger.info(result["content"])
            try:
                process(g, crawler, url, key, result['content'])
            except Exception, ex:
                logger.exception(ex)
            break
        elif result['get'] == 'redirect':
            logger.info("Redirect: %s", result["url"])
            break

        retry_times += 1
        if retry_times > 18:
            break

def run(g, last_key, crawler):
    global cnt
    while True:
        key = g.nextKey()
        if int(key) > last_key:
            logger.info("over")
            return

        mongo = db.connect_mongo()
        collection = mongo.raw.projectdata
        collection_job = mongo.job.company
        item = collection.find_one({"source": 13050, "type": 36001, "key_int": int(key)})
        item1 = collection_job.find_one({"source": 13050, "sourceId": key})
        item2 = collection_job.find_one({"source": 13050, "sourceId": int(key)})
        if item is None or (item1 is None and item2 is None):
            logger.info("crawler missing key: %s", key)
            logger.info("*******found %s", cnt)
            crawl(crawler, key, g)
        mongo.close()



def start_run(concurrent_num, flag):
    global DATE
    while True:

        logger.info("Lagou company %s start for all back check", flag)
        

        g = GlobalValues.GlobalValues(13055, 36001, flag)
        last_key = crawler_util.get_latest_key_int(13055, 36001)
        # last_key = 100
        logger.info("Lagou last ddkey %s", last_key)

        threads = [gevent.spawn(run, g, last_key, LagouCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Lagou company %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*30)        #30 minutes
        else:
            gevent.sleep(86400*3)   #3 days

        # break

if __name__ == "__main__":

    start_run(2, "all")