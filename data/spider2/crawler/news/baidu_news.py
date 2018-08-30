# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, time
import urllib
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../news'))
import Newscrawler

#logger
loghelper.init_logger("crawler_baidu_news", stream=True)
logger = loghelper.get_logger("crawler_baidu_news")

NEWSSOURCE = "baiduSearch"

URLS = []
CURRENT_PAGE = 1
# linkPattern = "cn.dailyeconomic.com/\d+/\d+/\d+/\d+.html"
Nocontents = [
]
columns = [
    # {"column": "jmd", "max": 2},
    {"column": "foucs", "max": 2},
    # {"column": "title", "max": 1},

]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=10):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

        # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("百度") >= 0:
            return True
        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
           return False

        d = pq(html.fromstring(content.decode("utf-8","ignore")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("每日经济") >= 0:
            return True
        if title.find("Nothing") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8","ignore")))
    title = d('head> title').text().strip()
    temp = title.split("|")
    logger.info("title:%s %s", title, len(temp))
    if len(title) == 0 or title == "":
        return False
    return True

def add_companyIds(link, companyId):
    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    item = collection_news.find_one({"link": link})
    # logger.info("companyId:%s", companyId)
    if item is not None and item.has_key("companyIds") and companyId not in item["companyIds"]:
        collection_news.update_one({"_id": item["_id"]}, {'$set': {"companyId":int(companyId), "processStatus":1},
                                                          '$addToSet': {"companyIds": int(companyId)}})
        logger.info("add companyId %s into %s", companyId, link)
    mongo.close()

def add_newsdate(link, bdate):
    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    item = collection_news.find_one({"link": link})
    # logger.info("companyId:%s", companyId)
    if item is not None and item.has_key("source") and item["source"] == 13900:
        if item["date"] > bdate:
            collection_news.update_one({"_id": item["_id"]}, {'$set': {"date":bdate}})
            logger.info("update date %s into %s", bdate, link)
    mongo.close()

def run_news(companyId, keyword):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        Newscrawler.crawlerNews(URL["link"])
        if companyId is not None:
            add_companyIds(URL["link"], companyId)
            add_newsdate(URL["link"], URL["newsdate"])



def process(content, flag, companyId):
    if content.find("result") >= 0:
        # logger.info(content)
        d = pq(html.fromstring(content.replace("&nbsp;","bamy").decode("utf-8")))
        for a in d('div> div.result'):
            try:
                link = d(a)('h3> a').attr("href")
                title = "".join(d(a)('h3> a').text().split())
                # logger.info(link)
                if title is not None and title.strip() != "":
                    # logger.info("Link: %s is right news link %s", link, title)
                    # title = d(a)('h3> a').text()
                    ndate = d(a)('div.c-title-author').text().split("bamybamy")[1].replace("查看更多相关新闻>>","").strip()
                    newsdate = datetime.datetime.strptime(ndate, "%Y年%m月%d日 %H:%M") - datetime.timedelta(hours=8)
                    # ndate = d(a)('div.c-title-author').text()
                    logger.info("Link: %s is right news link %s|%s", link, title,ndate)
                    mongo = db.connect_mongo()
                    collection_news = mongo.article.news
                    item = collection_news.find_one({"link": link})
                    item2 = collection_news.find_one({"title": title})
                    mongo.close()

                    if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                        linkmap = {
                            "link": link,
                            "title": title,
                            "newsdate":  newsdate
                        }
                        URLS.append(linkmap)
                    else:
                        if item is not None:
                            add_companyIds(item["link"], companyId)
                            add_newsdate(item["link"], newsdate)
                        elif item2 is not None:
                            add_companyIds(item2["link"], companyId)
                            add_newsdate(item2["link"], newsdate)
                else:
                    # logger.info(link)
                    pass
            except Exception, e:
                logger.info(e)
                logger.info("cannot get link")
    return len(URLS)


def run(flag, column, listcrawler, newscrawler, keyword, companyId):
    global CURRENT_PAGE
    cnt = 1
    while True:
        key = CURRENT_PAGE

        if flag == "all":
            if key > column["max"]:
                return
        else:
            if cnt == 0 or key > column["max"]:
                return

        CURRENT_PAGE += 1

        # keyword =urllib.urlencode({"s":column["column"]})
        url = "http://news.baidu.com/ns?word=%s&pn=%s&cl=2&ct=0&tn=newstitle&rn=20&ie=utf-8&bt=0&et=0" % (keyword, (key-1)*20)
        while True:
            result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag, companyId)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)

                        # run_news(companyId, keyword)
                        threads = [gevent.spawn(run_news, companyId, keyword) for i in
                                   xrange(5)]
                        gevent.joinall(threads)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break



def start_run(flag, keycolums, keyword, companyId):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        for column in keycolums:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, keyword, companyId)

        break

if __name__ == "__main__":
    start_run("incr", columns, "聚财猫", 13774)