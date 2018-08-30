# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, time
import urllib
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey;

monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, extract, db, util, url_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../news'))
import Newscrawler
import parser_mysql_util, extractArticlePublishedDate

# logger
loghelper.init_logger("crawler_baidu_news", stream=True)
logger = loghelper.get_logger("crawler_baidu_news")

NEWSSOURCE = "baiduSearch"

URLS = []
CURRENT_PAGE = 1
# linkPattern = "cn.dailyeconomic.com/\d+/\d+/\d+/\d+.html"
Nocontents = [
]
columns = [
    {"keyword": 'A\+轮', "max": [1]},
    {"keyword": 'B\+轮', "max": [1]},
    {"keyword": "天使轮", "max": [1, 2]},
    {"keyword": "战略投资", "max": [1, 2]},
    {"keyword": "A轮", "max": [1, 2]},
    {"keyword": "B轮", "max": [1, 2]},
    {"keyword": "C轮", "max": [1, 2]},
    {"keyword": "D轮", "max": [1, 2]},
    {"keyword": "种子轮", "max": [1, 2]},
    {"keyword": "领投", "max": [1, 2]},
    {"keyword": "获投", "max": [1]},
    {"keyword": "千万 融资", "max": [1]},
    {"keyword": "债权融资", "max": [1]},

]
MAX = 2


class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=10):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout, use_proxy=1)

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

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("每日经济") >= 0:
            return True
        if title.find("Nothing") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8", "ignore")))
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
        collection_news.update_one({"_id": item["_id"]}, {'$set': {"companyId": int(companyId), "processStatus": 1},
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
            collection_news.update_one({"_id": item["_id"]}, {'$set': {"date": bdate}})
            logger.info("update date %s into %s", bdate, link)
    mongo.close()


def run_news(keyword):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawlerNews_baidu(URL["link"])


def process(content, flag, type):
    if content.find("result") >= 0:
        # logger.info(content)
        d = pq(html.fromstring(content.replace("&nbsp;", "bamy").decode("utf-8")))
        for a in d('div> div.result'):
            try:
                link = d(a)('h3> a').attr("href")
                title = "".join(d(a)('h3> a').text().split())
                # logger.info(link)
                if title is not None and title.strip() != "":
                    # logger.info("Link: %s is right news link %s", link, title)
                    # title = d(a)('h3> a').text()
                    if type == 'title':
                        ndate = d(a)('div.c-title-author').text().split("bamybamy")[1].replace("查看更多相关新闻>>", "").strip()
                    else:
                        ndate = d(a)('.c-author').text().split("bamybamy")[1].replace("查看更多相关新闻>>", "").strip()
                    newsdate = extract.extracttime(ndate)
                    newsdate = newsdate - datetime.timedelta(hours=8) if newsdate is not None else newsdate
                    # newsdate = datetime.datetime.strptime(ndate, "%Y年%m月%d日 %H:%M") - datetime.timedelta(hours=8)
                    # ndate = d(a)('div.c-title-author').text()
                    logger.info("Link: %s is right news link %s|%s|%s", link, title, ndate, type)
                    mongo = db.connect_mongo()
                    collection_news = mongo.article.news
                    item = collection_news.find_one({'$or': [{"link": link}, {'title': title}]})
                    collection_news_more = mongo.article.news_more
                    item2 = collection_news_more.find_one({'$or': [{"link": link}, {'title': title}]})
                    mongo.close()

                    if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                        linkmap = {
                            "link": link,
                            "title": title,
                            "newsdate": newsdate
                        }
                        URLS.append(linkmap)
                    else:
                        logger.info('already exists %s', title)
                    #     if item is not None:
                    #         add_companyIds(item["link"], companyId)
                    #         add_newsdate(item["link"], newsdate)
                    #     elif item2 is not None:
                    #         add_companyIds(item2["link"], companyId)
                    #         add_newsdate(item2["link"], newsdate)
                else:
                    pass
            except Exception, e:
                logger.info(e)
                logger.info("cannot get link")
    return len(URLS)


def run(flag, column, listcrawler, newscrawler):
    global CURRENT_PAGE
    cnt = 1
    keyword = column['keyword']
    for type in ['focus', 'time', 'title']:
        CURRENT_PAGE = 1
        while True:
            key = CURRENT_PAGE

            if flag == "all":
                if key > MAX:
                    break
            else:
                if cnt == 0 or key > MAX:
                    break

            CURRENT_PAGE += 1

            # keyword =urllib.urlencode({"s":column["column"]})

            if type == 'focus':
                # 按焦点排序
                url = "http://news.baidu.com/ns?word=%s&pn=%s&cl=2&ct=1&tn=news&rn=20&ie=utf-8&bt=0&et=0&rsv_page=1" % (
                    keyword, (key - 1) * 20)
            elif type == 'time':
                # 按时间排序
                url = "http://news.baidu.com/ns?word=%s&pn=%s&cl=2&ct=0&tn=news&rn=20&ie=utf-8&bt=0&et=0" % (
                    keyword, (key - 1) * 20)
            elif type == 'title':
                # 标题搜索
                url = "http://news.baidu.com/ns?word=%s&pn=%s&cl=2&ct=0&tn=newstitle&rn=20&ie=utf-8&bt=0&et=0" % (
                    keyword, (key - 1) * 20)

            while True:
                result = listcrawler.crawl(url, agent=True)
                if result['get'] == 'success':
                    try:
                        cnt = process(result['content'], flag, type)
                        if cnt > 0:
                            logger.info("%s has %s fresh news", url, cnt)
                            logger.info(URLS)

                            # run_news(companyId, keyword)
                            threads = [gevent.spawn(run_news, keyword) for i in
                                       xrange(5)]
                            gevent.joinall(threads)
                            # exit()
                    except Exception, ex:
                        logger.exception(ex)
                        cnt = 0
                    break


def start_run(flag, columns):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler)

        logger.info("%s news %s end...", NEWSSOURCE, flag)
        time.sleep(60*30)


class NewsDownloader:
    def __init__(self, TYPE=60005, SOURCE=13901, RETRY=20, CATEGORY=None, FORCE=False):
        self.TYPE = TYPE
        self.SOURCE = SOURCE
        self.RETRY = RETRY
        self.CATEGORY = CATEGORY
        self.FORCE = FORCE

    def has_news_content(self, content):
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        if len(title) > 0 and title.find("404") == -1:
            return True
        else:
            return False

    def process_news(self, newsurl, content, download_crawler):
        if self.has_news_content(content):
            try:
                d = pq(html.fromstring(content.decode("utf-8")))
            except:
                d = pq(html.fromstring(content))

            key = newsurl.split("/")[-1].replace(".shtml", "").replace(".html", "")
            try:
                key_int = int(key)
            except:
                key_int = None

            news_time = extractArticlePublishedDate.extractArticlePublishedDate(newsurl, content)
            if news_time is None:
                news_time = datetime.datetime.now()

            title = extract.extractTitle(content)

            contents = extract.extractContents(newsurl, content)

            tags = []
            try:
                articletags = d("meta[name='keywords']").attr("content")
                if articletags is not None:
                    for tag in articletags.split():
                        if tag is not None and tag.strip() != "" and tag not in tags and tag != title:
                            tags.append(tag)
            except:
                pass

            logger.info("News: %s, %s, %s", key, title, news_time)

            # mongo = db.connect_mongo()
            # collection_news = mongo.article.news
            # if collection_news.find_one({"link": newsurl}) is not None:
            #     mongo.close()
            #     return

            flag, domain = url_helper.get_domain(newsurl)
            dnews = {
                "date": news_time - datetime.timedelta(hours=8),
                "title": title,
                "link": newsurl,
                "createTime": datetime.datetime.now(),
                "source": self.SOURCE,
                "key": key,
                "key_int": key_int,
                "type": self.TYPE,
                "original_tags": tags,
                "processStatus": 0,
                # "companyId": None,
                "companyIds": [],
                "category": self.CATEGORY,
                "domain": domain,
                "categoryNames": []
            }
            dcontents = []
            rank = 1
            for c in contents:

                if c["type"] == "text":
                    dc = {
                        "rank": rank,
                        "content": c["data"],
                        "image": "",
                        "image_src": "",
                    }
                else:
                    if download_crawler is None:
                        dc = {
                            "rank": rank,
                            "content": "",
                            "image": "",
                            "image_src": c["data"],
                        }
                    else:
                        # imgurl = parser_mysql_util.get_logo_id(c["data"], download_crawler, self.SOURCE, key, "news")
                        (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler,
                                                                                    self.SOURCE,
                                                                                    key, "news")
                        if imgurl is not None:
                            dc = {
                                "rank": rank,
                                "content": "",
                                "image": str(imgurl),
                                "image_src": "",
                                "height": int(height),
                                "width": int(width)
                            }
                        else:
                            continue

                logger.info(c["data"])
                dcontents.append(dc)
                rank += 1
            dnews["contents"] = dcontents

            brief = util.get_brief_from_news(dcontents)
            post = util.get_poster_from_news(dcontents)
            if download_crawler is None:
                dnews["post"] = post
            else:
                dnews["postId"] = post
            dnews["brief"] = brief

            # if news_time > datetime.datetime.now() or news_time < datetime.datetime.now() - datetime.timedelta(days=30):
            #     logger.info("Time: %s is not correct with current time", news_time)
            #     dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)

            if news_time > datetime.datetime.now():
                logger.info("Time: %s is not correct with current time", news_time)
                dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
            if len(dnews["contents"]) > 2:
                mongo = db.connect_mongo()
                collection_news = mongo.article.news_more
                nid = collection_news.insert(dnews)
                mongo.close()
                # nid = parser_mongo_util.save_mongo_news(dnews)
                logger.info("Done: %s", nid)
            logger.info("*************DONE*************")

    def crawler_news(self, crawler, newsurl, download_crawler=None):
        retry = 0
        while True:
            # headers = {"Cookie": "_ga=fff"}
            result = crawler.crawl(newsurl, agent=True)
            if result['get'] == 'success' and result.get("code") == 200:
                # logger.info(result["redirect_url"])
                try:
                    self.process_news(newsurl, result['content'], download_crawler)
                    return {"result": "SUCCESS"}
                except Exception, ex:
                    logger.exception(ex)
                    return {"result": "FAILED"}

            if retry > self.RETRY:
                return {"result": "FAILED"}
            retry += 1


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        # if title.find("页面未找到404") >= 0:
        #     return False
        # if title.find("您所请求的网址（URL）无法获取") >= 0:
        #     return False
        # if title.find("403 Forbidden") >= 0:
        #     return False
        # if title.find("ERROR: The requested URL could not be retrieved") >= 0:
        #     return False
        # if content.find("421 Server too busy") >= 0:
        #     return False
        # if content.find("铅笔道") >= 0:
        #     return True
        # return False
        return True


def crawlerNews_baidu(link, pdate=None):
    # download_crawler = download.DownloadCrawler(use_proxy=False)
    download_crawler = None
    print 'user here'
    crawler = NewsDownloader()
    result = crawler.crawler_news(NewsCrawler(), link, download_crawler)
    logger.info(result)


if __name__ == "__main__":
    start_run("incr", columns)