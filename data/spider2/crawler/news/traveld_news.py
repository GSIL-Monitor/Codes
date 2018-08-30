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
loghelper.init_logger("crawler_traveld_news", stream=True)
logger = loghelper.get_logger("crawler_traveld_news")

NEWSSOURCE = "Traveldaily"
RETRY = 3
TYPE = 60001
SOURCE =13822
URLS = []
CURRENT_PAGE = 1
linkPattern = "/article/\d+"
Nocontents = [
]
columns = [
    {"column": None, "max": 4},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("环球旅讯") >= 0:
            return True
        return False

class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("Xtecher") >= 0:
            return True
        if content.find("您没有权限预览该文章") >= 0:
            return True
        return False



def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    temp = title.split("-")
    if len(temp) < 2:
        return False
    if temp[0].strip() == "":
        return False
    return True


def process_news(column, newsurl, content, newsposttime, download_crawler):
    if has_news_content(content):
        d = pq(html.fromstring(content.decode("utf-8")))

        key = newsurl.split("/")[-1].strip()

        type = TYPE


        title = d('div.article-wrap> div.article-head> h1').text().strip()
        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        if collection_news.find_one({"title": title}) is not None:
            mongo.close()
            return
        tags = []
        articletags = d("meta[name='keywords']").attr("content")
        if articletags is not None:
            for tag in articletags.split(","):
                if tag is not None and tag.strip() != "" and tag not in tags and tag != title:
                    tags.append(tag)

        category = None
        categoryNames = []
        if "投资并购" in tags:
            category = 60101
            categoryNames.append("融资")

        # post = d('div#post_thumbnail> img').attr("src")
        post = None

        brief = d("meta[name='description']").attr("content")

        news_time = None
        if newsposttime is not None:
            news_time = extract.extracttime(newsposttime)
        if news_time is None:
            dt = datetime.date.today()
            post_time = d('div.article-wrap> div.article-head> p> span.article-time').text()
            if post_time is None or post_time.strip() == str(dt):
                news_time = datetime.datetime.now()
                # news_time = datetime.datetime.strptime(post_time, "%Y-%m-%d")
            else:
                news_time =  datetime.datetime.strptime(post_time, "%Y-%m-%d")

        article = d('div.article-wrap> div.article-content').html()
        contents = extract.extractContents(newsurl, article)

        logger.info("%s, %s, %s, %s -> %s, %s. %s", key, title, news_time, ":".join(tags), category, brief, post)
        # exit()
        # mongo = db.connect_mongo()
        # collection_news = mongo.article.news
        # if collection_news.find_one({"title": title}) is not None:
        #     mongo.close()
        #     return

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
        dnews["postId"] = post
        dnews["brief"] = brief

        # Design for sector:
        dnews["sectors"] = [10]
        dnews["sector_confidence"] = [1]

        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        # collection_news.insert(dnews)
        mongo.close()
        # logger.info("*************DONE*************")
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
    return


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL["posttime"], download_crawler)

def crawler_news(column, crawler, newsurl, newsposttime, download_crawler):
    while True:
        result = crawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'], newsposttime, download_crawler)
            except Exception,ex:
                logger.exception(ex)
            break



def process(content, flag):

    d = pq(html.fromstring(content.decode("utf-8")))
    for a in d('div.main-left> ul> li.main-child> div.childR'):
        try:
            link = d(a)('h2> a').attr("href").strip()
            # logger.info(link)
            if re.search(linkPattern, link):
                link = "https://www.traveldaily.cn" + link
                logger.info("Link: %s is right news link", link)
                posttime = d(a)('div.time').text()
                # check mongo data if link is existed
                mongo = db.connect_mongo()
                collection_news = mongo.article.news
                item = collection_news.find_one({"link": link})
                mongo.close()

                if (item is None or flag == "all") and link not in URLS:
                    linkmap = {
                        "link": link,
                        "posttime": posttime
                    }
                    URLS.append(linkmap)
            else:
                # logger.info(link)
                pass
        except:
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

        url = 'https://www.traveldaily.cn/today/%s/' % (key)

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
        newscrawler = ListCrawler()
        download_crawler = download.DownloadCrawler(use_proxy=False)
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
            download_crawler = download.DownloadCrawler(use_proxy=False)
            crawler_news({}, ListCrawler(), link, None, download_crawler)
    else:
        start_run(1, "incr")

    # download_crawler = download.DownloadCrawler(use_proxy=False)
    # (imgurl, width, height) = parser_mysql_util.get_logo_id_size('http://mmbiz.qpic.cn/mmbiz_gif/pozCkWaPLSaP14v0tHds5dt7KvnZofwyPRR0FZODPBtq8kMGMCYaLvYA8mNBpstiaBVIGuvBzE52fG6jRQg3Ymg/0.gif', download_crawler, SOURCE, "3333", "news")
    # print (imgurl, int(width), int(height))
    # (imgurl, width, height) = parser_mysql_util.get_logo_id_size(
    #     'http://mmbiz.qpic.cn/mmbiz_png/QXPrBFL6vNNoTgKchWFA8ia97siacicFLzMZKr6171Oz7uW1Yj4VrqWHrp41x1cCThOVWgG1unoHz2mjmHtouupFw/640?wx_fmt=png',
    #     download_crawler, SOURCE, "3333", "news")
    # print (imgurl, width, height)


