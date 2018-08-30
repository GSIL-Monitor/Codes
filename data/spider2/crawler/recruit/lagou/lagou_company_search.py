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
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,util

#logger
loghelper.init_logger("crawler_lagou_company", stream=True)
logger = loghelper.get_logger("crawler_lagou_company")

DATE = None

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
        if title.find("找工作-互联网招聘求职网-拉勾网") >= 0:
            return False
        if title.find("拉勾网") >= 0:
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
    if temp[0].strip() == "找工作":
        return False
    return True



def process(crawler, url, key, content):
    #logger.info(content)
    if has_content(content):
        logger.info(key)
        crawler.save(13050, 36001, url, key, content)

def crawl(crawler, key, g):
    url = "https://www.lagou.com/gongsi/%s.html" % key
    retry_times = 0
    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            # logger.info(result["content"])
            try:
                process(crawler, url, key, result['content'])
            except Exception, ex:
                logger.exception(ex)
            break
        elif result['get'] == 'redirect':
            logger.info("Redirect: %s", result["url"])
            break

        retry_times += 1
        if retry_times > 10:
            break


def start_run(keyword, sourceId):

    companycrawler = LagouCrawler()
    while True:
        if sourceId is None:
            pass
        else:
            crawl(companycrawler, str(sourceId), "new")
        break

        #break

if __name__ == "__main__":
    start_run("teambitionBBBB", None)