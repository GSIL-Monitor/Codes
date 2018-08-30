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
loghelper.init_logger("crawler_vilcanpost_news", stream=True)
logger = loghelper.get_logger("crawler_vilcanpost_news")

NEWSSOURCE = "vilcanpost"
RETRY = 3
TYPE = 60004
SOURCE =13886
URLS = []
CURRENT_PAGE = 1
linkPattern = "/\d+/.*"
Nocontents = [
]
columns = [
    {"column": "geek", "max": 1},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=10):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

        # 实现

    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
        title = d('head> title').text().strip()
        # logger.info("title: %s url: %s", title, url)
        if title.find("Geek") >= 0:
            return True
        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        if content.find('article-container') >= 0:
            return True
        return False


def process_news(column,  content, msg, download_crawler):
    download_crawler = download.DownloadCrawler(use_proxy=False)
    d = pq(html.fromstring(content.decode("utf-8", "ignore")))

    title = msg['title']
    newsurl = msg['link']
    brief = msg['brief']
    newspost = msg['post']
    post_time = msg['newsDate']

    category = None
    categoryNames = []

    key = re.search('https://vulcanpost.com/(\d+)/.*',newsurl).group(1)
    type = TYPE

    (posturl, width, height) = parser_mysql_util.get_logo_id_new(newspost, download_crawler, SOURCE, key, "news")
    if posturl is not None:
        post = str(posturl)
    else:
        post = None

    tags = []

    try:
        news_time = datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S")
        logger.info("news-time: %s", news_time)
    except Exception, e:
        logger.info(e)
        news_time = datetime.datetime.now()

    article = d('div.entry').html()
    contents = extract.extractContents(newsurl, article, document=False)


    logger.info("%s, %s, %s, %s -> %s, %s", key, title, news_time, ":".join(tags), category, brief)

    flag, domain = url_helper.get_domain(newsurl)
    dnews = {
        "date": news_time - datetime.timedelta(hours=8),
        "title": title,
        "link": newsurl,
        "createTime": datetime.datetime.now(),
        "source": SOURCE,
        "key": key,
        "key_int": None,
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
        if c["data"].find("Also Read") >= 0 or c['data'].find('function()') >= 0:
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
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
        pass
    return

def crawler_news(column, crawler, msg, download_crawler):
    retry = 0
    newsurl = msg['link']
    while True:
        result = crawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column,  result['content'], msg, download_crawler)
            except Exception,ex:
                logger.exception(ex)
                raise ValueError('something wrong at process nrews')
            break

        retry += 1
        if retry > 20:
            break


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL, download_crawler)


def process(content, flag):
    if content.find("alm-listing") >= 0:
        d = pq(html.fromstring(content.decode("utf-8")))
        for a in d('div.alm-listing> article.story'):
            try:
                link =  d(a)('a').attr("href")
                title = d(a)('h2').text()
                ndate = d(a)('div.author> div.meta> span.timestamp').attr('title')
                brief = d(a)('div.excerpt> p').text()
                post = re.search('url\((.*?)\);',d(a)('div.thumbnail> figure').attr('style')).group(1)
                # print(link, title, ndate, brief, post)
                if re.search(linkPattern, link) and title is not None and title.strip() != "":
                    logger.info("Link: %s is right news link: %s|%s", link, title, ndate)

                    linknew = 'https://vulcanpost.com' + link
                    mongo = db.connect_mongo()
                    collection_news = mongo.article.news
                    item = collection_news.find_one({"link": linknew})

                    item2 = collection_news.find_one({"title": title})
                    mongo.close()

                    if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                        linkmap = {
                            "link": linknew,
                            "post": post,
                            "newsDate": ndate,
                            'brief':brief,
                            'title':title
                        }
                        URLS.append(linkmap)

                else:
                    pass
            except Exception, e:
                logger.info(e)
                logger.info("cannot get link")
    return len(URLS)


def run(flag, column, listcrawler, newscrawler, concurrent_num):
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

        url = "https://vulcanpost.com/category/geek/"

        while True:
            result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        # logger.info(URLS)
                        # threads = [gevent.spawn(run_news, column, newscrawler, download_crawler=None) for i in xrange(concurrent_num)]
                        # gevent.joinall(threads)
                        run_news(column, newscrawler, download_crawler=None)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break


@traceback_decorator.try_except
def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            time.sleep(60*60*6)
        else:
            return


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
        #     crawler_news({"column":"geek"}, NewsCrawler(), link, None, '2018-07-17T05:31:39', download_crawler)
    else:
        start_run(1, "incr")





