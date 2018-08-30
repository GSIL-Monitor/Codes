# -*- coding: utf-8 -*-
import os, sys, datetime, json, urllib2, time
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db

#logger
loghelper.init_logger("crawler_itjuzi_company3_SE", stream=True)
logger = loghelper.get_logger("crawler_itjuzi_company3_SE")


TYPE = 36001
SOURCE =13030
columns = [
    {"column": "new", "max": 20}]
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

def run_news(crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)
        crawl(crawler, URL["id"], URL["name"])


def crawl(crawler, id, name):
    url = "https://www.itjuzi.com/company/%s" % id
    retries = 0
    retries_2 = 0
    headers = {
               # "Cookie": "acw_sc__=5a44bfed12f472772990fdadd57a71ba15554322",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0"}
    while True:
        result = crawler.crawl(url, headers=headers)
        # logger.info("here")
        # logger.info(result)
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
                retries_2 += 1
                if retries_2 > 25:
                    break
                continue
            d = pq(html.fromstring(result["content"]))
            title = d('head> title').text().strip()
            if title == "找不到您访问的页面":
                if retries >= 2:
                    break
                retries += 1
        logger.info("retry: %s", retries_2)
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




def process(content):
    # logger.info(content)
    d = pq(html.fromstring(content.decode("utf-8")))
    for a in d('div.main> div.sec> ul> li> a'):
        # logger.info(pq(a))
        try:
            link = pq(a)('a').attr("href")
            logger.info(link)
            id = link.split("/")[-1]

            name = pq(a)('h4').text()
            logger.info("company: %s|%s", id, name)

            # check mongo data if link is existed
            mongo = db.connect_mongo()
            collection_news = mongo.raw.projectdata
            item = collection_news.find_one({"source": SOURCE, "type": TYPE, "key_int": int(id)})
            mongo.close()
            if item is None or ((datetime.datetime.now() - item["date"]).days >1):
            #     URLS.append(a)
            # if item is None:
                URLS.append({"id": id, "name": name})
        except Exception, e:
            logger.info(e)
            logger.info("cannot get company data")
    return len(URLS)



def run_search(companycrawler, keyword):
    retry = 0

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
    }

    url = 'https://www.itjuzi.com/search?word=%s' % keyword

    while True:

        result = companycrawler.crawl(url,agent=True, headers=headers)

        if result['get'] == 'success':

            cnt = process(result['content'])
            logger.info("%s has %s fresh company", url, cnt)
            if cnt > 0:
                logger.info("%s has %s fresh company", url, cnt)
                logger.info(URLS)
                run_news(companycrawler)

            break

        retry += 1
        if retry > 20:
            break






def start_run(keyword, sourceId):
    companycrawler = ItjuziCrawler()
    while True:
        if sourceId is None:
            run_search(companycrawler, keyword)
        else:
            crawl(companycrawler, str(sourceId), "new")
        break



if __name__ == "__main__":

    start_run("teambitionBBBB", 29998)