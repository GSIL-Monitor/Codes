# -*- coding: utf-8 -*-
import os, sys, datetime, re, json
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
import loghelper,extract,db, util,url_helper,download, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_zhidx_news", stream=True)
logger = loghelper.get_logger("crawler_zhidx_news")

NEWSSOURCE = "Zhidx"
RETRY = 3
TYPE = 60001
SOURCE =13830
URLS = []
CURRENT_PAGE = 1
linkPattern = "/p/\d+.html"
Nocontents = [
]
columns = [
    {"column": "news", "max": 1, "category": None},
    {"column": "vanguard", "max": 2, "category": 60102},
    {"column": "report", "max": 2, "category": 60003},
    {"column": "daily", "max": 2, "category": 60105},
    {"column": "kuwan", "max": 2, "category": None},
    {"column": "review", "max": 2, "category": None},
    {"column": "huodong", "max": 2, "category": None},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("智东西") >= 0:
            return True
        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=20):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    #实现<div class="tabCont
    def is_crawl_success(self,url,content):

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("智东西") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    temp = title.split("|")
    if len(temp) < 2:
        return False
    if temp[0].strip() == "":
        return False
    return True


def process_news(column, newsurl, content, newspost, download_crawler):
    if has_news_content(content):
        d = pq(html.fromstring(content.decode("utf-8")))

        key = newsurl.split("/")[-1].replace(".html","")

        type = TYPE
        categoryNames = []

        if column["category"] == 60003: type = 60003; category = 60107
        else: category = column["category"]

        if category == 60102: categoryNames.append("产品")
        if category == 60105: categoryNames.append("大公司")

        title = d('div.finTit> h1').text().strip()

        tags = []
        articletags = d("div.finTit> p> em.leibie> a").text()
        # logger.info(articletags)
        if articletags is not None:
            for tag in articletags.split():
                if tag is not None and tag.strip() != "" and tag not in tags and tag != title:
                    tags.append(tag)

        # post = d('div#post_thumbnail> img').attr("src")
        # posturl = parser_mysql_util.get_logo_id(newspost, download_crawler, SOURCE, key, "news")
        # if posturl is not None:
        #     post = str(posturl)
        # else:
        #     post = None

        postraw = newspost
        # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        brief = d("div.finAbstract").text().strip().replace('[&hellip;]',"").replace(' […]',"")

        post_time = d('div.finTit> p> em.time').text().replace("/","-")
        logger.info(post_time)
        # news_time = extract.extracttime(post_time)
        # try:
        #     news_time = datetime.datetime.strptime(str(datetime.date.today().year) + "年"+ post_time, "%Y年%m月%d日 %H:%M")
        # except:
        if post_time == str(datetime.date.today()):news_time = datetime.datetime.now()
        else: news_time = datetime.datetime.strptime(post_time, "%Y-%m-%d")

        article = d('div.article> div.finCnt').html()
        contents = extract.extractContents(newsurl, article)

        logger.info("%s, %s, %s, %s -> %s, %s. %s", key, title, news_time, ":".join(tags), category, brief, post)
        # exit()
        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        if collection_news.find_one({"title": title}) is not None:
            mongo.close()
            return

        flag, domain = url_helper.get_domain(newsurl)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": newsurl,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": int(key),
            "type": type,
            "original_tags": tags,
            "processStatus": 0,
            # "companyId": None,
            "companyIds": [],
            "category": category,
            "domain": domain,
            # "sectors": [20]
            "categoryNames": categoryNames
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
                    (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler, SOURCE, key, "news")
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

            # logger.info(c["data"])
            dcontents.append(dc)
            rank += 1
        dnews["contents"] = dcontents
        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        if post is None or post.strip() == "":
            post = util.get_posterId_from_news(dcontents)

        if download_crawler is None:
            dnews["post"] = post
        else:
            dnews["postId"] = post
        dnews["brief"] = brief

        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)

        if len(dcontents)>1:
            # collection_news.insert(dnews)
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s", nid)
        mongo.close()
        # logger.info("*************DONE*************")
    return


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL["post"], download_crawler)

def crawler_news(column, crawler, newsurl, newspost, download_crawler):
    while True:
        result = crawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'], newspost, download_crawler)
            except Exception,ex:
                logger.exception(ex)
            break



def process(content, flag):
    d = pq(html.fromstring(content.decode("utf-8")))
    for li in d('div.tabCont> ul> li'):
        try:
            link = d(li)('a').attr("href").strip()
            # logger.info(link)
            if re.search(linkPattern, link) and link.find("http")>=0:
                logger.info("Link: %s is right news link", link)
                title = d(li)('p.name> a').text()
                logger.info("title: %s", title)
                post = d(li)('a> img').attr("src").strip()
                # check mongo data if link is existed
                mongo = db.connect_mongo()
                collection_news = mongo.article.news
                item = collection_news.find_one({"link": link})
                item2 = collection_news.find_one({"title": title})
                mongo.close()

                if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                    linkmap = {
                        "link": link,
                        "post": post
                    }
                    URLS.append(linkmap)

            else:
                # logger.info(link)
                pass
        except Exception, e:
            logger.info(e)
            logger.info("cannot get link")
    return len(URLS)


def run(flag, column, listcrawler, newscrawler, concurrent_num, download_crawler):
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
        if key == 1:
            if column["column"] == "news":
                url = "http://zhidx.com/"
            else:
                url = "http://zhidx.com/p/category/%s" % (column["column"])
        else:
            url = "http://zhidx.com/p/category/%s/page/%s" % (column["column"], key)
        while True:
            result = listcrawler.crawl(url,agent=True)

            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        threads = [gevent.spawn(run_news, column, newscrawler, download_crawler) for i in xrange(concurrent_num)]
                        gevent.joinall(threads)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break



def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        download_crawler = download.DownloadCrawler(use_proxy=False)
        #download_crawler = None
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num, download_crawler)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            gevent.sleep(60*8)        #30 minutes
        else:
            return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(1, "all")
        else:
            link = param
            # download_crawler = download.DownloadCrawler(use_proxy=False)
            download_crawler = None
            crawler_news({"column": "vanguard", "max": 2, "category": 60102}, NewsCrawler(), link, "http://zhidx.com/wp-content/uploads/2016/12/tcl-h9700-quantum-dot-4k-tv-300x200.jpg", download_crawler)
    else:
        start_run(1, "incr")