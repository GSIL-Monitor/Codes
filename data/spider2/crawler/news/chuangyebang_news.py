# -*- coding: utf-8 -*-
import os, sys, time
import datetime
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db,util,extract, url_helper, desc_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_chuangyebang_news", stream=True)
logger = loghelper.get_logger("crawler_chuangyebang_news")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

MAX_PAGE_ALL = 810
MAX_PAGE_INCR = 5
CURRENT_PAGE = 1

SOURCE = 13806
TYPE = 60001

class CzbNewsListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        # if content.find("</html>") == -1:
        #     return False

        # d = pq(html.fromstring(content))
        # title = d('head> title').text().strip()
        # logger.info("title: %s url: %s", title, url)
        # if title.find("创业邦") >= 0:
        #     return True
        if content.find("cyzone") >= 0:
            logger.info(content)
            return True

        return False

class CzbNewsPageCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("创业邦")>= 0:
            return True
        if title.find("您访问了一个错误的链接") >= 0:
            return True
        return False

def has_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    temp = title.split("-")
    if len(temp) < 3:
        return False
    if temp[-1].strip() != "创业邦":
        return False
    return True


def process_news(content, news_key, url):
    if has_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        d = pq(html.fromstring(content))
        brief = d("meta[name='description']").attr("content").split(",")[-1]
        title = d('div#article> div.single-item> div.article-hd> h1').text().strip()
        pagetitle = d('head> title').text().strip()
        temp = pagetitle.split("-")[-2]
        categoryNames = []
        if temp.strip() == "初页":
            category = 60102
            categoryNames.append("产品")
        elif temp.strip() == 'IPO/并购':
            category = 60105
            categoryNames.append("大公司")
        else:
            category = None
        post_time = d('div.author-time> span.date-time').attr("data-time")
        post_date = time.localtime(int(post_time))
        news_time = datetime.datetime(post_date.tm_year, post_date.tm_mon, post_date.tm_mday, post_date.tm_hour,
                                      post_date.tm_min, post_date.tm_sec)
        key = news_key
        column = d('div.article-tags> a').text()
        tags = column.split()
        logger.info("%s, %s, %s, %s, %s, %s, %s", key, title, post_time, news_time, temp,  category, ":".join(tags))
        article = d('div#article> div> div.article-content').html()
        # # logger.info(article)
        contents = extract.extractContents(url, article)

        if collection_news.find_one({"source": SOURCE, "key_int": int(key)}) is not None:
            return
            # collection_news.delete_one({"source": SOURCE, "key_int": int(key)})

        if collection_news.find_one({"title": title, "source": {"$ne": SOURCE}}) is not None:
            return
            # collection_news.delete_many({"title": title, "source": {"$ne": SOURCE}})

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
        if brief is None or brief.strip() == "" or desc_helper.check_desc(brief,2) is False:
            brief = util.get_brief_from_news(dcontents)
        # post = util.get_poster_from_news(dcontents)
        # dnews["post"] = post

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
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)

    # logger.info("Done")


def process(content, page_crawler, flag):
    d = pq(html.fromstring(content.decode("utf-8")))
    # divs = d("div.article-list> div.list-inner")
    divs = d("div.article-item.clearfix")
    #logger.info(lis)
    for div in divs:
        l = pq(div)
        title = l("div.item-intro> a.item-title").text().strip()
        href = l("div.item-intro> a.item-title").attr("href").strip()
        news_key = href.split("/")[-1].replace(".html","")
        news_url = href

        logger.info("%s, %s, %s", title, news_key, news_url)

        if collection_news.find_one({"source":SOURCE, "key_int":int(news_key)}) is None or flag == "all":
            craw = True
            newses = list(collection_news.find({"title": title, "source": {"$ne": SOURCE}}))
            for news in newses:
                if news.has_key("type") and news["type"] > 0:
                    craw = False
                    break
            if craw:
                retry = 0
                while True:
                    result = page_crawler.crawl(news_url, agent=True)
                    if result['get'] == 'success':
                        #logger.info(result["content"])
                        try:
                            process_news(result['content'], news_key, news_url)
                        except Exception,ex:
                            logger.exception(ex)
                        break

                    if retry >= 20:
                        break
                    retry += 1
    #crawler.save(g.SOURCE, g.TYPE, url, key, content)


def run(flag):
    global CURRENT_PAGE
    crawler = CzbNewsListCrawler()
    page_crawler = CzbNewsPageCrawler()

    while True:
        key = CURRENT_PAGE
        #logger.info("key=%s", key)
        if flag == "all":
            if key > MAX_PAGE_ALL:
                return
        else:
            if key > MAX_PAGE_INCR:
                return

        CURRENT_PAGE += 1
        # url = "http://www.cyzone.cn/category/3/index_%s.html" % key
        url = "http://api.cyzone.cn/index.php?m=content&c=index&a=init&tpl=index_page&page=%s" % key
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    process(result['content'], page_crawler, flag)
                except Exception,ex:
                    logger.exception(ex)
                break


def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("Chuangyebang news %s start...", flag)
        CURRENT_PAGE = 1
        threads = [gevent.spawn(run,flag) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Chuangyebang news %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*15)        #45mins
        else:
            return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    flag = "incr"
    concurrent_num = 1

    if len(sys.argv) > 1:
        flag = sys.argv[1]

    start_run(concurrent_num, flag)