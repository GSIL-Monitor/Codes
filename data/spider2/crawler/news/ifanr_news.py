# -*- coding: utf-8 -*-
import os, sys, datetime
from lxml import html
from pyquery import PyQuery as pq
import urllib
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import json

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,extract,db,util,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_ifanr_news", stream=True)
logger = loghelper.get_logger("crawler_ifanr_news")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

newsid =[]
b_id =""

SOURCE = 13811
TYPE =60001
dt = datetime.date.today()

columns = [
    {"category": "review"},
    {"category": "business"},
    {"category": "innovation"},
    {"category": "people"},
    {"category": "mindtalk"},
]
categoryDict={
            "review":60102,
            "business":60105,
            "innovation":60102,
            "people":60103,
            "mindtalk":60103,
        }

class IfanrCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        #logger.info(content)
        if content.find("ifanr") >= 0:
            return True
        return False

class IfanrNewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " " + url)

        if title.find("爱范儿") >= 0:
            return True
        # logger.info(content)
        return False


def has_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    lis = d("div.o-matrix__row")
    if len(lis) > 0:
        return True
    return False

def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    temp = title.split("|")
    if len(temp) <2 :
        return False
    if temp[-1].strip() != "爱范儿":
        return False
    if temp[0].strip() == "" or temp[0].find("Page not found") >= 0:
        return False
    return True


def process_news(item, url, content,category_ori):
    if has_news_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        d = pq(html.fromstring(content.decode("utf-8")))
        if content.find("c-single-normal__title") >= 0:
            title = d('h1.c-single-normal__title').text().strip()
        elif content.find("c-article-header__title") >= 0:
            title = d('h1.c-article-header__title').text().strip()
        else:
            # exit()
            return
        try:
            post_time = pq(content)("meta[property='og:updated_time']").attr("content").split("+")[0]
            news_time = datetime.datetime.strptime(post_time, "%Y-%m-%dT%H:%M:%S")
        except:
            datecontent = d('div.c-article-header-meta> span.c-article-header-meta__time').text().strip()
            logger.info("Date********%s",datecontent)
            result = util.re_get_result('(\d{4}\-)', datecontent)
            if result:
                news_time = datetime.datetime.strptime(datecontent,"%Y-%m-%d %H:%M")
            else:
                post_time = str(dt.year) + '-' +datecontent
                news_time = datetime.datetime.strptime(post_time,"%Y-%m-%d %H:%M")

        key = item["key"]
        column = d('div.c-article-header-meta> span.c-article-header-meta__category').text().strip()
        brief = d("meta[name='description']").attr("content")[:100]


        if column is not None:
            tags = column.split()
        else:
            tags = []

        categoryNames = []
        category=categoryDict[category_ori]
        if category == 60105: categoryNames.append("大公司")
        # if category == None:
        #     if "访谈" in tags:
        #         category = 60103
        #     elif "范品" in tags or "产品" in tags:
        #         category = 60102
        #     else:
        #         category = None

        keywords = d('div#article-content> div.c-article-tags').text()
        if keywords is not None:
            for keyword in keywords.split():
                if keyword is not None and keyword.strip() not in tags:
                    tags.append(keyword.strip())
        logger.info("%s, %s, %s, %s, %s, %s", key, title, news_time,category, ":".join(tags), brief)
        article = d('article.s-single-article').html()
        #logger.info(article)
        contents = extract.extractContents(url, article)

        if collection_news.find_one({"link": url}) is not None:
            return
            # collection_news.delete_one({"link": url})
        if collection_news.find_one({"title": title, "source": {"$ne": SOURCE}}) is not None:
            return
            # collection_news.delete_many({"title": title, "source": {"$ne": SOURCE}})

        postraw = d("meta[property='og:image']").attr("content")
        # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

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
            "companyIds":[],
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
        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        # if post is None or post.strip() == "" or (post.find("http://") == -1 and post.find("https://") == -1):
        #     post = util.get_poster_from_news(dcontents)
        # dnews["post"] = post

        if post is None or post.strip() == "" or (post.find("http://") == -1 and post.find("https://") == -1):
            post = util.get_posterId_from_news(dcontents)

        if download_crawler is None:
            dnews["post"] = post
        else:
            dnews["postId"] = post

        dnews["brief"] = brief[:100]

        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        # collection_news.insert(dnews)
        # logger.info("*************DONE*************")
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
        #g.latestIncr()

def run_news(crawler,category):
    while True:
        if len(newsid) ==0:
            return
        nitem = newsid.pop(0)

        url = nitem['link']
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["redirect_url"])
                try:
                    process_news(nitem, url, result['content'],category)
                except Exception,ex:
                    logger.exception(ex)
                break




def process_page(content,flag):
    bid = None
    d = pq(html.fromstring(content.decode("utf-8")))
    divs = d("div.o-matrix__row")
    # logger.info(lis)
    for div in divs:
        lis = pq(div)('div.o-matrix__row__unit')
        for li in lis:
            l = pq(li)

            title = l("div.c-card> div> h1").text()
            if  title=='':title = l("div > h3").text().strip()

            href = l("div.c-card> div> h1> a").attr("href")
            if href=='' or href is None:href = l(" div >  .article-link").attr("href").strip()

            news_key = href.split("/")[-1]
            news_url = href
            if news_url.find("http") == -1:
                continue

            logger.info("%s, %s, %s,", title, news_key, news_url)
            if news_key is not None and (
                    collection_news.find_one({"source": SOURCE, "key_int": int(news_key)}) is None or flag == "all"):
                craw = True
                newses = list(collection_news.find({"title": title, "source": {"$ne": SOURCE}}))
                for news in newses:
                    if news.has_key("type") and news["type"] > 0:
                        craw = False
                        break
                if craw:
                    item = {
                        "key": news_key,
                        "link": news_url,
                    }
                    newsid.append(item)

            bid = news_key

    return newsid, bid

def start_run(flag):
    global b_id
    while True:
        logger.info("Ifanr news %s start...", flag)

        crawler = IfanrCrawler()
        for column in columns:
            retryCnt = 0
            while True:
                if b_id == "":
                    page_url = "http://www.ifanr.com/category/%s" % (column["category"])
                else:
                    page_url = "http://www.ifanr.com/category/%s?pajax=1&post_id__lt=%s" % (column["category"], b_id)
                result = crawler.crawl(page_url, agent=True)

                if result['get'] == 'success':

                    if has_content(result["content"]):
                        newsid, b_id = process_page(result["content"],flag)
                        if len(newsid) > 0 and int(b_id) > 550000:
                            logger.info("crawler news details")
                            run_news(IfanrNewsCrawler(),column["category"])
                            retryCnt=0
                            #exit()
                            continue
                        else:
                            b_id = ""
                    else:
                        b_id = ""
                        logger.info("no content")
                        logger.info(result["content"])
                    break

                retryCnt+=1
                print
                if retryCnt>10:
                    logger.info( 'retry too many times')
                    b_id=''
                    newsid=[]

                    break


        logger.info("Ifanr news %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*25)        #10 minutes
        else:
            return  #3 days


if __name__ == "__main__":

    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "all":
            start_run("all")
        else:
            start_run("incr")
    else:
        start_run("incr")

