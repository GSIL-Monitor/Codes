# -*- coding: utf-8 -*-
import os, sys
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import crawler_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper

#logger
loghelper.init_logger("crawler_chuangyepu_company", stream=True)
logger = loghelper.get_logger("crawler_chuangyepu_company")

SOURCE = 13040  #创业铺
TYPE = 36001    #公司信息
PAGE = 1
URLS = []

class ChuangyepuPageCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: " + title)
        page = url.split("page=")[-1]
        str = "含的项目列表 | Page %s | 创业谱" % page
        if title == str:
            return True
        return False


class ChuangyepuCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        try:
            d = pq(html.fromstring(content))
            title = d('head> title').text().strip()
            logger.info("title: " + title)
            if title.find("创业谱") >= 0:
                return True
        except Exception,e:
            logger.info(e)
        return False


def process(crawler, url, content):
    if content is None:
        logger.info("Fail to get content")
        return
    key = url.split("/")[-1]
    #logger.info(content)
    crawler.save(SOURCE, TYPE, url, key, content)


def run(flag, crawler, url=None):
    global URLS
    if url is None:
        while url is None:
            if len(URLS) > 0:
                url = URLS.pop(0)
            else:
                gevent.sleep(10)

    if flag == "incr":
        key = url["url"].split("/")[-1]
        if crawler_util.get(SOURCE,TYPE,key) is not None:
            logger.info("%s exist!", url["name"])
            gevent.spawn(run, flag, crawler)
            return

    logger.info(url["name"])
    result = crawler.crawl(url["url"])

    if result['get'] == 'success':
        process(crawler, url["url"], result['content'])
        gevent.spawn(run, flag, crawler)
    else:
        gevent.spawn(run, flag, crawler, url)


def has_content_page(content):
    d = pq(content)
    text_error = d('p.text-error').text().strip()

    if text_error != "很抱歉，创业谱没有为您找到相关条目。":
        return True
    return False


def process_page(event, content):
    global URLS
    if has_content_page(content):
        #logger.info(r.text)
        d = pq(content)
        divs = d('div.caption')
        for div in divs:
            l = pq(div)
            name = l("div.name> a").text().strip()
            url = "http://chuangyepu.com" + l("div.name> a").attr("href").strip()
            u = {"name":name,"url":url}
            logger.info("name: %s", name)
            logger.info("url: %s", url)
            URLS.append(u)

        return False
    else:
        return True


def run_page(event, flag, crawler, page=None):
    global PAGE
    if flag == "incr" and page is None:
        if PAGE > 5:
            event.set()
            return

    if page is None:
        page = PAGE
        PAGE += 1

    url = "http://chuangyepu.com/search/startups?key_word=&page=%s" % page
    result = crawler.crawl(url)

    if result['get'] == 'success':
        isEnd = process_page(event, result['content'])
        if isEnd:
            event.set()
            return
        gevent.spawn(run_page, event, flag, crawler)
    else:
        gevent.spawn(run_page, event, flag, crawler, page)


def start_run(concurrent_num, flag):
    global PAGE
    while True:
        logger.info("Chuangyepu company start...")
        PAGE = 1
        event = Event()

        for i in range(concurrent_num/12):
            gevent.spawn(run_page, event, flag, ChuangyepuPageCrawler())
        for i in range(concurrent_num):
            gevent.spawn(run, flag, ChuangyepuCrawler())

        event.wait()
        logger.info("Chuangyepu company end.")

        if flag == "incr":
            gevent.sleep(60*30)        #30 minutes
        else:
            gevent.sleep(86400*3)   #3 days


if __name__ == "__main__":
    #start_run(50, "incr")
    start_run(50, "all")