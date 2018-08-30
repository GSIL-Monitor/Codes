# -*- coding: utf-8 -*-
import os, sys
from BaseCrawler import BaseCrawler
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper

#logger
loghelper.init_logger("crawler_itjuzi_investfirm", stream=True)
logger = loghelper.get_logger("crawler_itjuzi_investfirm")

SOURCE = 13030  #ITJUZI
TYPE = 36003    #投资公司

class ItjuziCrawler(BaseCrawler):
    def __init__(self, start):
        BaseCrawler.__init__(self,header=True)
        self.set_start(start)

    def set_start(self, start):
        self.current = start
        self.latest = start

    def get_url(self):
        key = str(self.current)
        url = "https://itjuzi.com/investfirm/%s" % key
        self.current += 1
        return (url, key)

    #实现
    def is_crawl_success(self,r):
        d = pq(r.text)
        title = d('head> title').text().strip()
        logger.info("title: " + title)
        if title.find("IT桔子") > 0:
            return True
        return False

    def has_content(self, r):
        d = pq(r.text)
        investfirm_name = d('div.infohead-group> div> div> p> span.title').text().strip()
        logger.info("investfirm_name: " + investfirm_name)

        if investfirm_name != "":
            return True
        return False

    def process(self, url, key, r):
        if r == None:
            logger.info("Fail to get content")
            return

        #logger.info(r.text)

        if self.has_content(r):
            self.save(SOURCE, TYPE, url, key, r.text)
            self.latest = self.current-1

    def is_end(self):
        if self.latest < self.current - 50:
            return True
        return False


if __name__ == "__main__":
    logger.info("Start...")

    flag = "incr"
    if len(sys.argv) > 1:
        flag = sys.argv[1]

    start = 958
    t = ItjuziCrawler(start)

    if flag == "incr":
        latest = t.get_latest_key_int(SOURCE, TYPE)
        if latest is not None:
            start = latest + 1
            t.set_start(start)

    while True:
        (url, key) = t.get_url()
        r = t.crawl(url)
        t.process(url, key, r)

        if t.is_end():
            break

    logger.info("End.")