# -*- coding: utf-8 -*-
import os, sys, re
import datetime, time
from lxml import html
from pyquery import PyQuery as pq
from pymongo import MongoClient

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db,util,extract,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_techcrunch_news", stream=True)
logger = loghelper.get_logger("crawler_techcrunch_news")

#mongo
#mongo = db.connect_mongo()
#collection_news = mongo.article.news

MAX_PAGE_ALL = 300
CURRENT_PAGE = 1

SOURCE = 13815
TYPE = 60004

class TcCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=40):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("TechCrunch") >= 0:
            return True

        return False

class TcNewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=40):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        if title.find("TechCrunch") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    temp = title.split("|")
    if title.find("Page not found") >= 0:
        return False
    if len(temp) < 2:
        return False
    if temp[-1].strip() != "TechCrunch":
        return False
    if temp[0].strip() == "":
        return False
    return True


def process_news(content, news_key, url, news_posttime):
    if has_news_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        d = pq(html.fromstring(content.decode('utf-8')))
        title = d('header.article-header>h1').text().strip()
        if title is None or title.strip() == "":
            logger.info("wrong title for url: %s", url)
            return
        post_time = pq(content)("meta[name='sailthru.date']").attr("content")
        news_time = datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=15)

        key = news_key
        try:
            postraw = pq(content)("meta[property='og:image']").attr("content")
            if postraw.find("techcrunch.opengraph.default.png")>=0:
                postraw = None
        except:
            postraw = None
        # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        divtags = d('div.tags> div.tag-item')
        tags = [pq(divtag)('a.tag').text().strip() for divtag in divtags if pq(divtag)('a.tag').text().strip() is not None]
        category = None
        logger.info("%s, %s, %s, %s, %s -> %s", key, title, post_time, news_time, ":".join(tags),category)

        article = d('div.article-entry.text').html()
        # logger.info(article)
        contents = extract.extractContents(url, article)

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
            "processStatus": 1,
            # "companyId": None,
            "companyIds": [],
            "category": category,
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
                    (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler, SOURCE,
                                                                                key, "news")
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
        brief = util.get_brief_from_news(dcontents)
        # if post is None or post.strip() == "" or post.find("techcrunch.opengraph.default.png")>=0:
        #     post = util.get_poster_from_news(dcontents)
        #
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
        if len(dcontents) > 0:
            # mongo = db.connect_mongo()
            # collection_news = mongo.article.news
            # collection_news.insert(dnews)
            # mongo.close()
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s", nid)

        logger.info("Done")


def process(content, page_crawler, flag):
    d = pq(html.fromstring(content))
    lis = d("ul#river1> li.river-block")
    lis1 = d("ul#river2> li.river-block")
    if len(lis1)>= 0:
        lis.extend(lis1)
    cnt = 0
    #logger.info(lis)
    for li in lis:
        l = pq(li)
        try:
            title = l("h2.post-title> a").text().strip()
            href = l("h2.post-title> a").attr("href").strip()
            news_key = l('li.river-block').attr("id")
        except:
            logger.info("No id for:")
            #logger.info(l)
            continue

        if title.find("Crunch Report") >= 0:
            continue
        news_url = href
        news_posttime = l('div.byline> time.timestamp').attr('datetime')
        logger.info("%s, %s, %s, %s", title, news_key, news_url, news_posttime)

        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        item = collection_news.find_one({"source":SOURCE, "key_int":int(news_key)})
        newses = list(collection_news.find({"title": title, "source": {"$ne": SOURCE}}))
        mongo.close()
        # cnt +=1
        if item is None or flag == "all":
            craw = True
            for news in newses:
                if news.has_key("type") and news["type"] > 0:
                    craw = False
                    break
            if craw:
                retry_times = 0
                while True:
                    result = page_crawler.crawl(news_url, agent=True)
                    if result['get'] == 'success':
                        #logger.info(result["content"])
                        try:
                            process_news(result['content'], news_key, news_url, news_posttime)
                            cnt += 1
                        except Exception,ex:
                            pass
                            logger.exception(ex)
                        break
                    retry_times += 1
                    if retry_times > 15:
                        break
    return cnt



def run(flag):
    global CURRENT_PAGE
    crawler = TcCrawler()
    page_crawler = TcNewsCrawler()
    cnt = 1
    while True:
        key = CURRENT_PAGE
        #logger.info("key=%s", key)
        if flag == "all":
            if key > MAX_PAGE_ALL:
                return
        else:
            if cnt == 0:
                return
            if key > MAX_PAGE_ALL:
                return

        CURRENT_PAGE += 1
        if key == 1:
            url = "https://techcrunch.com/"
        else:
            url = "https://techcrunch.com/page/%s/" % key
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    cnt = process(result['content'], page_crawler, flag)
                    logger.info("%s has %s news", url, cnt)
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break



def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("TechCrunch news %s start...", flag)
        CURRENT_PAGE = 1
        run(flag)
        logger.info("TechCrunch news %s end.", flag)

        if flag == "incr":
            time.sleep(60*45)        #45mins
        else:
            return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    flag = "incr"
    concurrent_num = 1

    if len(sys.argv) > 1:
        flag = sys.argv[1]

    start_run(concurrent_num, flag)