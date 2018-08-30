# -*- coding: utf-8 -*-
import os, sys
import datetime
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db,util

#logger
loghelper.init_logger("crawler_itjuzi_news", stream=True)
logger = loghelper.get_logger("crawler_itjuzi_news")

#mongo
mongo = db.connect_mongo()

collection = mongo.raw.projectdata

MAX_PAGE_ALL = 100
MAX_PAGE_INCR = 5
CURRENT_PAGE = 1

SOURCE = 13030
TYPE = 36006

class ItjuziNewsListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, timeout=30)

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

class ItjuziNewsPageCrawler(BaseCrawler.BaseCrawler):
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
            return True
        if title.find("IT桔子") >= 0:
            return True

        return False

class ItjuziNewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)


def process_news(content, news_crawler,news_key,company_key_int,title, news_date,tags):
    d = pq(html.fromstring(content))
    actual_news_url = d("iframe").attr("src")
    if actual_news_url is None:
        return
    if not actual_news_url.startswith("http"):
        return

    logger.info("actual_news_url: %s", actual_news_url)

    retry_time = 0
    while True:
        result = news_crawler.crawl(actual_news_url, agent=True)
        if result['get'] == 'success' and result.get("code") == 200:
            #logger.info(result["content"])
            news_content = util.html_encode(result["content"])
            try:
                collection_content = {
                    "date":datetime.datetime.now(),
                    "source":SOURCE,
                    "type":TYPE,
                    "url":actual_news_url,
                    "key":news_key,
                    "key_int":int(news_key),
                    "content":news_content,
                    "company_key_int": company_key_int,
                    "title": title,
                    "news_date": news_date,
                    "original_tags":tags
                }
                collection.insert_one(collection_content)
                break
            except Exception,ex:
                #logger.exception(ex)
                pass
        retry_time += 1
        if retry_time > 10:
            break


def process(content, page_crawler, news_crawler):
    d = pq(html.fromstring(content))
    lis = d("ul.list-timeline> li")
    for li in lis:
        l = pq(li)
        try:
            title = l("span.title> a").text().strip()
            news_url = l("span.title> a").attr("href")
            news_key = news_url.split("/")[-1]
            strdate = l("span.newsdate> span").eq(0).text().strip()
            news_date = datetime.datetime.strptime(strdate, "%Y.%m.%d")
            company_url = l("span.scopes> a").attr("href")
            company_key_int = int(company_url.split("/")[-1])
            logger.info("%s %s %s %s", company_key_int, title,strdate,news_url)
            tags = []
            bs = l('span.scopes> a> b')
            for b in bs:
                s = pq(b)
                tags.append(s.text())

            if collection.find_one({"source":SOURCE, "type":TYPE, "key":news_key}) is None:
                while True:
                    result = page_crawler.crawl(news_url, agent=True)
                    if result['get'] == 'success':
                        #logger.info(result["content"])
                        try:
                            process_news(result['content'], news_crawler, news_key, company_key_int, title, news_date,tags)
                        except Exception,ex:
                            logger.exception(ex)
                        break
        except:
            continue

    #crawler.save(g.SOURCE, g.TYPE, url, key, content)


def run(flag):
    global CURRENT_PAGE
    crawler = ItjuziNewsListCrawler()
    page_crawler = ItjuziNewsPageCrawler()
    news_crawler = ItjuziNewsCrawler()

    while True:
        key = CURRENT_PAGE
        #logger.info("key=%s", key)
        if flag == "all":
            if key > MAX_PAGE_ALL:
                return
        else:
            if key > MAX_PAGE_INCR:
                return

        CURRENT_PAGE += 1
        url = "https://www.itjuzi.com/news?page=%s" % key
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    process(result['content'], page_crawler, news_crawler)
                except Exception,ex:
                    logger.exception(ex)
                break


def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("Itjuzi news %s start...", flag)
        CURRENT_PAGE = 1
        threads = [gevent.spawn(run,flag) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Itjuzi news %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*30)        #30 minutes
        else:
            return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    flag = "incr"
    #concurrent_num = MAX_PAGE_INCR
    #if concurrent_num > 5:
    #    concurrent_num = 5
    concurrent_num = 1
    if len(sys.argv) > 1:
        flag = sys.argv[1]
    if flag == "all":
        concurrent_num = 20

    start_run(concurrent_num, flag)