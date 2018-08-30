# -*- coding: utf-8 -*-
import os, sys, datetime
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import GlobalValues_news

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,extract,db,util,url_helper

#logger
loghelper.init_logger("crawler_Pencil_news", stream=True)
logger = loghelper.get_logger("crawler_Pencil_news")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

DATE = None
TYPE = 60001

class PencilCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        #if content.find("</html>") == -1:
        #    return False

        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("页面未找到404") >= 0:
            return False
        if title.find("您所请求的网址（URL）无法获取") >= 0:
            return False
        if title.find("403 Forbidden") >= 0:
            return False
        if title.find("ERROR: The requested URL could not be retrieved") >= 0:
            return False
        if content.find("421 Server too busy") >= 0:
            return False
        if content.find("铅笔道") >= 0:
            return True
        return False


def has_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    if title.find("502 Bad Gateway") >= 0:
        return False
    if title.find("页面未找到404") >= 0:
        # logger.info(content)
        return False
    if title.find("您所请求的网址（URL）无法获取") >= 0:
        # logger.info(content)
        return False
    return True


def process(g, crawler, url, key, content):
    if has_content(content):
        #logger.info(content)
        main = pq(content)('div.article_content')
        d = pq(main)
        title = d('h1#article_title').text()
        brief = pq(content)("meta[name='description']").attr("content")
        # post_time =pq(content)("meta[property='article:published_time']").attr("content").split("+")[0]
        # news_time = datetime.datetime.strptime(post_time, "%Y-%m-%dT%H:%M:%S")
        result = util.re_get_result("var publishTime = new Date\(\"(.*?)\"\)", content)
        if result:
            post_time, = result
            news_time = datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S")
        else:
            logger.info("incorrcet post time")
            logger.info(content)
            exit()
            return

        contents = extract.extractContents(url, content)
        if title.find("融资") >= 0 or title.find("获投") >= 0:
            category = 60101
        else:
            category = None
        tags =[]

        articletags = pq(content)("meta[name='keywords']").attr("content")
        if articletags is None:
            logger.info(content)
        else:
            for tag in articletags.split():
                if tag is not None and tag.strip() != "" and tag not in tags:
                    tags.append(tag)

        logger.info("%s, %s, %s, %s, %s", key, title, news_time, category, ":".join(tags))
        #logger.info(news_time)
        #logger.info(contents)
        # for t in contents:
        #     logger.info(t["data"])

        #item = collection_news.find_one({"source": g.SOURCE, "key_int": int(key)})
        craw = True
        #2016-10-01 pencilnews website upgrade, news keys changed! Have to redownload article with new keys
        if collection_news.find_one({"source": g.SOURCE, "key_int": int(key)}) is not None:
            cnews = collection_news.find_one({"source": g.SOURCE, "key_int": int(key)})
            logger.info("%s, %s", url, cnews["link"])
            if url == cnews["link"]:
                craw = False
            else:
                collection_news.delete_many({"source": g.SOURCE, "key_int": int(key)})
                logger.info("different link!")

        if craw:
            newses = list(collection_news.find({"title": title, "source": {"$ne": g.SOURCE}}))
            for news in newses:
                if news.has_key("type") and news["type"] > 0:
                    craw = False
                    break
        if craw:
            if collection_news.find_one({"title": title, "source": {"$ne": g.SOURCE}}) is not None:
                collection_news.delete_many({"title": title, "source": {"$ne": g.SOURCE}})
            flag, domain = url_helper.get_domain(url)
            dnews = {
                "date": news_time - datetime.timedelta(hours=8),
                "title": title,
                "link": url,
                "createTime": datetime.datetime.now(),
                "source": g.SOURCE,
                "key": key,
                "key_int": int(key),
                "type": TYPE,
                "original_tags":tags,
                "processStatus":0,
                "companyId": None,
                "companyIds":[],
                "category": category,
                "domain": domain
            }

            dcontents = []
            rank = 1
            for c in contents:
                if c["data"] == "/The End/":
                    break
                if c["type"] == "text":
                    dc = {
                        "rank": rank,
                        "content": c["data"],
                        "image": "",
                        "image_src": "",
                    }
                else:
                    dc = {
                        "rank": rank,
                        "content": "",
                        "image": "",
                        "image_src": c["data"],
                    }
                dcontents.append(dc)
                rank += 1
            dnews["contents"] = dcontents
            if brief is None or brief.strip() == "":
                brief = util.get_brief_from_news(dcontents)
            post = util.get_poster_from_news(dcontents)
            dnews["post"] = post
            dnews["brief"] = brief
            if news_time > datetime.datetime.now():
                logger.info("Time: %s is not correct with current time", news_time)
                dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
            collection_news.insert(dnews)
            logger.info("*************DONE**************")

        g.latestIncr()


def crawl(crawler, key ,g):
    url = "http://www.pencilnews.cn/p/%s.html" % key
    retry = 0
    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            #logger.info(result["content"])
            if result["redirect_url"] == url:
                logger.info(result["redirect_url"])
                try:
                    process(g, crawler, url, key, result['content'])
                except Exception,ex:
                    logger.exception(ex)
                break
            else:
                logger.info("wrong url: %s-> %s", url, result["redirect_url"])
                if retry >= 2:
                    break
                retry += 1
        else:
            if result.has_key("content") and result["content"] is not None and result["content"].strip!= "":
                try:
                    d = pq(html.fromstring(result["content"]))
                    title = d('head> title').text().strip()
                    logger.info("Here is the title: %s", title)
                    if title.find("502 Bad Gateway") >= 0:
                        if retry >= 2:
                            break
                        retry += 1
                    elif title.find("页面未找到404") >= 0 or title.find("您所请求的网址（URL）无法获取") >= 0 or \
                                    title.find("ERROR: The requested URL could not be retrieved") >= 0:
                        if retry >= 2:
                            break
                        retry += 1
                except:
                    pass

def run(g, crawler):
    while True:
        if g.finish(num=50):
            return
        key = g.nextKey()
        crawl(crawler, key, g)


def start_run(concurrent_num, flag):
    global DATE
    while True:
        logger.info("Pencil news %s start for %s", flag, DATE)
        dt = datetime.date.today()

        if DATE == dt:
            g = GlobalValues_news.GlobalValues(13800, TYPE, flag, back=5)
        else:
            logger.info("DATE change! %s, %s", DATE, dt)
            g = GlobalValues_news.GlobalValues(13800, TYPE, flag, back=40)
            DATE = dt

        threads = [gevent.spawn(run, g, PencilCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Pencil news %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*5)        #30 minutes
        else:
            gevent.sleep(86400*3)   #3 days


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(10, "all")
        else:
            key = str(int(param))
            g = GlobalValues_news.GlobalValues(13800, TYPE, "incr", back=0)
            crawl(PencilCrawler(), key, g)
    else:
        start_run(1, "incr")