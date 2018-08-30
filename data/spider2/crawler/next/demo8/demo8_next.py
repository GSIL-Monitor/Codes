# -*- coding: utf-8 -*-
import os, sys, re
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
loghelper.init_logger("crawler_demo8_next", stream=True)
logger = loghelper.get_logger("crawler_demo8_next")

PRODUCTS=[]

class Demo8Crawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self, url, content):
        if content.find('<h3 class="fl">今天</h3>') == -1:
            return False
        return True

class Demo8DetailCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self, url, content):
        if content.find('class="detail_main"') == -1:
            return False
        return True

class Demo8NextUrlCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content.find('var url =') == -1:
            return False
        return True

crawler_url = Demo8NextUrlCrawler()

def get_actual_url(url):
    while True:
        result = crawler_url.crawl(url)
        if result['get'] == 'success':
            content = result['content']
            pattern = re.compile('var url =\s\'(.*)\'')
            actual = re.search(pattern, content)
            if actual:
                return actual.group(1)
            else:
                pass


def process_detail(g, crawler, url, content):
    d = pq(html.fromstring(content.decode("utf-8")))
    name = d('div.detail_main> div> div> h3> a').text().strip()
    desc = d('div.detail_main> div> div> p.demo_info').text().strip()
    key = int(d('span.demo_laud_ico').text())
    score = int(d('span.demo_laud_num').text())
    website = "http://www.demo8.com/demo/%s" % key
    website = get_actual_url(website)
    #imgurl = d('div.swiper-slide> img').attr("src")
    tags = d('div.classify').text().strip().replace(" ",",")
    logger.info("key: %s, name: %s, desc: %s, score: %s, website: %s, tags: %s", key, name, desc, score, website, tags)
    ps = d('div.weixin_info')
    url_app = None
    url_ios = None
    url_android = None
    for p in ps:
        d = pq(p)
        if d('img.app_qrcode_img').attr("data-src") is not None:
            url_app = d('img.app_qrcode_img').attr("data-src")
            url_app = url_app.replace("http://qr.liantu.com/api.php?text=","")

            if url_app.find('itunes.apple.com') >= 0:
                url_ios = url_app
            else:
                url_android =  url_app
    logger.info("name: %s, url: %s, ios_app: %s, android_app: %s", name, url, url_ios, url_android)
    data = {
        "name": name,
        "website": website,
        "score": score,
        "desc": desc,
        "tags": tags,
        "url_ios": url_ios,
        "url_android": url_android
    }
    crawler.save(g.SOURCE, g.TYPE, url, key, data)

def run_detail(g, crawler, _url=None):
    if _url is None:
        if len(PRODUCTS) == 0:
            g.EVENT.set()
            return
        _url = PRODUCTS.pop(0)

    result = crawler.crawl(_url)

    if result['get'] == 'success':
        process_detail(g, crawler, _url, result['content'])
        gevent.spawn(run_detail, g, crawler)
    else:
        #run_detail(1, Demo8DetailCrawler(), _url)
        gevent.spawn(run_detail, g, crawler, _url)



def process(g, content):
    today = datetime.datetime.today()
    date_str = u"%02d月%02d日" % (today.month, today.day)
    logger.info(date_str)
    d = pq(html.fromstring(content.decode("utf-8")))
    divs = d("div.data_list")
    for div in divs:
        d = pq (div)

        date = d("div.date_tit> span.small_time").text().strip()
        if date != date_str:
            continue

        lis = d('li.data_row_li')
        for li in lis:
            d = pq(li)
            _url = d("a.demo_url_pos").attr("href").strip()
            logger.info("url: %s", _url)
            PRODUCTS.append(_url)
            #run_detail(1, Demo8DetailCrawler(), _url)

    for i in range(concurrent_num):
        gevent.spawn(run_detail, g, Demo8DetailCrawler())

def run(g, crawler):
    url = "http://www.demo8.com"
    result = crawler.crawl(url)

    if result['get'] == 'success':
        process(g, result['content'])
    else:
        #run(1, Demo8Crawler())
        gevent.spawn(run, g, crawler)


def start_run():
    while True:
        logger.info("Demo8 next start...")
        g = GlobalValues.GlobalValues(13110, 36009, "incr")
        gevent.spawn(run, g, Demo8Crawler())
        #run(1, Demo8Crawler())
        g.wait()
        logger.info("Demo8 next end.")

        gevent.sleep(60*30)        #30 minutes

concurrent_num = 1
if __name__ == "__main__":
    start_run()