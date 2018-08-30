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
import loghelper,extract,db, util,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_kejilie_news", stream=True)
logger = loghelper.get_logger("crawler_kejilie_news")

NEWSSOURCE = "kejilie"
RETRY = 3
TYPE = 60005
SOURCE =13888
URLS = []
CURRENT_PAGE = 1
linkPattern = "www.kejilie.com/\w+"
Nocontents = [
]
columns = [
    # {"column": "jmd", "max": 2},
    {"column": "None", "max": 1},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=10):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

        # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
           return False

        d = pq(html.fromstring(content.decode("utf-8","ignore")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("科技猎") >= 0:
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
        if title.find("科技猎") >= 0:
            return True
        if title.find("未找到该页") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8","ignore")))
    title = d('head> title').text().strip()
    temp = title.split("|")
    logger.info("title:%s %s", title, len(temp))
    if len(title) <2 or title == "":
        return False
    return True

def process_news(column, newsurl, content, newspost, topic, download_crawler):
    if has_news_content(content):
        logger.info('here')
        download_crawler = download.DownloadCrawler(use_proxy=False)
        # logger.info(content)
        d = pq(html.fromstring(content.decode("utf-8","ignore")))

        category = None
        categoryNames = []

        key = newsurl.split("/")[-1].replace(".html","")

        type = TYPE

        title = d('h1.article_nr_title').text().strip()
        # if title.find("融资") >= 0:
        #     type = 60001
        #     category = 60101

        (posturl, width, height) = parser_mysql_util.get_logo_id_new(newspost, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        logger.info("title: %s", title)
        # mongo = db.connect_mongo()
        # collection_news = mongo.article.news
        # if collection_news.find_one({"title": title}) is not None:
        #     mongo.close()
        #     return

        tags = []
        articletags = d("meta[name='keywords']").attr("content")
        if articletags is not None:
            for tag in articletags.split(","):
                if tag is not None and tag.strip() != "" and tag not in tags and tag != title:
                    tags.append(tag)

        # try:
        #     brief = d("meta[name='description']").attr("content")
        # except:
        brief = None


        try:
           post_time =d("span> time").attr("title")

           logger.info(post_time)
           news_time = extract.extracttime(post_time)
           logger.info("news-time: %s", news_time)
        except Exception, e:
            logger.info(e)
            news_time = datetime.datetime.now()

        if news_time is None:
            news_time = datetime.datetime.now()

        article = d('div.so-content').html()
        contents = extract.extractContents(newsurl, article)


        logger.info("%s, %s, %s, %s -> %s, %s", key, title, news_time, ":".join(tags), category, brief)

        flag, domain = url_helper.get_domain(newsurl)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": newsurl,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": None,
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
            if c["data"].find("随意打赏") >= 0 or \
                    c["data"].find("版权声明") >= 0:
                break

            if c["data"].find("8btctest1/custom/images")>=0:
                continue

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
            logger.info(c["data"])
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
        # collection_news.insert(dnews)
        if title is not None and len(contents) > 0:
            # logger.info("*************DONE*************")
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s", nid)
            pass
    return

def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL["post"], None, download_crawler)

def crawler_news(column, crawler, newsurl, newspost, topic, download_crawler):
    while True:
        result = crawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'], newspost, topic, download_crawler)
            except Exception,ex:
                logger.exception(ex)
            break


def process(content, flag):
    if content.find("kejilie") >= 0:
        d = pq(html.fromstring(content.decode("utf-8","ignore")))
        for a in d('ul.am-list> li> div> h3'):
            try:
                link = d(a)('a').attr("href")
                title = d(a)('a').text()
                # link = "http://www.8btc.com" + link
                if re.search(linkPattern, link) and title is not None and title.strip() != "":
                    # logger.info("Link: %s is right news link %s", link, title)
                    # title = d(a)('h3> a').text()
                    post = None
                    sort = None
                    logger.info("Link: %s is right news link %s|%s", link, title, sort)
                    mongo = db.connect_mongo()
                    collection_news = mongo.article.news
                    item = collection_news.find_one({"link": link})
                    item2 = collection_news.find_one({"title": title})
                    mongo.close()

                    if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                        linkmap = {
                            "link": link,
                            "post": post,
                            "sort": sort
                        }
                        URLS.append(linkmap)

                else:
                    # logger.info(link)
                    pass
            except Exception, e:
                logger.info(e)
                logger.info("cannot get link")
    return len(URLS)


def run(flag, column, listcrawler, newscrawler, concurrent_num):
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
        # pdata = "action=loadpost&offset=%s" % (key-1)
        url = "http://www.kejilie.com/toindex.do?currentPage=%s#news" % key
        while True:
            result = listcrawler.crawl(url, agent=True)
            # result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        # threads = [gevent.spawn(run_news, column, newscrawler, download_crawler=None) for i in xrange(concurrent_num)]
                        # gevent.joinall(threads)
                        run_news(column, newscrawler, download_crawler=None)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break
        # exit()
        # elif result['get'] == 'redirect' and r


def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num)

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
            download_crawler = None
            crawler_news({}, NewsCrawler(), link, None, [], download_crawler)
    else:
        start_run(1, "incr")