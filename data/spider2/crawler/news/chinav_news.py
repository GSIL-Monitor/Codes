# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, time
from lxml import html
from pyquery import PyQuery as pq

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
loghelper.init_logger("crawler_cnav_news", stream=True)
logger = loghelper.get_logger("crawler_cnav_news")

NEWSSOURCE = "ChinaVenture"
RETRY = 3
TYPE = 60001
SOURCE =13818
URLS = []
CURRENT_PAGE = 1
linkPattern = "https://www.chinaventure.com.cn/cmsmodel/news/detail/\d+.shtml"
Nocontents = [
]
columns = [
    {"column": "cna", "max": 40},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
                logger.info(j)
            except Exception,E:
                logger.info(E)
                return False

            if j.has_key("msg") is True and j["msg"] == "成功":
                return True

        return False

def has_news_content(content):
    return True


def process_news(column, newsurl, content, newspost):
    if has_news_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        key = content["news"]["id"]

        newsurl = "https://www.chinaventure.com.cn/cmsmodel/news/detail/%s.shtml" % key

        type = TYPE

        category = None
        categoryNames = []
        if content["news"].has_key("newsChannelId"):
            if content["news"]["newsChannelId"] == 52:
                category = 60101
                categoryNames.append("融资")

        if content["news"].has_key("tagName"):
            if content["news"]["tagName"] == '人物':
                category = 60103

        tags = []
        if content.has_key("keywordList") is True and len(content["keywordList"])>0:
            for tag in content["keywordList"]:
                if tag.has_key("keyword") and tag["keyword"] is not None and tag["keyword"].strip() != "" and tag["keyword"] not in tags:
                    tags.append(tag["keyword"])

        title = content["news"]["title"].replace("&quot;","\"")

        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        if collection_news.find_one({"title": title}) is not None:
            logger.info("***************************News existed!!!***********************")
            mongo.close()
            return

        # post = d('div#post_thumbnail> img').attr("src")
        postraw = "http://pic.chinaventure.com.cn/"+content["news"]["coverImg"]
        # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        brief = content["news"]["introduction"]

        post_time = content["news"]["updateAt"]

        news_time = extract.extracttime(str(post_time))
        if news_time is None:
            news_time = datetime.datetime.now()

        article = pq(content["news"]["content"]).html()
        contents = extract.extractContents(newsurl, article)
        # for c in contents:
        #     logger.info(c["data"])
        logger.info("%s, %s, %s, %s -> %s, %s", key, title, news_time, ":".join(tags), category, post)
        # return
        # mongo = db.connect_mongo()
        # collection_news = mongo.article.news
        # if collection_news.find_one({"title": title}) is not None:
        #     logger.info("***************************News existed!!!***********************")
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
            if c["data"].find("img.mp.itc.cn") >= 0:
                continue
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
        dnews["contents"] = dcontents
        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        # if post is None or post.strip() == "":
        #     post = util.get_poster_from_news(dcontents)

        if post is None or post.strip() == "":
            post = util.get_posterId_from_news(dcontents)

        if download_crawler is None:
            dnews["post"] = post
        else:
            dnews["postId"] = post
        # dnews["post"] = post
        dnews["brief"] = brief

        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        # collection_news.insert(dnews)
        mongo.close()
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
        # logger.info("*************DONE*************")
    return




def process(content, flag):
    j = json.loads(content)
    infos = j["data"]["list"]
    logger.info("Got %s news", len(infos))
    cnt = 0
    if len(infos) == 0:
        return cnt
    for info in infos:
        try:
            key = info["news"]["id"]
            logger.info("News id: %s", key)
            # check mongo data if link is existed
            mongo = db.connect_mongo()
            collection_news = mongo.article.news
            item = collection_news.find_one({"source": SOURCE, "key_int": int(key)})
            mongo.close()

            if item is None or flag == "all":
                process_news(None, None, info, None)
                cnt += 1
        except Exception,ex:
            logger.exception(ex)
            continue
    logger.info("Cnt: %s", cnt)
    return cnt

def run(flag, column, listcrawler, newscrawler, concurrent_num):
    global CURRENT_PAGE
    cnt = 1
    while True:
        key = (CURRENT_PAGE-1) * 10

        if flag == "all":
            if key > column["max"]:
                return
        else:
            if cnt == 0 or key > column["max"]:
                return

        CURRENT_PAGE += 1


        url = "https://www.chinaventure.com.cn/cmsmodel/news/jsonListByChannel/-1/%s-10.shtml" % (key)

        while True:
            result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
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
        newscrawler = ListCrawler()
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num)

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
        start_run(1, "incr")