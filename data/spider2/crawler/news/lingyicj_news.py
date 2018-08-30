# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, urllib,time
from lxml import html
from pyquery import PyQuery as pq


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
loghelper.init_logger("crawler_01caijing_news", stream=True)
logger = loghelper.get_logger("crawler_01caijing_news")

NEWSSOURCE = "lingyicaijing"
RETRY = 3
TYPE = 60001
SOURCE =13853
URLS = []
CURRENT_PAGE = 1
linkPattern = "www.01caijing.com/(article|ejinrong)/\d+.htm"
Nocontents = [
]
columns = [
    {"column": "new", "max": 1},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        # logger.info(content)
        if title.find("零壹财经") >= 0:
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
        if title.find("零壹财经") >= 0:
            return True
        if title.find("404") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    temp = title.split("-")
    logger.info("%s-%s",title, len(temp))
    if len(temp) < 2:
        return False
    if temp[0].strip() == "" or temp[0].strip() == "未找到页面":
        return False
    return True


def process_news(column, newsurl, content, newspost, download_crawler):
    if has_news_content(content):
        logger.info("here")
        d = pq(html.fromstring(content.decode("utf-8")))

        key = newsurl.split("/")[-1].replace(".htm", "")

        type = TYPE

        category = None

        title = d('div.article-main>h1').text().strip()

        if title is None or title == "":
            return
        tags = []
        articletags = d("meta[name='keywords']").attr("content")
        if articletags is not None:
            for tag in articletags.replace("，", ",").split(","):
                if tag is not None and tag.strip() != "" and tag not in tags and tag != title:
                    tags.append(tag)
        #

        newspost1 = d('div.article-main> div> img').attr("src")
        # posturl = parser_mysql_util.get_logo_id(newspost, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(newspost1, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        # post = d("meta[property='og:image']").attr("content")
        try:
            brief = d("meta[name='description']").attr("content")
        except:
            brief = None

        try:
            post_time =d('small> span').text().split()[-1]
            if post_time == datetime.date.strftime(datetime.date.today(),'%Y-%m-%d'):
                news_time = datetime.datetime.now()
            else:
                news_time = datetime.datetime.strptime(post_time, "%Y-%m-%d")
        except:
            news_time = datetime.datetime.now()
        article = d('div.article-txt').html()
        contents = extract.extractContents(newsurl, article, document=False)

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
            "companyId": None,
            "companyIds": [],
            "category": category,
            "domain": domain,
            "categoryNames": [],
            "sectors": [20]
        }
        dcontents = []
        rank = 1
        for c in contents:
            # if c["data"].find("◆END◆")>=0 or c["data"].find("…………………")>=0:
            #     break
            #
            # if c["data"].find("ACG 领域最具影响力的产业新媒体") >= 0 or c["data"].find("访问三文娱网站3wyu.com查看产业必读文章") >=0:
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

        if title is not None and len(contents) > 0:
            # mid = collection_news.insert(dnews)
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s", nid)
            pass
        mongo.close()
        # logger.info("*************DONE************* %s", mid)
    return


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL.get("post",None), download_crawler)

def crawler_news(column, crawler, newsurl, newspost, download_crawler):
    retry = 0
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
        if retry > 25: break



def process(content, flag):
    if content.find("caijing") >= 0:
        d = pq(html.fromstring(content.decode("utf-8")))
        for a in d('a'):
            try:
                link = d(a)('a').attr("href")
                title = d(a)('a').text()
                # logger.info(link)
                if re.search(linkPattern, link) and title is not None and title.strip() != "":
                    logger.info("Link: %s is right news link: %s", link, title)
                    title = d(a)('a').text()
                    linknew = link.replace("ejinrong","article")
                    mongo = db.connect_mongo()
                    collection_news = mongo.article.news
                    item = collection_news.find_one({"link": linknew})
                    item2 = collection_news.find_one({"title": title})
                    mongo.close()

                    if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                        linkmap = {
                            "link": linknew,
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

        url = "http://www.01caijing.com/"

        while True:
            result = listcrawler.crawl(url,agent=True)

            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        run_news(column, newscrawler, download_crawler)

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
        # download_crawler = None
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num, download_crawler)

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
            crawler_news({"column": "new", "max": 1}, NewsCrawler(), link, "", download_crawler)
    else:
        start_run(1, "incr")