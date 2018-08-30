# -*- coding: utf-8 -*-
import os, sys, datetime
from lxml import html
from pyquery import PyQuery as pq
import urllib
# import gevent
# from gevent.event import Event
# from gevent import monkey; monkey.patch_all()
import time
import json

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,extract,db,util,url_helper,desc_helper, extractArticlePublishedDate,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_lieyun_news", stream=True)
logger = loghelper.get_logger("crawler_lieyun_news")

# #mongo
# mongo = db.connect_mongo()
# collection_news = mongo.article.news

newsid =[]
b_id =1

SOURCE = 13803

class LieyunCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content.find("archives") >= 0:
            return True
        # logger.info(content)
        return False

class LieyunNewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8","ignore")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " " + url)

        if title.find("猎云网") >= 0:
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
        if len(j["content"])> 0:
            return True
        else:
            logger.info("No content: %s", content)
    else:
        logger.info("Fail to get content")
    return False

def has_news_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    temp = title.split("|")
    if len(temp) != 2:
        return False
    if temp[1].strip() != "猎云网":
        return False
    if temp[0].strip() == "":
        return False
    return True


def process_news(item, url, content):
    if has_news_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        d = pq(html.fromstring(content.decode("utf-8","ignore")))
        titleraw = d('head> title').text().strip()
        temp = titleraw.split("|")
        title = temp[0].strip()
        # title = d('h1.article-title').text().strip()
        if item is None:
            news_time = extractArticlePublishedDate.extractArticlePublishedDate(url, content)
            if news_time is None:
                news_time = datetime.datetime.now()
            key = url.split("/")[-1].replace(".html", "")
        else:
            news_time = extract.extracttime(item["post_date"])
            if news_time is None:
                news_time = datetime.datetime.now()

            key = item["key"]

        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        if collection_news.find_one({"source": SOURCE, "key_int": int(key)}) is not None:
            mongo.close()
            return
            # collection_news.delete_one({"source": SOURCE, "key_int": int(key)})

        if collection_news.find_one({"title": title, "source": {"$ne": SOURCE}}) is not None:
            mongo.close()
            return
            # collection_news.delete_many({"title": title, "source": {"$ne": SOURCE}})
        mongo.close()

        #column = d('div.main-text> div.addd-fl-tag').text()
        # column = d('div.article-source> span.article-tag-top').text()
        if isinstance(item, dict):
            column = item["columns"]
        else:
            column = None
        brief = d('div.article-digest').text()
        if column is not None and column.strip() != "":
            tags = column.split()
        else:
            tags = []

        categoryNames = []
        if "课堂" in tags or "专栏" in tags:
            TYPE = 60003
            category = 60107
        else:
            TYPE = 60001
            if "融资汇" in tags:
                category = 60101
                categoryNames.append("融资")
            elif "早期项目" in tags:
                categoryNames.append("早期项目")
                if title.find("融资") >= 0:
                    category = 60101
                    categoryNames.append("融资")
                else:
                    category = 60102
            elif "A轮后" in tags and title.find("融资") >= 0:
                category = 60101
                categoryNames.append("融资")
            elif "大公司" in tags:
                category = 60105
                categoryNames.append("大公司")
            elif "投行" in tags:
                category = 60104
                categoryNames.append("投资人观点")
            else:
                category = None

        # tagsmore = d('div.article-tag> ul').text().split()
        # for a in tagsmore:
        #     if a not in tags:
        #         tags.append(a)
        if isinstance(item, dict):
            postraw = item["post"]
            # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
            (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
        else:
            posturl = None
        if posturl is not None:
            post = str(posturl)
        else:
            post = None
        #article_img = d('div.article> div.main-text> p> img').attr('src')

        logger.info("%s, %s, %s, %s, %s, %s", key, title, news_time, TYPE, category, ":".join(tags))
        article = d('div.article-main > div.main-text').html()
        #logger.info(article)
        contents = extract.extractContents(url, article, document=False)

        # dcontents = []
        # if article_img is not None:
        #     dc = {
        #         "rank": 1,
        #         "content": "",
        #         "image": "",
        #         "image_src": article_img,
        #     }
        #     dcontents.append(dc)
        #     logger.info(article_img)
        # mongo = db.connect_mongo()
        # collection_news = mongo.article.news
        # if collection_news.find_one({"source": SOURCE, "key_int": int(key)}) is not None:
        #     mongo.close()
        #     return
        #     # collection_news.delete_one({"source": SOURCE, "key_int": int(key)})
        #
        # if collection_news.find_one({"title": title, "source": {"$ne": SOURCE}}) is not None:
        #     mongo.close()
        #     return
        #     # collection_news.delete_many({"title": title, "source": {"$ne": SOURCE}})
        # mongo.close()
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
            "key_int": int(key),
            "type": TYPE,
            "original_tags": tags,
            "processStatus":0,
            "companyId": None,
            "companyIds":[],
            "category": category,
            "domain": domain,
            # "sectors": [20]
        }
        dcontents = []
        rank = 1
        for c in contents:
            if column is not None and c["data"].strip() == column.strip():
                continue
            if c["data"].find("default/images/theme/company_code.jpg") >= 0:
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
            dcontents.append(dc)
            rank += 1
        dnews["contents"] = dcontents
        if brief is None or brief.strip() == "" or desc_helper.check_desc(brief,2) is False:
            brief = util.get_brief_from_news(dcontents)
        # post = util.get_poster_from_news(dcontents)
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
        # exit()
        # collection_news.insert(dnews)
        #g.latestIncr()

def run_news(crawler, outlink=None):

    while True:
        if outlink is None:
            if len(newsid) ==0:
                return
            nitem = newsid.pop(0)

            url = "http://www.lieyunwang.com/archives/%s" % nitem["key"]
        else:
            url = outlink
            nitem = None
        maxretry = 0
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["redirect_url"])
                try:
                    process_news(nitem, url, result['content'])
                except Exception,ex:
                    logger.exception(ex)
                break
            if maxretry > 20: break
            maxretry += 1

        if outlink is not None: return



def process_page(content,flag):
    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    # bid = None
    # j = json.loads(content)
    # infos = j["content"]
    d = pq(html.fromstring(content.decode("utf-8", "ignore")))


    for div in d('div.article-bar.clearfix'):
        try:

            key = pq(div)('a.lyw-article-title').attr("href").split("/")[-1]
            title = pq(div)('a.lyw-article-title').text()
            date = pq(div)('span.timestamp').text()
            cat = pq(div)('span.article-tag').text()
            post = pq(div)('img.img-fuil').attr("src")
            logger.info("%s, %s, %s, %s, %s", key, date, title, cat, post)

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
                        "post_date": date,
                        "columns" : cat,
                        "post": post
                    }
                    newsid.append(item)
        except Exception, E:
            logger.info(E)
            logger.info("wrong to get link")

        mongo.close()
    return newsid

def start_run(flag):
    global b_id
    while True:
        logger.info("Lieyun news %s start...", flag)

        crawler = LieyunCrawler()
        while True:
            page_url = "http://www.lieyunwang.com/latest/p%s.html" % b_id
            headers = {"AjaxFilter": "1"}
            result = crawler.crawl(page_url, agent=True, headers=headers)
            if result['get'] == 'success':
                newsid = process_page(result["content"],flag)
                if len(newsid) > 0:
                    logger.info("crawler news details")
                    logger.info(newsid)
                    # threads = [gevent.spawn(run_news, LieyunNewsCrawler()) for i in xrange(1)]
                    # gevent.joinall(threads)
                    run_news(LieyunNewsCrawler())
                    # exit()
                    b_id += 1
                    continue
                else:
                    b_id = 1

                break


        logger.info("Lieyun news %s end.", flag)

        if flag == "incr":
            time.sleep(60*5)        #10 minutes
        else:
            time.sleep(86400*3)   #3 days


if __name__ == "__main__":

    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "all":
            start_run("all")
        elif param == "incr":
            start_run("incr")
        else:
            run_news(LieyunNewsCrawler(), outlink=param)
    else:
        start_run("incr")