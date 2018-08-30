# -*- coding: utf-8 -*-
import os, sys
from BaseCrawler import BaseCrawler
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper

#logger
loghelper.init_logger("crawler_chuangyepu_company", stream=True)
logger = loghelper.get_logger("crawler_chuangyepu_company")

SOURCE = 13040  #创业铺
TYPE = 36001    #公司信息

class ChuangyepuCrawler(BaseCrawler):
    def __init__(self, start):
        BaseCrawler.__init__(self)
        self.page = start
        self.isEnd = False

    def get_page_url(self):
        url = "http://chuangyepu.com/search/startups?key_word=&page=%s" % self.page
        self.page += 1
        return url

    def get_url(self):
        return None

    #实现
    def has_page_content(self, r):
        d = pq(r.text)
        text_error = d('p.text-error').text().strip()

        if text_error != "很抱歉，创业谱没有为您找到相关条目。":
            return True
        return False

    def page_process(self, r):
        urls = []
        if r is None:
            logger.info("Fail to get page content")
        else:
            if self.has_page_content(r):
                #logger.info(r.text)
                d = pq(r.text)
                divs = d('div.caption')
                for div in divs:
                    l = pq(div)
                    name = l("div.name> a").text().strip()
                    url = "http://chuangyepu.com" + l("div.name> a").attr("href").strip()
                    u = {"name":name,"url":url}
                    urls.append(u)
            else:
                self.isEnd = True

        return urls

    def process(self, url, r):
        if r is None:
            logger.info("Fail to get content")
            return
        key = url.split("/")[-1]
        self.save(SOURCE, TYPE, url, key, r.text)

    def is_end(self):
        return self.isEnd


if __name__ == "__main__":
    logger.info("Start...")

    start = 1
    t = ChuangyepuCrawler(start)

    while True:
        page_url = t.get_page_url()
        r = t.crawl(page_url)
        urls = t.page_process(r)

        for u in urls:
            name = u["name"]
            url = u["url"]
            logger.info(name)
            logger.info(url)
            r = t.crawl(url)
            t.process(url, r)

        if t.is_end():
            break

    logger.info("End.")
