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
import loghelper, db, util, extract, url_helper, json,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

# logger
loghelper.init_logger("crawler_sspai_news", stream=True)
logger = loghelper.get_logger("crawler_sspai_news")

# mongo
# mongo = db.connect_mongo()
# collection_news = mongo.article.news

MAX_PAGE_ALL = 50
CURRENT_PAGE = 0

SOURCE = 13814
TYPE = 60001


class SspaiCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)  # todo!

    # 实现
    def is_crawl_success(self, url, content):
        try:
            json.loads(content)
            return True
        except Exception, ex:
            print Exception, ":", ex
            return False

        return False


class SspaiNewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        if title.find("少数派") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    temp = title.split("-")
    if title.find("页面找不到了") >= 0:
        return False
    return True


def process_news(content, news_key, url, news_posttime):
    # if has_news_content(content):
    if 1:
        download_crawler = download.DownloadCrawler(use_proxy=False)
        j=json.loads(content)
        title = j['title']
        news_time = datetime.datetime.strptime(news_posttime, '%Y-%m-%d %H:%M:%S')

        key = news_key
        tags=[i['title'] for i in j['tags']]

        category = 60102
        postraw = 'https://cdn.sspai.com/' + j['banner']
        brief = j['summary']
        logger.info("%s, %s, %s, %s, %s -> %s, %s", key, title, news_time, brief, ":".join(tags),
                    category, postraw)

        article = j['body']
        # logger.info(article)
        contents = extract.extractContents(url, article)

        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        if collection_news.find_one({"source": SOURCE, "key_int": int(key)}) is not None:
            return
            # collection_news.delete_one({"source": SOURCE, "key_int": int(key)})
        if collection_news.find_one({"title": title, "source": {"$ne": SOURCE}}) is not None:
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
            dcontents.append(dc)
            rank += 1
        dnews["contents"] = dcontents
        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        dnews["brief"] = brief

        # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None
        if post is None or post.strip() == "":
            post = util.get_posterId_from_news(dcontents)

        if download_crawler is None:
            dnews["post"] = post
        else:
            dnews["postId"] = post


        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)

        # collection_news.insert(dnews)
        #
        # logger.info("Done")
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)


def process(content, page_crawler, flag):
    j = json.loads(content.decode("utf-8"))

    cnt = 0
    # logger.info(lis)
    for li in j['list']:
        title = li['title']
        href = 'https://sspai.com/post/' + str(li['id'])
        news_key = href.split("/")[-1]
        news_url = href
        api_url='https://sspai.com/api/v1/articles/%s'%str(li['id'])
        news_posttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(li['released_at']))
        logger.info("%s, %s, %s, %s", title, news_key, news_url, news_posttime)

        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        item = collection_news.find_one({"source": SOURCE, "key_int": int(news_key)})
        newses = list(collection_news.find({"title": title, "source": {"$ne": SOURCE}}))
        mongo.close()

        if item is None or flag == "all":
            craw = True
            for news in newses:
                if news.has_key("type") and news["type"] > 0:
                    craw = False
                    break
            if craw:
                while True:
                    result = page_crawler.crawl(api_url, agent=True)
                    if result['get'] == 'success':
                        # logger.info(result["content"])
                        try:
                            process_news(result['content'], news_key, news_url, news_posttime)
                            cnt += 1
                        except Exception, ex:
                            pass
                            logger.exception(ex)
                        break
    return cnt


def run(flag):
    global CURRENT_PAGE
    crawler = SspaiCrawler()
    page_crawler = SspaiCrawler()
    cnt = 1
    while True:
        key = CURRENT_PAGE * 10
        # logger.info("key=%s", key)
        if flag == "all":
            if key > MAX_PAGE_ALL:
                return
        else:
            if cnt == 0:
                return
            if key > MAX_PAGE_ALL:
                return

        url = 'https://sspai.com/api/v1/articles?offset=%s&limit=10&type=recommend_to_home&sort=recommend_to_home_at' % key

        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                # logger.info(result["content"])
                try:
                    cnt = process(result['content'], page_crawler, flag)
                    logger.info("%s has %s news", url, cnt)
                except Exception, ex:
                    logger.exception(ex)
                    cnt = 0
                break

        CURRENT_PAGE += 1


def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("Sspai news %s start...", flag)
        CURRENT_PAGE = 0
        run(flag)
        logger.info("Sspai news %s end.", flag)

        if flag == "incr":
            time.sleep(60 * 15)  # 5hour
        else:
            return
            # gevent.sleep(86400*3)   #3 days


if __name__ == "__main__":
    flag = "incr"
    concurrent_num = 1

    if len(sys.argv) > 1:
        flag = sys.argv[1]

    start_run(concurrent_num, flag)
