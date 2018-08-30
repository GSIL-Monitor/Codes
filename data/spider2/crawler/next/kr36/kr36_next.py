# -*- coding: utf-8 -*-
import os, sys
import datetime
import urllib
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
loghelper.init_logger("crawler_36kr_next", stream=True)
logger = loghelper.get_logger("crawler_36kr_next")


class Kr36NextCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self, url, content):
        if content.find('OK, NEXT') == -1:
            return False
        return True


class Kr36NextDetailCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self, url, content):
        if content.find('评论加载中..') == -1:
            return False
        return True

class Kr36NextUrlCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)


crawler_url = Kr36NextUrlCrawler()
def get_actual_url(url):
    while True:
        result = crawler_url.crawl(url,redirect=False)
        if result['get'] == 'redirect':
            if result["url"] != url:
                actual = result["url"]
                actual = actual.replace("?utm_source=next.36kr.com","")
                actual = actual.replace("&utm_source=next.36kr.com","")
                return actual
            else:
                #logger.info(result["redirect_url"])
                pass


def process_detail(g, crawler, url, key, content):
    d = pq(html.fromstring(content.decode("utf-8")))
    name = d('div.product-url> a').text().strip()
    website = "http://next.36kr.com" + d('div.product-url> a').attr("href").strip()
    website = get_actual_url(website)
    score = int(d('div.upvote> a> span').text().strip())
    desc = d('span.post-tagline').text().strip()
    logger.info("name: %s, website: %s, score: %s", name, website, score)
    #logger.info(desc)
    ps = d('li.product-mark')
    url_ios = None
    url_android = None
    for p in ps:
        d= pq(p)
        if d('i.mark-ios').attr("class") is not None:
            url_ios = d('a.hoverable').attr("href")
            if url_ios is not None:
                url_ios = get_actual_url(url_ios.strip())
                logger.info("url_ios: %s", url_ios)

        if d('i.mark-android').attr("class") is not None:
            url_android = d('a.hoverable').attr("href")
            if url_android is not None:
                url_android = get_actual_url(url_android.strip())
                logger.info("url_android: %s", url_android)
    data = {
        "name": name,
        "website": website,
        "score": score,
        "desc": desc,
        "url_ios": url_ios,
        "url_android": url_android
    }

    crawler.save(g.SOURCE, g.TYPE, url, key, data)

def run_detail(g, crawler, _id):
    url = "http://next.36kr.com/posts/%s" % _id

    while True:
        result = crawler.crawl(url)
        if result['get'] == 'success':
            process_detail(g, crawler, url, _id, result['content'])
            break


def process(g, content):
    detail_crawler = Kr36NextDetailCrawler()

    today = datetime.datetime.today()
    date_str = u"%s年%d月%02d日" % (today.year, today.month, today.day)
    #logger.info(date_str)
    d = pq(html.fromstring(content.decode("utf-8")))
    divs = d('section.post')
    for div in divs:
        d = pq(div)
        date = d("div.date").attr("title").strip()
        if date != date_str:
            continue

        items = d("div.upvote")
        for item in items:
            d = pq(item)
            _id = d.attr("data-note-id").strip()
            logger.info("id: %s", _id)
            run_detail(g, detail_crawler, _id)


def run(g, crawler):
    url = "http://next.36kr.com/posts"

    while True:
        result = crawler.crawl(url)
        if result['get'] == 'success':
            process(g, result['content'])
            break


def start_run():
    while True:
        logger.info("36kr next start...")
        g = GlobalValues.GlobalValues(13021, 36009, "incr")
        thread = gevent.spawn(run, g, Kr36NextCrawler())
        thread.join()
        logger.info("36kr next end.")

        gevent.sleep(60*30)        #30 minutes

if __name__ == "__main__":
    start_run()