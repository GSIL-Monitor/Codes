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
loghelper.init_logger("crawler_itjuzi_investfirm", stream=True)
logger = loghelper.get_logger("crawler_itjuzi_investfirm")


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
        if title.find("IT桔子") >= 0:
            return True

        return False


def has_content(content):
    d = pq(html.fromstring(content))
    investfirm_name = d('div.infohead-group> div> div> p> span.title').text().strip()
    logger.info("investfirm_name: " + investfirm_name)

    if investfirm_name != "":
        return True
    return False


def process(g, crawler, url, key, content):
    if has_content(content):
        crawler.save(g.SOURCE, g.TYPE, url, key, content)
        g.latestIncr()


def run(g, crawler):
    while True:
        if g.finish(num=25):
            return
        key = g.nextKey()
        url = "https://www.itjuzi.com/investfirm/%s" % key
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    process(g, crawler, url, key, result['content'])
                except Exception,ex:
                    logger.exception(ex)
                break


def start_run(concurrent_num, flag):
    while True:
        logger.info("Itjuzi investfirm %s start...", flag)
        g = GlobalValues.GlobalValues(13030, 36003, flag)

        threads = [gevent.spawn(run, g, ItjuziCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Itjuzi investfirm %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*50)        #30 minutes
        else:
            gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    start_run(1, "incr")