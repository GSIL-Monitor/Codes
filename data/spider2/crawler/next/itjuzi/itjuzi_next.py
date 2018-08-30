# -*- coding: utf-8 -*-
import os, sys
import datetime
import urllib
from lxml import html
from pyquery import PyQuery as pq
import gevent
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
loghelper.init_logger("crawler_itjuzi_next", stream=True)
logger = loghelper.get_logger("crawler_itjuzi_next")


class ItjuziNextCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self, url, content):
        if not content.startswith('<div class="day"'):
            return False
        if content.find('<a href="javascript:">更多</a>') == -1:
            return False
        return True


class ItjuziNextURLCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)


crawler_url = ItjuziNextURLCrawler()
def get_actual_url(url):
    while True:
        result = crawler_url.crawl(url,redirect=False)
        if result['get'] == 'redirect':
            if result["url"] != url:
                actual = result["url"]
                return actual
            else:
                #logger.info(result["redirect_url"])
                pass

def process(g, crawler, url, content):
    today = datetime.datetime.today()
    date_str = "%s-%02d-%02d" % (today.year, today.month, today.day)
    #logger.info(date_str)
    d = pq(html.fromstring(content.decode("utf-8")))
    divs = d('div.day[date="%s"]> div.media.col-sm-12' % date_str)
    for div in divs:
        d = pq(div)
        a = d("div.row> div> h4> strong> a")
        name = a.text().strip()
        href= a.attr("href").strip()
        website = get_actual_url(href)
        score = int(d("a> div.media-object> strong").text())
        desc = d("div.row> div> p").text().strip()
        logger.info("name: %s, href: %s, score: %s", name, href, score)
        #logger.info(desc)
        data = {
                "name":name,
                "website":website,
                "score":score,
                "desc":desc}
        key = href.split("/")[-1]
        url = "http://today.itjuzi.com/product/comment_info/%s" % key
        crawler.save(g.SOURCE, g.TYPE, url, key, data)


def run(g, crawler):
    url = "http://today.itjuzi.com/product/getday"
    headers = {"Content-Type":"application/x-www-form-urlencoded"}
    data = {"start":0}

    while True:
        postdata = urllib.urlencode(data)
        result = crawler.crawl(url, headers=headers, postdata=postdata)
        if result['get'] == 'success':
            process(g, crawler, url, result['content'])
            break


def start_run():
    while True:
        logger.info("Itjuzi next start...")
        g = GlobalValues.GlobalValues(13031, 36009, "incr")
        thread = gevent.spawn(run, g, ItjuziNextCrawler())
        thread.join()

        logger.info("Itjuzi next end.")

        gevent.sleep(60*30)        #30 minutes

if __name__ == "__main__":
    start_run()