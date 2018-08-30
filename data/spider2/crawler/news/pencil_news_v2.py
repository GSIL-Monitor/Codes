# -*- coding: utf-8 -*-
import os, sys, datetime, re, json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

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
loghelper.init_logger("crawler_pencil_news", stream=True)
logger = loghelper.get_logger("crawler_pencil_news")

NEWSSOURCE = "Pencil"
RETRY = 3
TYPE = 60001
SOURCE =13800
URLS = []
CURRENT_PAGE = 1
linkPattern = "/article/\d+"
Nocontents = [
]
columns = [
    {"column": None, "max": 3},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
                # logger.info(j)
            except:
                return False

            if j.has_key("message") is True and j["message"] == "SUCCESS":
                return True

        return False

class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("页面未找到404") >= 0:
            return False
        if title.find("您所请求的网址（URL）无法获取") >= 0:
            return False
        if title.find("403 Forbidden") >= 0:
            return False
        if title.find("ERROR: The requested URL could not be retrieved") >= 0:
            return False
        if content.find("421 Server too busy") >= 0:
            return False
        if content.find("铅笔道") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    # logger.info("title: " + title)

    if title.find("502 Bad Gateway") >= 0:
        return False
    if title.find("页面未找到404") >= 0:
        # logger.info(content)
        return False
    if title.find("您所请求的网址（URL）无法获取") >= 0:
        # logger.info(content)
        return False
    return True


def process_news(column, newsurl, content, newspost, download_crawler, force):
    if has_news_content(content):
        main = pq(content)('div.article_content')
        d = pq(main)

        key = newsurl.split("/")[-1].replace(".html", "")

        title = pq(content)('head> title').text().strip()
        logger.info("title: %s",title)
        # title = d('h1#article_title').text()

        brief = pq(content)("meta[name='description']").attr("content")
        # post_time =pq(content)("meta[property='article:published_time']").attr("content").split("+")[0]
        # news_time = datetime.datetime.strptime(post_time, "%Y-%m-%dT%H:%M:%S")
        result = util.re_get_result("var publishTime = new Date\(\"(.*?)\"\)", content)
        if result:
            post_time, = result
            news_time = datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S")
        else:
            logger.info("incorrcet post time")
            logger.info(content)
            # exit()
            return

        categoryNames = []
        contents = extract.extractContents(newsurl, d.html())
        if title.find("融资") >= 0 or title.find("获投") >= 0:
            category = 60101
            categoryNames.append("融资")
        else:
            category = None
        tags = []

        articletags = pq(content)("meta[name='keywords']").attr("content").replace("；",",")
        if articletags is None:
            logger.info(content)

        else:
            for tag in articletags.split(","):
                if tag is not None and tag.strip() != "" and tag not in tags:
                    tags.append(tag)

        logger.info("%s, %s, %s, %s, %s, %s", key, title, news_time, category, ":".join(tags), brief)

        if force is True:
            mongo = db.connect_mongo()
            collection_news = mongo.article.news
            collection_news.delete_many({"source": SOURCE, "key_int": int(key)})
            collection_news.delete_many({"title": title})
            mongo.close()

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
            "type": TYPE,
            "original_tags": tags,
            "processStatus": 0,
            # "companyId": None,
            "companyIds": [],
            "category": category,
            "domain": domain,
            "categoryNames": categoryNames
        }


        #pjtables
        pjcontents = []
        trs =  pq(content)('div.proj_table> table> tr')
        logger.info("*****len of trs %s", len(trs))
        for tr in trs:
            logger.info(tr)
            co = pq(tr).text()
            logger.info(co)
            if co is not None and co.strip() != "": pjcontents.append(co.replace(" ",":"))


        dcontents = []
        rank = 1
        for c in contents:
            if c["data"] == "/The End/":
                break
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
            # logger.info(c["data"])
            dcontents.append(dc)
            rank += 1

        for pjc in pjcontents:
            dc = {
                "rank": rank,
                "content": pjc,
                "image": "",
                "image_src": "",
            }
            dcontents.append(dc)
            logger.info(pjc)
            rank += 1
        dnews["contents"] = dcontents
        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        # post = util.get_poster_from_news(dcontents)
        # dnews["post"] = post

        # if post is None or post.strip() == "":
        post = util.get_posterId_from_news(dcontents)

        if download_crawler is None:
            dnews["post"] = post
        else:
            dnews["postId"] = post
        dnews["brief"] = brief
        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        # id =collection_news.insert(dnews)
        # logger.info("***********id: %s", id)
        # logger.info("*************DONE**************")
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
        mongo.close()
    return


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL["post"], download_crawler)

def crawler_news(column, crawler, newsurl, newspost, download_crawler, force=False):
    headers = {"Cookie": "_ga=fff"}
    maxretry = 0
    while True:
        result = crawler.crawl(newsurl, agent=True, headers=headers)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'], newspost, download_crawler, force)
            except Exception,ex:
                logger.exception(ex)
            break
        if maxretry >200:
            break
        maxretry+=1



def process(content, flag):
    j = json.loads(content)
    infos = j["data"]["articles"]
    logger.info("Got %s news", len(infos))
    cnt = 0
    if len(infos) == 0:
        return cnt
    for info in infos:
        try:
            key = info["article_info"]["article_id"]
            logger.info("News id: %s", key)
            link = "https://www.pencilnews.cn/p/%s.html" % (key)

            mongo = db.connect_mongo()
            collection_news = mongo.article.news
            item = collection_news.find_one({"source": SOURCE, "key_int": int(key)})
            item2 = collection_news.find_one({"link": link})
            mongo.close()

            if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                linkmap = {
                    "link": link,
                    "post": None,
                }
                URLS.append(linkmap)
        except Exception, ex:
            logger.exception(ex)
            continue
    return len(URLS)

def run(flag, column, listcrawler, newscrawler, concurrent_num, download_crawler):
    global CURRENT_PAGE
    cnt = 1
    while True:
        key = CURRENT_PAGE - 1

        if flag == "all":
            if key > column["max"]:
                return
        else:
            if cnt == 0 or key > column["max"]:
                return

        CURRENT_PAGE += 1

        url = 'https://api.pencilnews.cn/articles?page=%s&page_size=20' % (key)
        headers = {"Cookie": "_ga=fff"}

        while True:
            result = listcrawler.crawl(url,agent=True, headers=headers)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        threads = [gevent.spawn(run_news, column, newscrawler, download_crawler) for i in xrange(concurrent_num)]
                        gevent.joinall(threads)
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
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num, download_crawler)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            gevent.sleep(60*8)        #30 minutes
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
            crawler_news({}, NewsCrawler(), link, None, download_crawler, force=True)
    else:
        start_run(1, "incr")