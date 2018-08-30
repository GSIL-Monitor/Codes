# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, time
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download, traceback_decorator

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_techinasia_news", stream=True)
logger = loghelper.get_logger("crawler_techinasia_news")

NEWSSOURCE = "techinasia"
RETRY = 3
TYPE = 60004
SOURCE =13882
URLS = []
CURRENT_PAGE = 1
# linkPattern = "www.pintu360.com/a\d+.html"
Nocontents = [
]
columns = [
    {'column':'posts','max':1},

]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=10):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

        # 实现
    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j_content = json.loads(content)
            except Exception, E:
                logger.info(E)
                return False
            if j_content.has_key("posts") is True:
                return True
        return False

def process_news(content, download_crawler):
    download_crawler = download.DownloadCrawler(use_proxy=False)

    category = None
    categoryNames = []

    key = content['id']
    type = TYPE
    title = content['title']

    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    if collection_news.find_one({"title": title}) is not None:
        mongo.close()
        return
    newspost = content.get('featured_image').get('source')
    (posturl, width, height) = parser_mysql_util.get_logo_id_new(newspost, download_crawler, SOURCE, key, "news")
    if posturl is not None:
        post = str(posturl)
    else:
        post = None
    # logger.info(post)

    tags = []
    for tag in content['tags']:
        tags.append(tag['name'])
    brief = content['seo']['description']
    try:
        post_time = content['modified_gmt']
        news_time = None
        if post_time.find('T'):
            post_time = post_time.replace('T',' ')
            news_time = extract.extracttime(post_time)
            logger.info("news-time: %s", news_time)
    except Exception, e:
        logger.info(e)
        news_time = datetime.datetime.now()

    logger.info("%s, %s, %s, %s -> %s, %s", key, title, news_time, ":".join(tags), category, brief)

    newsurl = content['link']
    article = pq(html.fromstring(content['content'].decode('utf-8', 'ignore'))).html()
    contents = extract.extractContents(newsurl, article, document=False)
    flag, domain = url_helper.get_domain(newsurl)
    dnews = {
        "date": news_time - datetime.timedelta(hours=8),# todo time
        "title": title,
        "link": newsurl,
        "createTime": datetime.datetime.now(),
        "source": SOURCE,
        "key": key,
        "key_int": int(key),
        "type": type,
        "original_tags": tags,
        "processStatus": 1,
        # "companyId": None,
        "companyIds": [],
        "category": category,
        "domain": domain,
        "categoryNames": categoryNames
    }
    dcontents = []
    rank = 1
    for c in contents:
        # if c["data"].find("fromgeek.com/awards/") >= 0 or \
        #         c["data"].find("http://www.fromgeek.com/uploadfile/2017/0430/20170430328184.jpg") >= 0:
        #     continue

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
                (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler, SOURCE, key,
                                                                            "news")
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
    # logger.info(json.dumps(dnews,ensure_ascii=False,indent=2,cls=util.CJsonEncoder))
    if title is not None and len(contents) > 0:
        # logger.info("*************DONE*************")
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
        pass
    return

def run_news(download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)
        process_news(URL, download_crawler)

def process(content, flag):
    posts = json.loads(content)['posts']
    logger.info("Got %s news", len(posts))
    cnt = 0
    if len(posts) == 0:
        return cnt
    for post in posts:
        try:
            title = post['title']
            link = post['link']
            mongo = db.connect_mongo()
            collection_news = mongo.article.news
            item = collection_news.find_one({"title": title})
            item2 = collection_news.find_one({"link": link})
            mongo.close()
            if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                URLS.append(post)
        except Exception,ex:
            logger.exception(ex)
            continue
    return len(URLS)


def run(flag, column, listcrawler):
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

        url = "https://www.techinasia.com/wp-json/techinasia/2.0/%s?page=%d&per_page=10"%(column['column'], key)

        while True:
            result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        # logger.info(URLS)

                        run_news(download_crawler=None)

                except Exception, ex:
                    logger.exception(ex)
                    cnt = 0
                break

@traceback_decorator.try_except
def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            time.sleep(60 * 60 * 3)
        else:
            return
            # gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(1, "all")
        # else:
        #     link = param
        #     download_crawler = None
        #     crawler_news({"column":"None"}, NewsCrawler(), link, None, '2018-05-07 18:24', download_crawler)
    else:
        start_run(1, "incr")

