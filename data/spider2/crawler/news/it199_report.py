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
loghelper.init_logger("crawler_it199_news", stream=True)
logger = loghelper.get_logger("crawler_it199_news")

NEWSSOURCE = "it199"
RETRY = 30
TYPE = 60006
SOURCE =13835
URLS = []
CURRENT_PAGE = 1
linkPattern = "199it.com/archives/\d+.html"
Nocontents = [
]
columns = [
    {"column": "report", "max": 5},
    {"column": "cbinsights", "max": 5}
    # {"column": "news", "max": 3, "category": None},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content.decode("utf-8","ignore")))

        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("研究报告 | 互联网数据资讯中心-199IT") >= 0:
            return True
        if title.find("199IT") >= 0:
            return True
        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=20):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    #实现<div class="tabCont
    def is_crawl_success(self,url,content):

        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("199IT") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    temp = title.split("|")
    if len(temp) < 2:
        return False
    if temp[0].strip() == "":
        return False
    return True


def process_news(column, newsurl, content, newspost, download_crawler):
    if has_news_content(content):

        d = pq(html.fromstring(content.decode('utf-8', "ignore")))

        key = newsurl.split("/")[-1].replace(".html","")

        type = TYPE

        category = None

        title = d('div#content> article> header> h1').text().strip()
        [author, cleanTitle] = clean_title(title)

        tags = []
        # articletags = d("meta[name='keywords']").attr("content")
        # if articletags is not None:
        #     for tag in articletags.split(","):
        #         if tag is not None and tag.strip() != "" and tag not in tags and tag != title:
        #             tags.append(tag)

        # posturl = parser_mysql_util.get_logo_id(newspost, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(newspost, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        brief = d("meta[name='description']").attr("content")
        news_time = None
        post_time = d('li.post-time> time').text()
        logger.info(post_time)

        if post_time.find("月") >=0:
            dt = datetime.date.today()
            today = datetime.datetime(dt.year, dt.month, dt.day)
            if datetime.datetime.strptime(post_time, "%Y年%m月%d日") == today:
                news_time = datetime.datetime.now()

        if news_time is None:
            if post_time is not None:
                news_time = datetime.datetime.strptime(post_time, "%Y年%m月%d日")
            else:
                news_time = datetime.datetime.now()

        article = d('div#content> article> div.entry-content').html()
        # logger.info(article)
        contents = extract.extractContents(newsurl, article, document=False)


        logger.info("%s, %s, %s, %s -> %s, %s. %s", key, title, news_time, ":".join(tags), category, brief, post)
        # exit()
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
            "type": type,
            "original_tags": tags,
            "processStatus": 1,
            # "companyId": None,
            "companyIds": [],
            "category": category,
            "domain": domain,
            "author": author,
            "cleanTitle": cleanTitle,
            "categoryNames": []
            # "sectors": [20]
        }
        dcontents = []
        rank = 1
        for c in contents:
            if c["data"].find("报告下载")>=0 and c["data"].find("回复关键词")>=0 or c["data"].find("原创编译")>=0 or \
                            c["data"].find("199IT感谢您的支持！") >= 0:
                continue
            if c["data"].find("其它年份报告，请点击下载")>=0 or c["data"].find("var wum")>=0 or \
                    c["data"].find("原创编译自") >=0 or c["data"].find("更多阅读")>=0:
                break

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

            logger.info(c["data"])
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
        # mid = collection_news.insert(dnews)
        mongo.close()
        # logger.info("*************DONE*************%s",mid)
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
    return


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL["post"], download_crawler)

def crawler_news(column, crawler, newsurl, newspost, download_crawler):
    retry = 0
    while True:
        result = crawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'], newspost, download_crawler)
            except Exception,ex:
                logger.info("EEEEEEEEEE")
                logger.exception(ex)
            break
        if retry > RETRY: break
        retry += 1


def clean_title(title):
    if title is None: return [None, None]
    title = title.replace("：",":").replace("（附下载）","").replace("（附报告）","")
    temp = title.split(":")
    if len(temp) == 1:
        return [None, title]
    elif temp[0].strip() != "":
        return [temp[0], title.replace(temp[0],"").replace(":","")]
    else:
        return [None, None]




def process(content, flag):
    d = pq(html.fromstring(content.decode("utf-8","ignore")))
    for li in d('div#content> article'):
        try:
            link = d(li)('div.entry-content> h2> a').attr("href").strip()
            # logger.info(link)
            if re.search(linkPattern, link) and link.find("http") >= 0:
                logger.info("Link: %s is right news link", link)
                title = d(li)('div.entry-content> h2> a').text()
                post = d(li)('div.post-img> div> a> img').attr("src")
                if post is not None: post = post.strip()
                [author, cleanTitle] = clean_title(title)
                logger.info("title: %s, author: %s, cleanTitle: %s, post: %s", title, author, cleanTitle, post)
                mongo = db.connect_mongo()
                collection_news = mongo.article.news
                item = collection_news.find_one({"link": link})
                item2 = collection_news.find_one({"title": title})
                item3 = collection_news.find_one({"author": author, "cleanTitle": cleanTitle})
                mongo.close()


                if ((item is None and item2 is None and item3 is None) or flag == "all") and link not in URLS:
                    linkmap = {
                        "link": link,
                        "post": post
                    }
                    URLS.append(linkmap)
                else:
                    logger.info("link existed")

            else:
                # logger.info(link)
                pass
        except Exception, e:
            logger.info(e)
            logger.info("cannot get link")
    return len(URLS)


def run(flag, column, listcrawler, newscrawler, concurrent_num, download_crawler):
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

        url = "http://www.199it.com/archives/category/report/page/%s" % key
        if column["column"] == "cbinsights":
            url = "http://www.199it.com/archives/tag/cb-insights/page/%s" % key
        while True:
            result = listcrawler.crawl(url,agent=True)

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
        # download_crawler = None
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num, download_crawler)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            gevent.sleep(60*50)        #30 minutes
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
            # download_crawler = None
            crawler_news({"column": "report", "max": 5}, NewsCrawler(), link, None, download_crawler)
    else:
        start_run(1, "incr")