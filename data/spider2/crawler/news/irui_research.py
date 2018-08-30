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
loghelper.init_logger("crawler_irui_research", stream=True)
logger = loghelper.get_logger("crawler_irui_research")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news
download_crawler = download.DownloadCrawler(use_proxy=False)

newsid =[]
b_id =""

SOURCE = 13808
TYPE =60003
columns = [
    {"root": "rootId", "rootnum": 2, "type": "blog"},
    {"root": "rootId", "rootnum": 4, "type": "news"},
    {"root": "rootId", "rootnum": 5, "type": "news"},
    # {"root": "channelId", "rootnum": 564, "type": "freport"},
]
class IruiCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        #logger.info(content)
        if content.find("iresearch") >= 0:
            return True
        return False

class IruiNewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("gbk")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " " + url)

        if title.find("艾瑞网") >= 0:
            return True
        # logger.info(content)
        return False


def has_content(content):
    d = pq(html.fromstring(content.decode("gbk")))
    lis = d("li")
    if len(lis) > 0:
        return True
    return False

def has_news_content(content):
    d = pq(html.fromstring(content.decode("gbk")))
    title = d('head> title').text().strip()
    temp = title.split("_")
    if len(temp) <2 :
        return False
    if temp[-1].strip() != "艾瑞网":
        return False
    if temp[0].strip() == "":
        return False
    return True


def process_news(item, url, content):
    if has_news_content(content):
        d = pq(html.fromstring(content.decode("gbk")))

        title = d('div.g-main> div> div.m-cont-hd> div.title> h1').text().strip()
        datecontent =  d('div.g-main> div> div.m-cont-hd> div.m-info> div> div> div.box> div.origin').text().strip()
        result = util.re_get_result('(\d{4}\/.*?)$', datecontent)
        if result:
            post_time, = result
            news_time = datetime.datetime.strptime(post_time,"%Y/%m/%d %H:%M:%S")
        else:
            post_time = None
            news_time = None

        key = item["key"]
        column = d('div.g-main> div> div.m-cont-hd> div.tag').text().strip()
        brief = d('div.g-article> div> div.review').text().strip()
        postraw =  item["post"]
        # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        if column is not None:
            tags = column.split()
        else:
            tags = []

        logger.info("%s, %s, %s, %s, %s, %s", key, title, post_time, news_time, brief, ":".join(tags))
        article = d('div.g-article> div.m-article').html()
        #logger.info(article)
        contents = extract.extractContents(url, article)

        if collection_news.find_one({"link": url}) is not None:
            return
            # collection_news.delete_one({"link": url})
        #
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
            "processStatus":0,
            # "companyId": None,
            "companyIds":[],
            "category": None,
            "domain": domain,
            "categoryNames": []
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
        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        # if post is None or post.strip() == "":
        #     post = util.get_posterId_from_news(dcontents)
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
        #g.latestIncr()

def run_news(crawler):
    while True:
        if len(newsid) ==0:
            return
        nitem = newsid.pop(0)

        url = nitem['link']
        retry = 0
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["redirect_url"])
                try:
                    process_news(nitem, url, result['content'])
                except Exception,ex:
                    logger.exception(ex)
                break
            retry += 1
            if retry > 30: break




def process_page(content,flag):
    bid = None
    d = pq(html.fromstring(content.decode("gbk")))
    lis = d("li")
    # logger.info(lis)
    for li in lis:
        l = pq(li)
        id = l('li').attr("id").strip()
        title = l("div.txt> h3").text().strip()
        href = l("div.txt> h3> a").attr("href").strip()
        news_key = href.split("/")[-1].replace(".shtml", "")
        news_url = href
        post = l('div.u-img> a> img').attr("src")

        logger.info("%s, %s, %s, %s,",id, title, news_key, news_url)

        if collection_news.find_one({"link": news_url}) is None or flag == "all":
            if news_url.find("news.iresearch.cn/zt/") >= 0:
                continue
            item = {
                "key": news_key,
                "link": news_url,
                "post": post
            }
            newsid.append(item)

            bid = id

    return newsid, bid

def start_run(flag):
    global b_id
    while True:
        logger.info("Irui research %s start...", flag)

        crawler = IruiCrawler()
        for column in columns:
            while True:
                page_url = "http://report.iresearch.cn/include/pages/redis.aspx?%s=%s&lastId=%s" % (column["root"], column["rootnum"], b_id)
                result = crawler.crawl(page_url, agent=True)
                if result['get'] == 'success':
                    if has_content(result["content"]):
                        newsid, b_id = process_page(result["content"],flag)
                        if len(newsid) > 0:
                            logger.info("crawler news details")
                            threads = [gevent.spawn(run_news, IruiNewsCrawler()) for i in xrange(1)]
                            gevent.joinall(threads)
                            #exit()
                            continue
                        else:
                            b_id = ""
                    else:
                        b_id = ""
                        logger.info("no content")
                        logger.info(result["content"])
                    break


        logger.info("Irui research %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*45)        #10 minutes
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