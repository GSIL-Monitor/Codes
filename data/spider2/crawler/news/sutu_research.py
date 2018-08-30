# -*- coding: utf-8 -*-
import os, sys
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
loghelper.init_logger("crawler_sutu_research", stream=True)
logger = loghelper.get_logger("crawler_sutu_research")

#mongo
#mongo = db.connect_mongo()
#collection_news = mongo.article.news

MAX_PAGE_ALL = 3
MAX_PAGE_INCR = 2
CURRENT_PAGE = 1

SOURCE = 13805
TYPE = 60003

class SutuNewsListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        # if content.find("</html>") == -1:
        #     return False

        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("速途研究院") >= 0 or title.find("互联网") >=0:
            return True

        return False

class SutuNewsPageCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        # if content.find("</html>") == -1:
        #     return False
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        #logger.info("title: %s url: %s", title, url)
        temp = title.split("-")
        if len(temp) < 3:
            return False
        if temp[-1].strip() != "速途网":
            return False
        return True


def process_news(content, news_key, url):
    d = pq(html.fromstring(content))

    title = d('div.center-article> div> div> h1').text().strip()
    post_time = d('div.center-article> div> div.t11_info> div> span').eq(0).text()
    news_time = datetime.datetime.strptime(post_time, "%Y年%m月%d日%H:%M")
    key = news_key
    pagetitle = d('head> title').text().strip()
    column = pagetitle.split("-")[-2].replace("速途研究院","").replace("研—","").replace("速途研究院报告中心","").replace("报告中心","").replace("报告解读","").replace("速途数据","")

    tags = column.split()
    logger.info("%s, %s, %s, %s", key, title, news_time, column)
    article = d('div.center-article> div> div#content').html()
    # logger.info(article)
    contents = extract.extractContents(url, article)

    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    if collection_news.find_one({"source": SOURCE, "key_int": int(key)}) is not None:
        mongo.close()
        return
        # collection_news.delete_one({"source": SOURCE, "key_int": int(key)})
    mongo.close()

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
        "category": None,
        "domain": domain,
        "categoryNames": []
    }
    if title.find("速途研究院：") >= 0 or title.find("速途研究院:")>=0:
        logger.info("it is research for 60006")
        download_crawler = download.DownloadCrawler(use_proxy=False)
        dnews["type"] = 60006
        dnews["category"] = None
        dnews["author"] = "速途研究院"
        dnews["cleanTitle"] = title.replace("：",":").replace("速途研究院:", "")
        dnews["processStatus"] = 1
    else:
        download_crawler = download.DownloadCrawler(use_proxy=False)
    dcontents = []
    rank = 1
    for c in contents:
        if c["data"].find("son_media/msg/2014/06/06/626380.gif") >= 0 or c["data"].find("son_media/t14/img/logo_sootoo.jpg") >= 0:
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
    brief = util.get_brief_from_news(dcontents)
    # post = util.get_poster_from_news(dcontents)
    # dnews["post"] = post
    if download_crawler is None:
        post = util.get_poster_from_news(dcontents)
        dnews["post"] = post
    else:
        post = util.get_posterId_from_news(dcontents)
        dnews["postId"] = post
    dnews["brief"] = brief
    if news_time > datetime.datetime.now():
        logger.info("Time: %s is not correct with current time", news_time)
        dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)

    # collection_news.insert(dnews)
    #
    # logger.info("Done")
    nid = parser_mongo_util.save_mongo_news(dnews)
    logger.info("Done: %s", nid)


def process(content, page_crawler, flag):
    d = pq(html.fromstring(content))
    lis = d("div.main-content-left-pd> div.ZXGX> ul> li")
    #logger.info(lis)
    for li in lis:
        l = pq(li)
        title = l("h3").text().strip()
        href = l("h3> a").attr("href").strip()
        news_key = href.split("/")[-1].replace(".shtml","")
        news_url = "http://www.sootoo.com/content/%s.shtml" % news_key

        logger.info("%s, %s, %s", title, news_key, news_url)

        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        item = collection_news.find_one({"source":SOURCE, "key_int":int(news_key)})
        mongo.close()

        if item is None or flag == "all":
            retry =0
            while True:
                result = page_crawler.crawl(news_url, agent=True)
                if result['get'] == 'success':
                    #logger.info(result["content"])
                    try:
                        process_news(result['content'], news_key, news_url)
                    except Exception,ex:
                        pass
                        logger.exception(ex)
                    break

                if retry >= 20:
                    break
                retry += 1
    #crawler.save(g.SOURCE, g.TYPE, url, key, content)


def run(flag,column):
    global CURRENT_PAGE
    crawler = SutuNewsListCrawler()
    page_crawler = SutuNewsPageCrawler()

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
        if column == "key":
            url = "http://www.sootoo.com/keyword/157613/?page=%s" % key
        else:
            url = "http://www.sootoo.com/tag/5/?&day=--&page=%s" % key
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    process(result['content'], page_crawler, flag)
                except Exception,ex:
                    pass
                    logger.exception(ex)
                break



def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("Sutu research %s start...", flag)
        for column in ["key", "tag"]:
            CURRENT_PAGE = 1
            run(flag, column)
        logger.info("Sutu research %s end.", flag)

        if flag == "incr":
            time.sleep(60*45)        #5hour
        else:
            return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    flag = "incr"
    concurrent_num = 1

    if len(sys.argv) > 1:
        flag = sys.argv[1]

    start_run(concurrent_num, flag)