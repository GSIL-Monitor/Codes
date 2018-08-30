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
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper

#logger
loghelper.init_logger("crawler_itjuzi_company", stream=True)
logger = loghelper.get_logger("crawler_itjuzi_company")


class ItjuziCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title == "找不到您访问的页面":
            #return True
            return False
        if title.find("IT桔子") >= 0:
            return True
        return False


def has_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    temp = title.split("|")
    if len(temp) != 2:
        return False
    if temp[1].strip() != "IT桔子":
        return False
    if temp[0].strip() == "" or temp[0].strip() == "的简介，官网，联系方式，":
        return False
    return True


def process(g, crawler, url, key, content):
    if has_content(content):
        crawler.save(g.SOURCE, g.TYPE, url, key, content)
        g.latestIncr()


def crawl(crawler, key ,g):
    url = "http://www.itjuzi.com/company/%s" % key
    retries = 0
    retries_2 = 0
    headers={}
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0'
    headers['User-Agent'] = user_agent
    while True:
        result = crawler.crawl(url, headers=headers)
        if result['get'] == 'success':
            #logger.info(result["content"])
            try:
                process(g, crawler, url, key, result['content'])
            except Exception,ex:
                logger.exception(ex)
            break
        else:
            if result.has_key("content") is False or result["content"] is None or result["content"].strip() == "" or result["content"].find("</html>") == -1:
                continue
            d = pq(html.fromstring(result["content"]))
            title = d('head> title').text().strip()
            if title == "找不到您访问的页面":
                if retries >= 2:
                    break
                retries += 1

        retries_2 += 1
        if retries_2 > 25:
            break



def run(g, crawler):
    while True:
        if g.finish(num=25):
            return
        key = g.nextKey()
        crawl(crawler, key, g)


def start_run(concurrent_num, flag):
    while True:
        logger.info("Itjuzi company %s start...", flag)
        g = GlobalValues.GlobalValues(13030, 36001, flag)

        threads = [gevent.spawn(run, g, ItjuziCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Itjuzi company %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*50)        #30 minutes
        else:
            gevent.sleep(60*60)   #12 hour


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(1, "all")
        else:
            key = str(int(param))
            g = GlobalValues.GlobalValues(13030, 36001, "incr", back=0)
            crawl(ItjuziCrawler(), key, g)
    else:
        start_run(1, "incr")