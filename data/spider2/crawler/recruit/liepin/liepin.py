# -*- coding: utf-8 -*-
import os, sys, random, datetime
import urllib2
import urllib
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey;

monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, util, db

# logger
loghelper.init_logger("crawler_liepin_company", stream=True)
logger = loghelper.get_logger("crawler_liepin_company")

DATE = None
SOURCE = 13056
TYPE = 36001
URLS = []

columns = [
    {"column": None, "max": 99},
]


class LiepinCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=15):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    # 实现
    def is_crawl_success(self, url, content):
        if url.find('curPage') >= 0:
            if content.find('<p class="company-name">') >= 0: return True
        elif url.find('company') >= 0:
            if content.find('<div class="name-and-welfare">') >= 0: return True
        return False


def has_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    # logger.info("title: " + title)

    temp = title.split("-")

    if len(temp) < 2:
        return False
    if temp[0].strip() == "BOSS直聘":
        return False
    return True


def process(g, crawler, url, key, content):
    # logger.info(content)
    # if has_content(content):
    if 1:
        logger.info('saving %s', key)
        crawler.save(SOURCE, TYPE, url, key, content)


def crawl(crawler, key, g):
    url = "https://www.liepin.com/company/%s/" % key
    retries = 0
    while True:
        retries += 1
        if retries > 10: break
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            # logger.info(result["content"])
            try:
                process(g, crawler, url, key, result['content'])
            except Exception, ex:
                logger.exception(ex)
            break


def run(g, crawler):
    while True:
        if len(URLS) == 0: return
        linkDict = URLS.pop()
        crawl(crawler, linkDict['key'], g)


def get_list(crawler, concurrent_num, column):
    key = 0
    while True:
        if key > column['max']: break
        url = 'https://www.liepin.com/zhaopin/?jobTitles=&industries=040&curPage=%s' % key
        key += 1
        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                d = pq(html.fromstring(result['content'].decode("utf-8")))

                companies = d('.company-name')
                mongo = db.connect_mongo()
                for c in companies:
                    link = d(c)('a').attr('href')
                    sourceId = link.split('company/')[-1][:-1]
                    linkDict = {'link': link, 'key': sourceId}

                    collection = mongo.raw.projectdata

                    item = collection.find_one({"source": SOURCE, 'key': sourceId})
                    if item is None:
                        logger.info('not exists %s ,%s ' % (SOURCE, sourceId))
                        URLS.append(linkDict)
                    else:
                        logger.info('already exists %s , %s', SOURCE, sourceId)
                mongo.close()
                break

        g = GlobalValues.GlobalValues(SOURCE, TYPE, "incr", back=0)
        threads = [gevent.spawn(run, g, LiepinCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)


def start_run(concurrent_num, flag):
    global DATE
    while True:
        # logger.info("liepin last back is %s", DATE)
        # logger.info("liepin company %s start for %s", flag, datestr)
        logger.info("liepin start")
        for column in columns:
            get_list(LiepinCrawler(), concurrent_num, column)
        logger.info("liepin company %s end.", flag)

        if flag == "incr":
            gevent.sleep(60 * 30)  # 30 minutes
        else:
            gevent.sleep(86400 * 3)  # 3 days

        # break


if __name__ == "__main__":

    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(23, "all")
        else:
            key = str(int(param))
            g = GlobalValues.GlobalValues(SOURCE, 36001, "incr", back=0)
            crawl(LiepinCrawler(), key, g)
    else:
        start_run(1, "incr")
