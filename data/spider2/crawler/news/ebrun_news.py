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
loghelper.init_logger("crawler_ebrun_news", stream=True)
logger = loghelper.get_logger("crawler_ebrun_news")

NEWSSOURCE = "Ebrun"
RETRY = 3
TYPE = 60001
SOURCE =13817
URLS = []
CURRENT_PAGE = 1
linkPattern = "http://www.ebrun.com/\d+/\d+.shtml"
Nocontents = [
    "http://imgs.ebrun.com/images/201511/ybfirst.png",
    "http://imgs.ebrun.com/resources/2016_07/2016_07_13/2016071323814683813522931.png"
]
columns = [
    {"column": "ipo", "max": 1},
    {"column": "financing", "max": 1},
    {"column": "ma", "max": 1},
    {"column": "b2b", "max": 1},
    {"column": "service", "max": 1},
    {"column": "brands", "max": 1},
    {"column": "fto", "max": 1},
    {"column": "mec", "max": 1},
    {"column": "retail", "max": 1},
    {"column": "djk", "max": 1},
    {"column": "intl", "max": 1},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        # if content.find("</html>") == -1:
        #    return False
        if content.find("charset=GBK") == -1:
            d = pq(html.fromstring(content.decode("utf-8","ignore")))
        else:
            d = pq(html.fromstring(content.decode("gbk", "ignore")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("亿邦动力网") >= 0:
            return True
        return False


def has_news_content(content):
    if content.find("charset=GBK") == -1:
        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
    else:
        d = pq(html.fromstring(content.decode("gbk", "ignore")))
    title = d('head> title').text().strip()
    temp = title.split("-")
    if len(temp) < 3:
        return False
    if temp[0].strip() == "":
        return False
    return True


def process_news(column, newsurl, content, newspost):
    if has_news_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        # d = pq(html.fromstring(content.decode("utf-8","ignore")))
        if content.find("charset=GBK") == -1:
            d = pq(html.fromstring(content.decode("utf-8","ignore")))
            utfflag = True
        else:
            d = pq(html.fromstring(content.decode("gbk", "ignore")))
            utfflag = False

        key = newsurl.split("?")[0].split("/")[-1].replace(".shtml","")

        type = TYPE

        category = None
        categoryNames = []

        tags = []
        articletags = d("meta[name='keywords']").attr("content")
        if articletags is not None:
            for tag in articletags.split():
                if tag is not None and tag.strip() != "" and tag not in tags:
                    tags.append(tag)

        if utfflag is True:
            title = d('article> div> h1').text().strip()
        else:
            title = d('div.titleH> h1').text().strip()
        logger.info("title: %s",title)
        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        if collection_news.find_one({"title": title}) is not None:
            mongo.close()
            return


        # post = d('div#post_thumbnail> img').attr("src")
        postraw = newspost
        # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        brief = d("meta[name='description']").attr("content")

        if utfflag is True:
            post_time = d('p.source> span.f-right').eq(0).text()
        else:
            post_time = d('div.titleH> p.zsp> span').eq(2).text()
        logger.info(post_time)
        news_time = extract.extracttime(post_time)
        if news_time is None:
            news_time = datetime.datetime.now()

        # article = d('div.contdiv').html()
        if utfflag is True:
            article = d('div.post-text').html()
        else:
            article = d('div.contdiv').html()
        contents = extract.extractContents(newsurl, article)

        logger.info("%s, %s, %s, %s -> %s, %s", key, title, news_time, ":".join(tags), category, post)
        # exit()
        # mongo = db.connect_mongo()
        # collection_news = mongo.article.news
        # if collection_news.find_one({"title": title}) is not None:
        #     mongo.close()
        #     return

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
            if c["data"].find("电商资讯第一入口") != -1:
                break
            if c["data"] in Nocontents:
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
            # logger.info(c["data"])
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
        mongo.close()
        # logger.info("*************DONE*************")
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
    return


def run_news(column, crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL["post"])

def crawler_news(column, crawler, newsurl, newspost):
    maxretry = 0
    while True:
        result = crawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'], newspost)
            except Exception,ex:
                logger.exception(ex)
            break

        if maxretry > 40:
            break
        maxretry += 1



def process(content, flag):
    d = pq(html.fromstring(content.decode("utf-8","ignore")))
    for a in d('div.sublevel-panel> div> a'):
        try:
            link = d(a).attr("href").strip()
            if re.search(linkPattern, link):
                logger.info("Link: %s is right news link", link)
                title = d(a)('.liebiao-xinwen-title').text().strip()
                #check mongo data if link is existed
                mongo = db.connect_mongo()
                collection_news = mongo.article.news
                item = collection_news.find_one({"link":link})
                item2 = collection_news.find_one({"title": title})
                mongo.close()

                if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                    postlink = d(a)('div.liebiao-image> img').attr("src")
                    linkmap = {
                        "link": link,
                        "post": postlink
                    }
                    URLS.append(linkmap)
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
        # if key == 1:
        #     CURRENT_PAGE = 4
        # if column["column"] == 'b2b':
        #     url = "http://www.ebrun.com/b2b/more.php?page=%s" % (key)
        # elif column["column"] == "service":
        #     url = "http://www.ebrun.com/service/more.php?page=%s" % (key)
        # elif column["column"] in ["brands","fto","mec", "retail", "djk","intl"]:
        #     url = "http://www.ebrun.com/%s/more.php?page=%s" % (column["column"],key)
        # else:
        #     url = "http://www.ebrun.com/capital/%s/more.php?page=%s" % (column["column"], key)

        if column["column"] == 'b2b':
            url = "http://www.ebrun.com/b2b/%s" % (key)
        elif column["column"] == "service":
            url = "http://www.ebrun.com/service/%s" % (key)
        elif column["column"] in ["brands","fto","mec", "retail", "djk","intl"]:
            url = "http://www.ebrun.com/%s/%s" % (column["column"],key)
        else:
            url = "http://www.ebrun.com/capital/%s/%s" % (column["column"], key)




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
                        run_news(column, newscrawler)
                        # exit()
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
            crawler_news({}, ListCrawler(), link, None)
    else:
        start_run(1, "incr")