# -*- coding: utf-8 -*-
import os, sys, datetime, re, time
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
loghelper.init_logger("crawler_cheyun_newsf", stream=True)
logger = loghelper.get_logger("crawler_cheyun_newsf")

NEWSSOURCE = "chenyun"
RETRY = 3
TYPE = 60008
SOURCE =13851
URLS = []
CURRENT_PAGE = 1
MAX_PAGE = 2
linkPattern = "cheyun.com/content/\d+"

columns = [
    {"column": "news", "max": 1},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
           return False

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("车云") >= 0:
            return True
        return False

class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
           return False

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("车云") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    if title.find("车云") >= 0 :
        return True
    return False


def process_news(column, newsurl, content):
    if has_news_content(content):
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('h1.u-title-article').text()
        url = newsurl
        key = url.split('/')[-1]
        try:
            post_time = d('li.date>span').text().split(": ")[1].split("来源")[0].strip()
            logger.info(post_time)
            news_time = datetime.datetime.strptime(post_time, "%Y/%m/%d %H:%M:%S")
        except:
            news_time = datetime.datetime.now()

        logger.info("title:%s, date:%s", title, news_time)
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
            "original_tags": [],
            "processStatus": 0,
            # "companyId":companyId,
            "companyIds": [],
            "category": None,
            "domain": domain,
            "categoryNames": []
        }

        dcontents = []
        description = d('div.m-con-article> p').text()
        if description is not None:
            dc = {
                "rank": 1,
                "content": "车云快讯",
                "image": "",
                "image_src": "",
            }

            dcontents.append(dc)
            dc = {
                "rank": 2,
                "content": description.replace("【消息来源】",""),
                "image": "",
                "image_src": "",
            }
            dcontents.append(dc)

            logger.info(description)

        dnews["contents"] = dcontents

        brief = util.get_brief_from_news(dcontents)

        post = util.get_posterId_from_news(dcontents)
        dnews["postId"] = post
        # dnews["post"] = post
        dnews["brief"] = brief
        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
        # collection_news.insert(dnews)
    return


def run_news(column, crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL)

def crawler_news(column, crawler, newsurl):
    maxretry = 0
    while True:
        result = crawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'])
            except Exception,ex:
                logger.exception(ex)
            break
        if maxretry > 20:
            break
        maxretry += 1



def process(content, flag):
    d = pq(html.fromstring(content.decode("utf-8")))
    for a in d('ul.m-lsts-tab> li> div> h3> a'):
        try:
            link = d(a).attr("href").strip()
            link = 'http://www.cheyun.com'+ link
            if re.search(linkPattern, link):
                logger.info("Link: %s is right news link", link)

                #check mongo data if link is existed
                mongo = db.connect_mongo()
                collection_news = mongo.article.news
                item = collection_news.find_one({"link":link})
                mongo.close()

                if (item is None or flag == "all") and link not in URLS:
                    URLS.append(link)
            else:
                # logger.info(link)
                pass
        except:
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

        url = "http://www.cheyun.com/express/1"

        while True:
            result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        # threads = [gevent.spawn(run_news, column, newscrawler) for i in xrange(concurrent_num)]
                        # gevent.joinall(threads)
                        # exit()
                        run_news(column, newscrawler)
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break
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
            time.sleep(60*30)        #30 minutes
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
            crawler_news({}, NewsCrawler(), link)
    else:
        start_run(1, "incr")