# -*- coding: utf-8 -*-
import os, sys, datetime, re, ast
from lxml import html
from pyquery import PyQuery as pq
import time
import json

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,extract,db,util,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_wangyi_news", stream=True)
logger = loghelper.get_logger("crawler_wangyi_news")

NEWSSOURCE = "Wangyi"
RETRY = 3
TYPE = 60009
SOURCE =13850
URLS = []
CURRENT_PAGE = 1
Nocontents = [
]
columns = [
    {"id": "82f2ab51-1586-437b-9f0e-61c4333adaea_1", "max": 2},
    {"id": "2e159f5b-b812-45d7-9bf7-3c8760b5b9bd_1", "max": 2},
    {"id": "c5bc89eb-0b80-45fc-a581-e782219bd0a7_1", "max": 2},
    {"id": "414d4408-f460-4f2e-8221-4ae46a686a7a_1", "max": 2},
    {"id": "edc09530586245e2ad6c08b63abe06b6_1", "max": 1},

]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=20):
        BaseCrawler.BaseCrawler.__init__(self,timeout=timeout)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                # logger.info("type: %s", type(content))
                # logger.info(content.decode("utf-8"))
                content1 = content.replace("true","\"abctrue\"").replace("false","\"abcfalse\"").replace("null","\"abcnull\"")
                # logger.info(content1)
                contentnew = eval(content1.decode("utf-8").strip())
                # logger.info("type: %s", type(contentnew))
                # logger.info(contentnew)
                j = contentnew[0]
                # logger.info(j)
                logger.info(j["nextPageToken"])
                # logger.info(j)
            except Exception, ex:
                logger.exception(ex)
                return False

            if len(contentnew[1])>20:
                return True

        return False

class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=20):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    #实现<div class="tabCont
    def is_crawl_success(self,url,content):

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('div.news-header> h1').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title is not None:
            return True
        return False


def has_news_content(content):

    return True


def process_news(column, wangyiurl, content, newspost, download_crawler, reallink):
    if has_news_content(content):
        d = pq(html.fromstring(content.decode("utf-8")))

        key = reallink.split("=")[-1].replace("","")

        type = TYPE

        category = None

        title = d('div.news-header> h1').text().strip()
        logger.info("title: %s", title)
        tags = []


        post_time = d('div.news-header> p.info').text()
        logger.info(post_time)
        try:

            news_time = extract.extracttime(post_time.split("&nbsp;")[0].strip())
            if news_time is None:
                news_time = datetime.datetime.now()
        except:
            news_time = datetime.datetime.now()

        article = d('div.news-content').html()
        contents = extract.extractContents(wangyiurl, article, document=False)

        logger.info("%s, %s, %s -> %s", key, title, news_time, ":".join(tags))


        flag, domain = url_helper.get_domain(reallink)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": reallink,
            "wangyiLink": wangyiurl,
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
            "categoryNames": [],
            # "sectors": [20]
        }
        dcontents = []
        rank = 1
        for c in contents:
            # if c["data"].find("网页转载须在文首注明来源投资界")>=0:
            #     continue
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

            logger.info(c["data"])
            dcontents.append(dc)
            rank += 1
        dnews["contents"] = dcontents

        brief = util.get_brief_from_news(dcontents)

        post = util.get_posterId_from_news(dcontents)

        if download_crawler is None:
            dnews["post"] = post
        else:
            dnews["postId"] = post
        dnews["brief"] = brief

        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        if title is not None and len(contents) > 0:
            # collection_news.insert(dnews)
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s", nid)
            pass
        # logger.info("*************DONE*************")
    return


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["wangyiLink"], URL["post"], download_crawler, URL["link"])

def crawler_news(column, crawler, newsurl, newspost, download_crawler, reallink):
    retry = 0
    while True:
        result = crawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'], newspost, download_crawler, reallink)
            except Exception,ex:
                logger.exception(ex)
            break
        retry += 1
        if retry > 20: break



def process(content, flag):
    # j = json.loads(content[0])
    # contentnew = eval(content.decode("utf-8"))
    content1 = content.replace("true", "\"abctrue\"").replace("false", "\"abcfalse\"").replace("null", "\"abcnull\"")
    # logger.info(content1)
    contentnew = eval(content1.decode("utf-8"))
    infos = contentnew[1]
    nextpt = contentnew[0]["nextPageToken"]

    for info in infos:
        try:
            sid = info["sourceID"]
            key = info["contentID"]
            title = info["title"]
            wangyilink = "https://yuedu.163.com/source.do?operation=queryContentHtml&id=%s&contentUuid=%s" % (sid, key)
            link = info["sourceURL"]
            logger.info("News id: %s, title: %s, realLink : %s", key, title, link)
            # check mongo data if link is existed
            mongo = db.connect_mongo()
            collection_news = mongo.article.news
            item = collection_news.find_one({"link": link})
            item2 = collection_news.find_one({"title": title})
            mongo.close()

            if ((item is None and item2 is None) or flag == "all") and link not in URLS and link.find("36kr") ==-1:
                linkmap = {
                    "wangyiLink": wangyilink,
                    "post": None,
                    "link": link
                }
                URLS.append(linkmap)
                logger.info("News id: %s, title: %s, realLink : %s existed", key, title, link)


        except Exception, ex:
            logger.exception(ex)
            continue
    return nextpt, len(URLS)


def run(flag, column, listcrawler, newscrawler, download_crawler):
    global CURRENT_PAGE
    cnt = 1
    nextPt = None
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
            url = "https://yuedu.163.com/source.do?operation=queryContentList&id=%s" % (column["id"])
        elif nextPt is not None:
            url = "https://yuedu.163.com/source.do?operation=queryContentList&id=%s&pageToken=%s" % (column["id"], nextPt)
        else:
            break
        maxretry = 0
        while True:
            result = listcrawler.crawl(url,agent=True)

            if result['get'] == 'success':
                try:
                    nextPt, cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        run_news(column, newscrawler, download_crawler)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break
            if maxretry > 20:
                break
            maxretry += 1



def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        download_crawler = download.DownloadCrawler(use_proxy=False)
        # download_crawler = None
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, download_crawler)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            time.sleep(60*8)        #30 minutes
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
            # download_crawler = None
            crawler_news({"column": "new", "max": 3}, NewsCrawler(), link, None, download_crawler, 'http://www.ifanr.com/889662')
    else:
        start_run(1, "incr")