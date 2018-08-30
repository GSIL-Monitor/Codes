# -*- coding: utf-8 -*-
import os, sys, datetime, re
from lxml import html
from pyquery import PyQuery as pq
import time
import GlobalValues_news

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,extract,db, util,url_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_cstbw_news", stream=True)
logger = loghelper.get_logger("crawler_cstbw_news")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news


TYPE = 60001
SOURCE =13812
CURRENT_PAGE = 1

columns = [
    # {"column": "cn", "maxpage": 145},
    # {"column": "index.php?m=content&c=index&a=lists&catid=40", "maxpage": 145},
    # {"column": "index.php?m=content&c=index&a=lists&catid=19", "maxpage": 48},
    # {"column": "view", "maxpage": 78},
    # {"column": "world", "maxpage": 27},
    {"column": "startup", "maxpage": 2, "category": 60102},
    {"column": "cn", "maxpage": 40, "category": None},
    {"column": "index.php?m=content&c=index&a=lists&catid=40", "maxpage": 40, "category": 60101},
    {"column": "index.php?m=content&c=index&a=lists&catid=19", "maxpage": 20, "category": 60105},
    {"column": "view", "maxpage": 30, "category": 60107},
    {"column": "world", "maxpage": 18, "category": None},
]

class CstbwCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
           return False

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("互联网创业投融资服务平台") >= 0:
            return False
        if title.find("创投时报") >= 0:
            return True
        if title.find("404") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    temp = title.split("_")
    if len(temp) < 2:
        return False
    if temp[-1].strip() != "创投时报":
        return False
    if temp[0].strip() == "":
        return False
    return True


def process_news(content, url, key, col):
    if has_news_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        d = pq(html.fromstring(content.decode("utf-8")))

        title = d('div.cj_content> div.cj_top> div.cj_tit> h2').text().strip().replace("&quo;", "\"")
        datecontent = d('div.cj_content> div.cj_top> div.cj_tit> p.fa').text()
        result = util.re_get_result('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', datecontent)
        if result:
            post_time, = result
            news_time = datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S")
        else:
            logger.info("incorrcet post time")
            return

        try:
            key_int = int(key)
        except:
            key_int = None

        brief = d("meta[name='description']").attr("content").strip()

        if col["column"] == "view":
            type = 60003
        else:
            type = TYPE

        categoryNames = []
        category = col["category"]
        if category == 60105: categoryNames.append("大公司")
        if category == 60101: categoryNames.append("融资")

        tags = []
        keywords = d("meta[name='keywords']").attr("content")
        if keywords is not None:
            for keyword in keywords.split(","):
                if keyword is not None and keyword.strip() not in tags:
                    tags.append(keyword.strip())
        postraw = d('div.cj_content> div.cj_top> img.gg').attr("src")
        # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        logger.info("%s, %s, %s, %s, %s, %s -> %s, %s", key, title, post_time, news_time, brief, ":".join(tags), category, post)

        article = d('div.para_ycont> div.col-xs-12').html()
        # logger.info(article)
        contents = extract.extractContents(url, article)

        if collection_news.find_one({"link": url}) is not None:
            return
            # collection_news.delete_one({"link": url})

        if collection_news.find_one({"title": title, "source": {"$ne": SOURCE}}) is not None:
            collection_news.delete_many({"title": title, "source": {"$ne": SOURCE}})
        flag, domain = url_helper.get_domain(url)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": url,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": key_int,
            "type": type,
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
                # dc = {
                #     "rank": rank,
                #     "content": "",
                #     "image": "",
                #     "image_src": c["data"].replace("?imageView2/2/w/750/q/90",""),
                # }
                if download_crawler is None:
                    dc = {
                        "rank": rank,
                        "content": "",
                        "image": "",
                        "image_src": c["data"].replace("?imageView2/2/w/750/q/90",""),
                    }
                else:
                    (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"].replace("?imageView2/2/w/750/q/90",""), download_crawler, SOURCE, key, "news")
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
        # if post is None or post.strip() == "":
        #     post = util.get_poster_from_news(dcontents)
        # dnews["post"] = post
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
        # logger.info("*************DONE*************")
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)

def process(content, column, page_crawler):
    d = pq(html.fromstring(content))
    divs = d("div> ul> article.list-single-article")
    cnt = 0
    #logger.info(lis)
    for div in divs:
        l = pq(div)
        title = l("h4> a").text().strip()
        href = l("h4> a").attr("href").strip()
        news_url = href
        news_key = href.split("/")[-1].replace("article-","").replace(".html","")

        logger.info("%s, %s, %s", title, news_key, news_url)

        if news_key is None:
            continue
        #cnt += 1
        if collection_news.find_one({"source": SOURCE, "key_int": int(news_key)}) is None or flag == "all":
            craw = True
            newses = list(collection_news.find({"title": title}))
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
                            process_news(result['content'], news_url, news_key, column)
                            cnt += 1
                        except Exception,ex:
                            logger.exception(ex)
                        break

                    if retry > 30:
                        break
                    retry += 1
    return cnt



def run(flag, column, crawler):
    global CURRENT_PAGE
    cnt = 1
    while True:
        key = CURRENT_PAGE
        #logger.info("key=%s", key)
        if flag == "all":
            if key > column["maxpage"]:
                return
        else:
            if cnt == 0:
                return
            if key > column["maxpage"]:
                return

        CURRENT_PAGE += 1
        if column["column"].find("index") >=0:
            url = "http://www.ctsbw.com/%s&page=%s" % (column["column"], key)
        else:
            if key > 1:
                url = "http://www.ctsbw.com/%s/%s.html" % (column["column"], key)
            else:
                url = "http://www.ctsbw.com/%s/index.html" % (column["column"])
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], column, crawler)
                    logger.info("%s has %s news", url, cnt)
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break


def start_run(flag):
    global CURRENT_PAGE
    while True:
        logger.info("Cstbw news %s start...", flag)
        crawler = CstbwCrawler()
        for column in columns:

            CURRENT_PAGE = 1
            run(flag, column, crawler)

        logger.info("Cstbw news %s end.", flag)

        if flag == "incr":
            time.sleep(60*10)        #30 minutes
        else:
            return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    flag = "incr"

    start_run(flag)