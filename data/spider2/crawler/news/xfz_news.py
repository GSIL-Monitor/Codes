# -*- coding: utf-8 -*-
import os, sys, datetime
from lxml import html
from pyquery import PyQuery as pq
import urllib
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import json

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,extract,db,util,url_helper,desc_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_xfz_news", stream=True)
logger = loghelper.get_logger("crawler_xfz_news")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

newsid =[]
page = 1

SOURCE = 13813

class XfzCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
                #logger.info(j)
            except:
                return False

            if j.has_key("code") and j["code"] == 200:
                return True

        return False

class XfzNewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):

        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " " + url)

        if title.find("小饭桌") >= 0 or title.find("不凡商业") >= 0:
            return True
        # logger.info(content)
        return False


def has_content(content):
    if content is not None:
        try:
            j = json.loads(content)
        except:
            logger.info("Not json content")
            logger.info(content)
            return False
        if len(j["data"])> 0:
            return True
        else:
            logger.info("No content: %s", content)
    else:
        logger.info("Fail to get content")
    return False

def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    temp = title.split("_")
    # if len(temp) < 3:
    #     logger.info(len(temp))
    #     return False
    # if temp[-2].strip() != "不凡商业":
    #     return False
    if temp[0].strip() == "":
        return False
    return True


def process_news(item, url, content):
    if has_news_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        d = pq(html.fromstring(content.decode("utf-8")))

        title = d('div.detail-content> h1').text().strip()
        logger.info(title)
        key = item["key"]
        if collection_news.find_one({"source": SOURCE, "key_int": int(key)}) is not None:
            logger.info("here1")
            return
            # collection_news.delete_one({"source": SOURCE, "key_int": int(key)})

        if collection_news.find_one({"title": title, "source": {"$ne": SOURCE}}) is not None:
            logger.info("here11")
            return
            # collection_news.delete_many({"title": title, "source": {"$ne": SOURCE}})

        news_time = datetime.datetime.strptime(item["post_date"],"%Y-%m-%d %H:%M:%S")
        # key = item["key"]
        postraw = d("meta[property='og:image']").attr("content")
        # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        brief = d("div.wxApi> input#article-intro").attr("value").strip()


        logger.info("%s, %s, %s, %s", key, title, news_time, brief)
        article = d('div.detail-content> div.content-detail').html()
        #logger.info(article)
        contents = extract.extractContents(url, article)


        # if collection_news.find_one({"source": SOURCE, "key_int": int(key)}) is not None:
        #     return
        #     # collection_news.delete_one({"source": SOURCE, "key_int": int(key)})
        #
        # if collection_news.find_one({"title": title, "source": {"$ne": SOURCE}}) is not None:
        #     return
        #     # collection_news.delete_many({"title": title, "source": {"$ne": SOURCE}})

        flag, domain = url_helper.get_domain(url)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": url,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": int(key),
            "type": 60001,
            "original_tags": [],
            "processStatus":0,
            # "companyId": None,
            "companyIds":[],
            "category": None,
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
        if brief is None or brief.strip() == "" or desc_helper.check_desc(brief,2) is False:
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
        # collection_news.insert(dnews)
        #g.latestIncr()
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)

def run_news(crawler):
    while True:
        if len(newsid) ==0:
            return
        nitem = newsid.pop(0)
        retry = 0
        url = "https://www.bufanbiz.com/post/%s.html" % nitem["key"]
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["redirect_url"])
                try:
                    process_news(nitem, url, result['content'])
                except Exception,ex:
                    logger.exception(ex)
                break
            retry += 1
            if retry > 10:
                break




def process_page(content, flag):
    j = json.loads(content)
    infos = j["data"]
    if infos is not None:
        for info in infos:
            key = info["uid"]
            title = info["title"]
            date = info["time"]
            logger.info("%s, %s, %s", key, date, title)

            if collection_news.find_one({"source": SOURCE, "key_int": int(key)}) is None or flag == "all":
                craw = True
                newses = list(collection_news.find({"title": title, "source": {"$ne": SOURCE}}))
                for news in newses:
                    if news.has_key("type") and news["type"] > 0:
                        craw = False
                        break
                if craw:
                    item = {
                        "key": key,
                        "post_date": date
                    }
                    newsid.append(item)


    return newsid

def start_run(flag):
    global page
    while True:
        logger.info("Xfz news %s start...", flag)

        crawler = XfzCrawler()
        while True:
            page_url = "https://www.bufanbiz.com/api/website/articles/?p=%s&n=20" % page
            result = crawler.crawl(page_url, agent=True)
            if result['get'] == 'success':
                if has_content(result["content"]):
                    newsid = process_page(result["content"], flag)
                    if len(newsid) > 0:
                        page += 1
                        logger.info("crawler news details")
                        run_news(XfzNewsCrawler())

                        #exit()
                        continue
                    else:
                        page = 1
                else:
                    page = 1
                    logger.info("no content")
                    logger.info(result["content"])
                break


        logger.info("Xfz news %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*15)        #10 minutes
        else:
            gevent.sleep(86400*3)   #3 days


if __name__ == "__main__":

    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "all":
            start_run("all")
        else:
            start_run("incr")
    else:
        start_run("incr")