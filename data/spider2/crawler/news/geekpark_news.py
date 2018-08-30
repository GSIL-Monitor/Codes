# -*- coding: utf-8 -*-
import os, sys, datetime
from lxml import html
from pyquery import PyQuery as pq
import urllib
import time
import json

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db,util,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_geekpark_news", stream=True)
logger = loghelper.get_logger("crawler_geekpark_news")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

newsid =[]
initpage = 1

SOURCE = 13809
TYPE =60001

class GeekparkCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        #logger.info(content)
        d = pq(html.fromstring(content.decode("utf-8")))
        if content.find("article-item") >= 0:
            return True
        return False

class GeekparkNewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " " + url)

        if title.find("极客公园") >= 0:
            return True
        # logger.info(content)
        return False


def has_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    articles = d("article.article-item")
    if len(articles) > 0:
        return True
    return False

def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    temp = title.split("|")
    if len(temp) < 2 :
        return False
    if temp[-1].strip() != "极客公园":
        return False
    if temp[0].strip() == "":
        return False
    return True


def process_news(item, url, content):
    if has_news_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        d = pq(html.fromstring(content.decode("utf-8")))

        title = d('div.main-wrap> header> h1').text().strip()
        post_time = d('div.topic-info> span.release-date> span').attr("data-time")
        post_Date = time.localtime(int(post_time))
        news_time = datetime.datetime(post_Date.tm_year, post_Date.tm_mon, post_Date.tm_mday, post_Date.tm_hour,
                                      post_Date.tm_min, post_Date.tm_sec)

        key = item["key"]
        column = d('div.main-wrap> div.label').text().strip()
        brief = d("meta[name='description']").attr("content")
        if brief is not None:
            brief = brief.strip()

        if column is not None:
            tags = column.split()
        else:
            tags = []

        category = None
        categoryNames = []
        if "深度报道" in tags:
            type = 60003
            category=60107
        else:
            type = 60001

            if "极客早知道" in tags:
                category = 60105
                categoryNames.append("大公司")

        keywords = pq(content.decode("utf-8"))("meta[name='keywords']").attr("content")
        if keywords is not None:
            for keyword in keywords.split(","):
                if keyword is not None and keyword not in tags:
                    tags.append(keyword.strip())

        logger.info("%s, %s, %s, %s, %s, %s -> %s", key, title, post_time, news_time, brief, ":".join(tags), category)
        article = d('section.main-content> article> div.article-content').html()
        #logger.info(article)
        contents = extract.extractContents(url, article)

        if collection_news.find_one({"source": SOURCE, "key_int": int(key)}) is not None:
            return
            # collection_news.delete_one({"source": SOURCE, "key_int": int(key)})

        if collection_news.find_one({"title": title, "source": {"$ne": SOURCE}}) is not None:
            return
            # collection_news.delete_many({"title": title, "source": {"$ne": SOURCE}})

        flag, domain = url_helper.get_domain(url)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": url,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": int(key),
            "type": type,
            "original_tags": tags,
            "processStatus":0,
            # "companyId": None,
            "companyIds":[],
            "category": category,
            "domain": domain,
            "categoryNames": categoryNames
        }
        dcontents = []
        article_img = d('section.main-content> article> div.topic-cover> img').attr("src")
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
        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        # post = util.get_poster_from_news(dcontents)
        # dnews["post"] = post
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
        # logger.info("*************DONE*************")
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
        #g.latestIncr()

def run_news(crawler):
    while True:
        if len(newsid) ==0:
            return
        nitem = newsid.pop(0)

        url = nitem['link']
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["redirect_url"])
                try:
                    process_news(nitem, url, result['content'])
                except Exception,ex:
                    logger.exception(ex)
                break




def process_page(content,flag):
    d = pq(html.fromstring(content.decode('utf-8')))
    articles = d("article.article-item")
    # logger.info(lis)
    for li in articles:
        l = pq(li)
        title = l("div.article-info> div> a.article-title").text().strip()
        href = l("div.article-info> div> a.article-title").attr("href")
        if href is None or href.strip() == "":
            continue
        news_key = href.split("/")[-1]
        news_url = "http://www.geekpark.net"+href

        logger.info("%s, %s, %s", title, news_key, news_url)

        if news_key is not None and (collection_news.find_one({"source": SOURCE, "key_int": int(news_key)}) is None or flag == "all"):
            craw = True
            newses = list(collection_news.find({"title": title, "source": {"$ne": SOURCE}}))
            for news in newses:
                if news.has_key("type") and news["type"] > 0:
                    craw = False
                    break
            if craw:
                item = {
                    "key": news_key,
                    "link": news_url,
                }
                newsid.append(item)


    return newsid

def start_run(flag):
    global initpage
    while True:
        logger.info("Geekpark news %s start...", flag)

        crawler = GeekparkCrawler()
        page = initpage
        retry = 0
        while True:
            if page == 1:
                page_url = "http://www.geekpark.net/"
            else:
                page_url  = "http://www.geekpark.net/articles_list?page=%s" % page
            result = crawler.crawl(page_url, agent=True)
            if result['get'] == 'success':
                if has_content(result["content"]):
                    newsid = process_page(result["content"],flag)
                    if len(newsid) > 0:
                        # logger.info("crawler news details")
                        run_news(GeekparkNewsCrawler())
                        # #exit()
                        page += 1
                        if page >=5:
                            break
                        continue
                else:
                    logger.info("no content")
                    logger.info(result["content"])
                break
            elif result['get'] == 'fail' and result['content'] is None:
                retry += 1
                if retry > 3:
                    break


        logger.info("Geekpark news %s end.", flag)

        if flag == "incr":
            time.sleep(60*15) #10 minutes
        else:
            return  #3 days


if __name__ == "__main__":

    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "all":
            start_run("all")
        else:
            start_run("incr")
    else:
        start_run("incr")