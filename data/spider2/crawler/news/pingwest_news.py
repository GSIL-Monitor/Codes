# -*- coding: utf-8 -*-
import os, sys, datetime, re
from lxml import html
from pyquery import PyQuery as pq
import time
import GlobalValues_news

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,extract,db, util,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_pingwest_news", stream=True)
logger = loghelper.get_logger("crawler_pingwest_news")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news


TYPE = 60001
SOURCE =13810
CURRENT_PAGE = 1

columns = [
    {"column": "figure", "maxpage": 13},
    {"column": "company", "maxpage": 5},
    {"column": "product", "maxpage": 80},
]

class PingwestCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
           return False

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)

        if title.find("PingWest品玩") >= 0:
            return True
        if title.find("Pingwest品玩") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    temp = title.split("|")
    if len(temp) < 2:
        return False
    if temp[-1].strip() != "PingWest品玩":
        return False
    if temp[0].strip() == "":
        return False
    return True


def process_news(content, url):
    if has_news_content(content):
        d = pq(html.fromstring(content.decode("utf-8")))
        download_crawler = download.DownloadCrawler(use_proxy=False)
        title = d('div.post-img-left> div> div.post-head> h1.title').text().strip()
        post_time = d('article.post-article').attr("ptime")
        post_Date = time.localtime(int(post_time))
        news_time = datetime.datetime(post_Date.tm_year, post_Date.tm_mon, post_Date.tm_mday, post_Date.tm_hour,
                                      post_Date.tm_min, post_Date.tm_sec)

        if collection_news.find_one({"link": url}) is not None:
            return
            # collection_news.delete_one({"link": url})

        if collection_news.find_one({"title": title, "source": {"$ne": SOURCE}}) is not None:
            return

        key = d('article.post-article').attr("postid")
        try:
            key_int = int(key)
        except:
            key_int = None
        column = d('span.post-category').text().strip()
        brief = d("meta[name='description']").attr("content").strip()

        if column is not None:
            tags = column.split()
        else:
            tags = []

        categoryNames = []
        if "人物" in tags:
            category = 60103
        elif "公司" in tags:
            category = 60105
            categoryNames.append("大公司")
        else:
            category = None

        keywords = d("meta[name='keywords']").attr("content")
        if keywords is not None:
            for keyword in keywords.split(","):
                if keyword is not None and keyword.strip() not in tags and keyword.strip() not in ["PingWest", "品玩"]:
                    tags.append(keyword.strip())

        postraw = d("link[rel='image_src']").attr("href")
        # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        logger.info("%s, %s, %s, %s, %s, %s -> %s, %s", key, title, post_time, news_time, brief, ":".join(tags), category, post)
        article = d('div.box-con> div#sc-container').html()
        # logger.info(article)
        contents = extract.extractContents(url, article)

        # if collection_news.find_one({"link": url}) is not None:
        #     return
        #     # collection_news.delete_one({"link": url})
        #
        # if collection_news.find_one({"title": title, "source": {"$ne": SOURCE}}) is not None:
        #     return
            # collection_news.delete_many({"title": title, "source": {"$ne": SOURCE}})
        flag, domain = url_helper.get_domain(url)
        dnews = {
            "date": news_time - datetime.timedelta(hours=16),
            "title": title,
            "link": url,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": key_int,
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
                # dc = {
                #     "rank": rank,
                #     "content": "",
                #     "image": "",
                #     "image_src": c["data"].replace("?imageView2/2/w/750/q/90",""),
                # }
                if download_crawler is None:
                    dc = {
                        "rank": rank,
                        "content": "",
                        "image": "",
                        "image_src": c["data"].replace("?imageView2/2/w/750/q/90",""),
                    }
                else:
                    (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"].replace("?imageView2/2/w/750/q/90",""), download_crawler, SOURCE, key, "news")
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
        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        # if post is None or post.strip() == "":
        #     post = util.get_poster_from_news(dcontents)
        # dnews["post"] = post
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
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
        # collection_news.insert(dnews)
        # logger.info("*************DONE*************")

def process(content, column, page_crawler):
    d = pq(html.fromstring(content))
    divs = d("div.post-list> div.news-list> div.item")
    cnt = 0
    #logger.info(lis)
    for div in divs:
        l = pq(div)
        title = l("h2.title").text().strip()
        href = l("h2.title> a").attr("href").strip()
        news_url = href

        logger.info("%s, %s", title, news_url)

        if news_url is None or news_url.strip() == "" or news_url.find("x.pingwest.com") > 0 or news_url.find("shift.pingwest.com") > 0:
            continue
        if news_url.find("http") == -1:
            continue

        if collection_news.find_one({"link": news_url}) is None or flag == "all":
            craw = True
            newses = list(collection_news.find({"title": title, "source": {"$ne": SOURCE}}))
            for news in newses:
                if news.has_key("type") and news["type"] > 0:
                    craw = False
                    break
            if craw:
                while True:
                    result = page_crawler.crawl(news_url, agent=True)
                    if result['get'] == 'success':
                        #logger.info(result["content"])
                        try:
                            process_news(result['content'], news_url)
                        except Exception,ex:
                            logger.exception(ex)
                        cnt += 1
                        break
    return cnt



def run(flag, column):
    global CURRENT_PAGE
    crawler = PingwestCrawler()
    cnt = 1
    while True:
        key = CURRENT_PAGE
        #logger.info("key=%s", key)
        if flag == "all":
            if key > column["maxpage"]:
                return
        else:
            if cnt == 0:
                return

        CURRENT_PAGE += 1
        url = "http://www.pingwest.com/category/%s/page/%s/" % (column["column"], key)
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], column, crawler)
                    logger.info("%s has %s news", url, cnt)
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break


def start_run(flag):
    global CURRENT_PAGE
    while True:
        logger.info("Pingwest news %s start...", flag)
        for column in columns:

            CURRENT_PAGE = 1
            run(flag, column)

        logger.info("Pingwest news %s end.", flag)

        if flag == "incr":
            time.sleep(60*15)        #30 minutes
        else:
            return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    flag = "incr"

    start_run(flag)