# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, urllib,time
from lxml import html
from pyquery import PyQuery as pq


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
loghelper.init_logger("crawler_tuoniao_news", stream=True)
logger = loghelper.get_logger("crawler_tuoniao_news")

NEWSSOURCE = "tuoniao"
RETRY = 3
TYPE = 60005
SOURCE =13801
URLS = []
CURRENT_PAGE = 1
linkPattern = "www.tuoniao.fm/p/\d+.html"
Nocontents = [
]
columns = [
    {"column": "business", "max": 1},
    # {"column": "company", "max": 1},
    # {"column": "article", "max": 1},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        # logger.info(content)
        if title.find("鸵鸟") >= 0:
            return True
        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)

        if title.find("您请求的页面不存在") >=0 or title.find("Object moved")>=0:
            return True
        if title.find("未找到页面") >= 0:
            return True
        if title.find("鸵鸟") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    # logger.info("title: " + title)
    if title.find("未找到页面") >= 0:
        return False
    if title.find("鸵鸟") >= 0:
        return True
    return False


def process_news(column, newsurl, content, newspost, download_crawler, sort):
    if has_news_content(content):
        key = newsurl.split("/")[-1].replace(".html","")

        try:
            columns = pq(content)("meta[name='keywords']").attr("content").split(",")
        except:
            columns = []
        # brief = pq(content)("meta[name='description']").attr("content").strip()
        breif = None
        main = pq(content)('div.data-article')
        d = pq(main)
        title = pq(content)('div.da-title> h2').text()
        type = 60001
        categoryNames = []
        if "上海" in columns:
            columns = []
            category = None
        else:
            if "融资" in columns or "融资发布" in columns or title.find("融资") >= 0:
                category = 60101
                categoryNames.append("融资")
            elif "鸵鸟干货" in columns:
                type = 60003
                category = 60107
            elif "投资人专访" in columns:
                category = 60104
                categoryNames.append("投资人观点")
            elif "苹果" in columns or "大公司" in columns:
                category = 60105
                categoryNames.append("大公司")
            elif "工具软件" in columns or \
                            "智能科技" in columns or \
                            "软件" in columns or \
                            "企业服务" in columns or \
                            "本地生活" in columns:
                category = 60102
                categoryNames.append("产品")
            else:
                category = None
        news_time = pq(content)('div.article-author> span.article-time').eq(0).text()
        if news_time is not None and news_time.strip() != "":
            logger.info("here :%s", news_time)
            try:
                news_time = datetime.datetime.strptime(news_time.strip(), "%Y-%m-%d %H:%M")
            except:
                news_time = datetime.datetime.now()
        else:
            news_time = datetime.datetime.now()
        # contents = extract.extractContents(newsurl, content)
        article = d('div.data-article').html()
        contents = extract.extractContents(newsurl, article, document=False)
        dcontents = []
        # article_img = d('div.article-img-box> img').attr("src")
        # if article_img is not None:
        #     dc = {
        #         "rank": 1,
        #         "content": "",
        #         "image": "",
        #         "image_src": article_img,
        #     }
        #     dcontents.append(dc)
        logger.info("%s, %s, %s, %s, %s", key, title, news_time, category, ":".join(columns))


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
            "original_tags": columns,
            "processStatus": 0,
            # "companyId": None,
            "companyIds": [],
            "category": category,
            "domain": domain,
            "categoryNames": categoryNames
        }

        rank = len(dcontents) + 1
        for c in contents:
            if c["data"].find("发表评论") >= 0 or c["data"].find("求报道、投融资对接") >= 0:
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
            logger.info(c["data"])
            dcontents.append(dc)
            rank += 1
        dnews["contents"] = dcontents

        brief = util.get_brief_from_news(dcontents)
        post = util.get_posterId_from_news(dcontents)
        dnews["postId"] = post
        dnews["brief"] = brief
        # mid = collection_news.insert(dnews)
        # logger.info("*********Done: %s", mid)
        if len(dnews["contents"]) > 0:
            # pass
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s", nid)
            pass


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL.get("post",None), download_crawler, URL["sort"])

def crawler_news(column, crawler, newsurl, newspost, download_crawler, sort):
    retry = 0
    while True:
        result = crawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'], newspost, download_crawler, sort)
            except Exception,ex:
                logger.exception(ex)
            break
        retry += 1
        if retry > 25: break



def process(content, flag):
    if content.find("tuoniao") >= 0:
        d = pq(html.fromstring(content.decode("utf-8")))
        for a in d('div.la-list02'):
            try:
                link = d(a)('div.la-r-text> h3> a').attr("href")
                title = d(a)('div.la-r-text> h3> a').text()
                # logger.info(link)
                if re.search(linkPattern, link) and title is not None and title.strip() != "":
                    # logger.info("Link: %s is right news link %s", link, title)
                    # title = d(a)('h3> a').text()
                    post = None
                    sort = None
                    logger.info("Link: %s is right news link %s|%s", link, title, sort)
                    mongo = db.connect_mongo()
                    collection_news = mongo.article.news
                    item = collection_news.find_one({"link": link})
                    item2 = collection_news.find_one({"title": title})
                    mongo.close()

                    if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                        linkmap = {
                            "link": link,
                            "post": post,
                            "sort": sort
                        }
                        URLS.append(linkmap)

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

        url = "http://www.tuoniao.fm/"

        while True:
            result = listcrawler.crawl(url,agent=True)

            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        run_news(column, newscrawler, download_crawler)

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
            time.sleep(60*8)        #30 minutes
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
            crawler_news({"column": "new", "max": 1}, NewsCrawler(), link, "", download_crawler, "投融资")
    else:
        start_run(1, "incr")