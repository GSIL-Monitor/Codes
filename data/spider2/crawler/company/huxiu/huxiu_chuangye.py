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
loghelper.init_logger("crawler_huxiu_chuangye", stream=True)
logger = loghelper.get_logger("crawler_huxiu_chuangye")


class HuxiuCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        if title.find("虎嗅网") >= 0:
            return True
        return False

def has_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    temp = title.split("-")
    if len(temp) != 2:
        return False
    if temp[1].strip() != "虎嗅网":
        return False
    if temp[0].strip() == "":
        return False
    return True

def process(g, crawler, url, key, content):
    if has_content(content):
        crawler.save(g.SOURCE, g.TYPE, url, key, content)
        g.latestIncr()

def run(g, crawler, key=None):
    if key is None:
        if g.finish():
            return
        key = g.nextKey()

    url = "http://www.huxiu.com/chuangye/product/%s" % key
    result = crawler.crawl(url)

    if result['get'] == 'success':
        process(g, crawler, url, key, result['content'])
        gevent.spawn(run, g, crawler)
    else:
        gevent.spawn(run, g, crawler, key)


def start_run(concurrent_num, flag):
    while True:
        logger.info("Huxiu chuangye start...")
        g = GlobalValues.GlobalValues(13041, 36001, flag)
        for i in range(concurrent_num):
            gevent.spawn(run, g, HuxiuCrawler())
        g.wait()
        logger.info("Huxiu chuangye end.")

        if flag == "incr":
            gevent.sleep(60*30)        #30 minutes
        else:
            gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    start_run(10, "incr")