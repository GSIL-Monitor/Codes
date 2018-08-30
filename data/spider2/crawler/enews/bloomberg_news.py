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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_bloomberg_news", stream=True)
logger = loghelper.get_logger("crawler_bloomberg_news")

NEWSSOURCE = "bloomberg"
RETRY = 3
TYPE = 60004
SOURCE =13893
URLS = []
CURRENT_PAGE = 1
linkPattern = "\w+"
Nocontents = [
]
columns = [
    # {"column": "jmd", "max": 2},
    # {"column": "investment", "max": 1},
    {"column": "technology", "max": 1},

    # {"column": "Recommend", "max": 2},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=40):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)
        self.pps = []

        # 实现
    def get_proxy(self, http_type):
        if len(self.pps) > 0:
            proxy_ip = self.pps.pop(0)

        else:
            proxy = {'type': "HTTPS", 'country':'国外','anonymous':'high'}

            while len(self.pps) == 0:
                logger.info("Start proxy_pool.get_single_proxy %s", self.num)
                proxy_ips = proxy_pool.get_single_proxy_x(proxy, 1000)
                if len(proxy_ips) == 0:
                    logger.info("proxy_pool.get_single_proxy return None")

                    time.sleep(30)
                else:
                    for pi in proxy_ips:
                        self.pps.append(pi)
            proxy_ip = self.pps.pop(0)
        logger.info("ppps: %s", proxy_ip)
        return proxy_ip

    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
           return False

        d = pq(html.fromstring(content.decode("utf-8","ignore")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("Bloomberg") >= 0:
            return True

        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=40):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    #实现
    def is_crawl_success(self,url,content):
        # if content.find("</html>") == -1:
        #    return False

        if content.find("e27") >= 0:
            return True

        return False


def has_news_content(content):
    # d = pq(html.fromstring(content.decode("utf-8","ignore")))
    # title = d('head> title').text().strip()
    # # temp = title.split("–")
    # # logger.info("title:%s %s", title, len(temp))
    # if len(title) < 2 or title == "":
    #     return False
    return True

def process_news(column, newsurl, content, newspost, topic, download_crawler):
    if has_news_content(content):
        # logger.info('here')
        download_crawler = download.DownloadCrawler(use_proxy=False)
        # logger.info(content)
        d = pq(html.fromstring(content.decode("utf-8","ignore")))

        category = None
        categoryNames = []

        key = newsurl.split("/")[-1].replace(".html", "")

        type = TYPE

        title = d('h1.lede-text-v2__hed').text().strip()

        newspost = d('header> img.wp-post-image').attr("src")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(newspost, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        tags = []
        # articletags = d("meta[name='keywords']").attr("content")
        # if articletags is not None:
        #     for tag in articletags.split(","):
        #         if tag is not None and tag.strip() != "" and tag not in tags and tag != title:
        #             tags.append(tag)
        # try:
        #     brief = d('h2.post-subheading').text().strip()
        # except:
        brief = None

        try:
           post_time = d("time.article-timestamp").eq(0).attr("datetime")

           logger.info(post_time)
           news_time = datetime.datetime.strptime(post_time.split(".")[0], "%Y-%m-%dT%H:%M:%S")
           logger.info("news-time: %s", news_time)
        except Exception, e:
            logger.info(e)
            news_time = datetime.datetime.now()

        article = d('div.fence-body').html()
        contents = extract.extractContents(newsurl, article)


        logger.info("%s, %s, %s, %s -> %s, %s", key, title, news_time, ":".join(tags), category, brief)

        flag, domain = url_helper.get_domain(newsurl)
        dnews = {
            # "date": news_time - datetime.timedelta(hours=8),
            "date": news_time,
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
        processStatus = 0
        dcontents = []
        rank = 1
        for c in contents:
            if c["data"].find("Related Stories") >= 0:
                # logger.info("here")
                break

            # if c["data"].find("Continue reading this story with a subscription to DealStreetAsia") >= 0:
            #     processStatus = -5
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
                    continue
                    # (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler, SOURCE, key, "news")
                    # if imgurl is not None:
                    #     dc = {
                    #         "rank": rank,
                    #         "content": "",
                    #         "image": str(imgurl),
                    #         "image_src": "",
                    #         "height": int(height),
                    #         "width": int(width)
                    #     }
                    # else:
                    #     continue
            logger.info(c["data"])
            dcontents.append(dc)
            rank += 1
        if processStatus != 0:
            dnews["processStatus"] = processStatus
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
        # collection_news.insert(dnews)
        if title is not None and len(contents) > 0:
            # logger.info("*************DONE*************")
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s | %s", nid, processStatus)
            pass
    return

def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL["post"], URL["newsDate"], download_crawler)

def crawler_news(column, crawler, newsurl, newspost, topic, download_crawler):
    retry = 0
    while True:
        result = crawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'], newspost, topic, download_crawler)
            except Exception,ex:
                logger.exception(ex)
            break

        retry += 1
        if retry > 400:
            break


def process(content, flag):
    if content.find("Bloomberg") >= 0:
        logger.info("aaa")
        d = pq(html.fromstring(content.decode("utf-8")))
        for a in d('section> div> article> h3'):
            try:
                link = d(a)('a').attr("href")
                title = d(a)('a').text().strip()
                ndate = None
                logger.info(link)
                if re.search(linkPattern, link) and title is not None and title.strip() != "":
                    logger.info("Link: %s is right news link: %s|%s", link, title, ndate)

                    linknew = "https://www.bloomberg.com" + link
                    mongo = db.connect_mongo()
                    collection_news = mongo.article.news
                    item = collection_news.find_one({"link": linknew})

                    item2 = collection_news.find_one({"title": title})
                    mongo.close()

                    if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                        linkmap = {
                            "link": linknew,
                            "post": None,
                            "newsDate": ndate


                        }
                        URLS.append(linkmap)

                else:
                    # logger.info(link)
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

        url = "https://www.bloomberg.com/technology"

        while True:
            result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        # threads = [gevent.spawn(run_news, column, newscrawler, download_crawler=None) for i in xrange(concurrent_num)]
                        # gevent.joinall(threads)
                        run_news(column, newscrawler, download_crawler=None)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break
        # exit()
        # elif result['get'] == 'redirect' and r

@traceback_decorator.try_except
def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        # newscrawler = ListCrawler()
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, listcrawler, concurrent_num)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            time.sleep(60*20)        #30 minutes
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
            download_crawler = None
            crawler_news({"column":"None"}, NewsCrawler(), link, None, None, download_crawler)
    else:
        start_run(1, "incr")