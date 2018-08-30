# -*- coding: utf-8 -*-
import os, sys, datetime
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db

#logger
loghelper.init_logger("crawler_itjuzi_company2", stream=True)
logger = loghelper.get_logger("crawler_itjuzi_company2")


TYPE = 36001
SOURCE =13030
columns = [
    {"column": "new", "max": 20}, {"column": "for", "max": 20}]
URLS = []

class ItjuziCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title == "找不到您访问的页面":
            #return True
            return False
        if title.find("IT桔子") >= 0:
            return True
        return False

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        # if title == "找不到您访问的页面":
        if title.find("创业公司") >= 0 and title.find("IT桔子") >= 0:
            return True
        return False



def has_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    temp = title.replace("-", "|").split("|")
    if len(temp) != 2:
        return False
    if temp[1].strip() != "IT桔子":
        return False
    if temp[0].strip() == "" or temp[0].strip() == "的简介，官网，联系方式，":
        return False
    return True

def run_news(column, crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)
        crawl(column, crawler, URL["id"], URL["name"])

def crawl(column, crawler, id, name):
    url = "https://www.itjuzi.com/company/%s" % id
    retries = 0
    retries_2 = 0
    # headers={}
    # user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0'
    # headers['User-Agent'] = user_agent
    headers = {
               # "Cookie": "acw_sc__=5a44bfed12f472772990fdadd57a71ba15554322",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0"}
    while True:
        result = crawler.crawl(url, headers=headers)
        if result['get'] == 'success':
            #logger.info(result["content"])
            try:
                # save(g, crawler, url, key, result['content'])
                if has_content(result["content"]):
                    save(SOURCE, TYPE, url, id, result["content"])
            except Exception,ex:
                logger.exception(ex)
            break
        else:
            if result.has_key("content") is False or result["content"] is None or result["content"].strip() == "" or result["content"].find("</html>") == -1:
                continue
            d = pq(html.fromstring(result["content"]))
            title = d('head> title').text().strip()
            if title == "找不到您访问的页面":
                if retries >= 2:
                    break
                retries += 1

        retries_2 += 1
        if retries_2 > 25:
            break



def save(SOURCE, TYPE, url, key, content):
    logger.info("Saving: %s", url)
    try:
        key_int = int(key)
    except:
        key_int = None

    collection_content = {
        "date": datetime.datetime.now(),
        "source": SOURCE,
        "type": TYPE,
        "url": url,
        "key": key,
        "key_int": key_int,
        "content": content
    }
    newflag = True
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    item = collection.find_one({"source": SOURCE, "type": TYPE, "key": key})
    if item is not None:
        if item["content"] != content:
            collection.delete_one({"source": SOURCE, "type": TYPE, "key": key})
            logger.info("old data changed for company: %s", key)
        else:
            logger.info("old data not changed for company: %s", key)
            newflag = False
    if newflag is True: collection.insert_one(collection_content)
    mongo.close()
    logger.info("Saved: %s", url)




def process(content, flag):
    # logger.info(content)
    d = pq(html.fromstring(content.decode("utf-8")))
    for a in d('p.title,div.title> a'):
        logger.info(pq(a))
        try:
            link = pq(a)('a').attr("href")
            logger.info(link)
            id = link.split("/")[-1]

            name = pq(a).text()
            logger.info("company: %s|%s", id, name)

            # check mongo data if link is existed
            mongo = db.connect_mongo()
            collection_news = mongo.raw.projectdata
            item = collection_news.find_one({"source": SOURCE, "type": TYPE, "key_int": int(id)})
            mongo.close()
            # if item is None or ((datetime.datetime.now() - item["date"]).days>= 1 and (datetime.datetime.now() - item["date"]).days <2):
            #     URLS.append(a)
            if item is None:
                URLS.append({"id":id,"name":name})
        except Exception, e:
            logger.info(e)
            logger.info("cannot get company data")
    return len(URLS)


def run(flag, column, listcrawler, companycrawler, concurrent_num):
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
        headers = {
            # "Cookie": "acw_sc__=5a44bfed12f472772990fdadd57a71ba15554322",
                   "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0"}
        url = 'https://www.itjuzi.com/company?page=%s' % (key)

        if column["column"] == "for":
            url = 'https://www.itjuzi.com/company/foreign?page=%s' % (key)

        while True:
            result = listcrawler.crawl(url,agent=True, headers=headers)

            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    logger.info("%s has %s fresh company", url, cnt)
                    if cnt > 0:
                        logger.info("%s has %s fresh company", url, cnt)
                        logger.info(URLS)
                        threads = [gevent.spawn(run_news, column, companycrawler) for i in xrange(concurrent_num)]
                        gevent.joinall(threads)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break

def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s company %s start...", SOURCE, flag)
        listcrawler = ListCrawler()
        companycrawler = ItjuziCrawler()

        # download_crawler = None
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, companycrawler, concurrent_num)

        if flag == "incr":
            gevent.sleep(60*60)        #30 minutes
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
            crawl({},ItjuziCrawler(),link, "aaaaaa")

    else:
        start_run(1, "incr")