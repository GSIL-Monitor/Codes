# -*- coding: utf-8 -*-
import os, sys, time
import datetime
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db,util,extract,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_tuopu_news", stream=True)
logger = loghelper.get_logger("crawler_tuopu_news")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

MAX_PAGE_ALL = 55
MAX_PAGE_INCR = 3
CURRENT_PAGE = 1

SOURCE = 13807

class TuopuNewsListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("拓扑社") >= 0:
            return True

        return False

class TuopuNewsPageCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("拓扑社") >= 0:
            return True
        return False

def has_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    temp = title.split("|")
    if temp[-1].strip() != "拓扑社":
        return False
    if temp[0] == "为找到页面":
        return False
    return True


def process_news(content, url):
    if has_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        d = pq(html.fromstring(content))

        title = d('section#page-content> div> h2').text().strip()
        post_time = d('section#page-content> div> div> span.date-bayside> a> time.entry-date').attr("datetime").split("+")[0]
        news_time = datetime.datetime.strptime(post_time, "%Y-%m-%dT%H:%M:%S")
        key = None
        column = d('section#page-content> div> h6> a').text()
        categoryNames = []
        if column is not None:
            tags = column.split()
        else:
            tags = []
        if "拓·海外" in tags or "拓·真经" in tags:
            TYPE = 60003
            category = 60107
        else:
            TYPE = 60001
            if "投资人说" in tags:
                category = 60104
                categoryNames.append("投资人观点")
            elif "拓扑日报" in tags:
                category = 60101
                categoryNames.append("汇总性新闻")
            else:
                category = None

        tagsmore = d('section#page-content> div.tags-bayside').text().strip().split()
        for a in tagsmore:
            if a not in tags:
                tags.append(a)
        logger.info("%s, %s, %s, %s, %s, %s", key, title, news_time, TYPE, category, ":".join(tags))
        article = d('section#page-content> div').eq(0).html()
        #logger.info(article)
        contents = extract.extractContents(url, article)
        #
        if collection_news.find_one({"link": url}) is not None:
            return
            # collection_news.delete_one({"link": url})

        if collection_news.find_one({"title": title, "source": {"$ne": SOURCE}}) is not None:
            return
            # collection_news.delete_many({"title": title, "source": {"$ne": SOURCE}})
        # for t in contents:
        #    logger.info(t["data"])
        #    logger.info("")
        flag, domain = url_helper.get_domain(url)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": url,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": None,
            "type": TYPE,
            "original_tags": tags,
            "processStatus": 0,
            # "companyId": None,
            "companyIds": [],
            "category": category,
            "domain": domain,
            "categoryNames": categoryNames
        }
        dcontents = []
        article_img = d('section#page-content> div> div.featured-media> a').attr("href")
        if article_img is not None:
            dc = {
                "rank": 1,
                "content": "",
                "image": "",
                "image_src": article_img,
            }
            dcontents.append(dc)
        rank = len(dcontents) + 1
        for c in contents:
            if c["type"] == "text":
                dc = {
                    "rank": rank,
                    "content": c["data"],
                    "image": "",
                    "image_src": "",
                }
            else:
                # dc = {
                #     "rank": rank,
                #     "content": "",
                #     "image": "",
                #     "image_src": c["data"],
                # }
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
            dcontents.append(dc)
            rank += 1
        dnews["contents"] = dcontents

        brief = util.get_brief_from_news(dcontents)
        # post = util.get_poster_from_news(dcontents)
        # dnews["post"] = post
        # if post is None or post.strip() == "":
        post = util.get_posterId_from_news(dcontents)

        if download_crawler is None:
            dnews["post"] = post
        else:
            dnews["postId"] = post
        dnews["brief"] = brief
        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        # collection_news.insert(dnews)
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
    logger.info("Done")


def process(content, page_crawler, flag):
    d = pq(html.fromstring(content))
    divs = d("section#content> div#mason-layout> div.boxed-mason")
    #logger.info(lis)
    for div in divs:
        l = pq(div)
        title = l("div.featured-summary> h2").text().strip()
        href = l("div.featured-summary> h2> a").attr("href").strip()
        #news_key = href.split("/")[-1]
        news_url = href

        logger.info("%s, %s", title, news_url)

        if collection_news.find_one({"link":news_url}) is None or flag == "all":
            craw = True
            newses = list(collection_news.find({"title": title, "source": {"$ne": SOURCE}}))
            for news in newses:
                if news.has_key("type") and news["type"] > 0:
                    craw = False
                    break
            if craw:
                retry = 0
                while True:
                    result = page_crawler.crawl(news_url, agent=True)
                    if result['get'] == 'success':
                        #logger.info(result["content"])
                        try:
                            process_news(result['content'], news_url)
                        except Exception,ex:
                            logger.exception(ex)
                        break

                    if retry >= 20:
                        break
                    retry += 1
    #crawler.save(g.SOURCE, g.TYPE, url, key, content)


def run(flag):
    global CURRENT_PAGE
    crawler = TuopuNewsListCrawler()
    page_crawler = TuopuNewsPageCrawler()

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


        url = "http://tobshe.com/page/%s/" % key
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    process(result['content'], page_crawler, flag)
                except Exception,ex:
                    logger.exception(ex)
                break


def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("Tuopu news %s start...", flag)
        CURRENT_PAGE = 1
        threads = [gevent.spawn(run,flag) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Tuopu news %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*15)        #5hour
        else:
            return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    flag = "incr"
    concurrent_num = 1

    if len(sys.argv) > 1:
        flag = sys.argv[1]

    start_run(concurrent_num, flag)