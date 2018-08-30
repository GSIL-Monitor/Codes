# -*- coding: utf-8 -*-
import os, sys, datetime, re
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
loghelper.init_logger("crawler_iheima_news", stream=True)
logger = loghelper.get_logger("crawler_iheima_news")

NEWSSOURCE = "Iheima"
RETRY = 15
TYPE = 60001
SOURCE =13819
URLS = []
CURRENT_PAGE = 1
linkPattern = "http://www.iheima.com/\w+/\d+/\d+/\d+.shtml"
Nocontents = [
]
columns = [
    {"column": None, "max": 6},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("iheima") != -1:
            return True
        if content.find("暂无数据") >= 0:
            return True
        return False

class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
           return False
        try:
            d = pq(html.fromstring(content.decode("utf-8")))
        except:
            d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("i黑马") >= 0:
            return True
        if title.find("#404") >= 0:
            return True
        return False



def has_news_content(content):
    try:
        d = pq(html.fromstring(content.decode("utf-8")))
    except:
        d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    temp = title.split("_")
    if len(temp) < 3:
        return False
    if temp[0].strip() == "":
        return False
    return True


def process_news(column, newsurl, content, newspost, download_crawler):
    if has_news_content(content):
        try:
            d = pq(html.fromstring(content.decode("utf-8",'ignore')))
        except:
            d = pq(html.fromstring(content))

        key = newsurl.split("/")[-1].replace(".shtml","")

        type = TYPE

        category = None

        title = d('div.main-content> div.title').text().strip()

        tags = []
        articletags = d("meta[name='keywords']").attr("content")
        if articletags is not None:
            for tag in articletags.split():
                if tag is not None and tag.strip() != "" and tag not in tags and tag != title:
                    tags.append(tag)

        # post = d('div#post_thumbnail> img').attr("src")
        post = None

        brief = d("meta[name='description']").attr("content")

        post_time = d('div.author> span.time').text()
        logger.info(post_time)
        news_time = extract.extracttime(post_time)
        if news_time is None:
            news_time = datetime.datetime.now()
        try:
            article = d('div.main-content').html()
        except:
            article = content
        contents = extract.extractContents(newsurl, article)

        logger.info("%s, %s, %s, %s -> %s, %s", key, title, news_time, ":".join(tags), category, brief)
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
            "categoryNames": []
        }
        dcontents = []
        rank = 1
        for c in contents:
            if c["data"].find("http://app.iheima.com/?app=member&controller=avatar") != -1 or \
                            c["data"] ==title or c["data"] == brief or c["data"].find(post_time) != -1 or \
                            c["data"].find("data:image/png;base64") != -1:
                continue

            if c["data"].find("未经授权，转载必究") != -1 or c["data"].find("赞(...)") != -1:
                break

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
            logger.info(c["data"])
            dcontents.append(dc)
            rank += 1
        dnews["contents"] = dcontents
        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        if post is None or post.strip() == "":
            post = util.get_posterId_from_news(dcontents)
        dnews["postId"] = post
        dnews["brief"] = brief

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

        crawler_news(column, crawler, URL["link"], URL["post"], download_crawler)

def crawler_news(column, crawler, newsurl, newspost, download_crawler):
    retry =0
    while True:
        result = crawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'], newspost, download_crawler)
            except Exception,ex:
                logger.exception(ex)
            break
        retry += 1
        if retry>20:
            break




def process(content, flag):
    # logger.info(content)
    d = pq(html.fromstring(content.decode("utf-8")))
    for a in d('div.list> div> div> a.title'):
        try:
            link = d(a).attr("href").strip()
            if re.search(linkPattern, link):
                logger.info("Link: %s is right news link", link)

                #check mongo data if link is existed
                mongo = db.connect_mongo()
                collection_news = mongo.article.news
                item = collection_news.find_one({"link":link})
                mongo.close()

                if (item is None or flag == "all") and link not in URLS:

                    linkmap = {
                        "link": link,
                        "post": None
                    }
                    URLS.append(linkmap)
            else:
                logger.info(link)
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

        url = 'http://www.iheima.com/?page=%s&category=%s' % (key, "%E5%85%A8%E9%83%A8")
        # header = {"X-Requested-With": "XMLHttpRequest"}
        header = {}
        while True:
            result = listcrawler.crawl(url, headers=header,agent=True)
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