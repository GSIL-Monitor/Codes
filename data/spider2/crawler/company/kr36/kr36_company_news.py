# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, random
from lxml import html
from pyquery import PyQuery as pq
import urllib2
import urllib
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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../news'))
import Newscrawler


#logger
loghelper.init_logger("crawler_company_news", stream=True)
logger = loghelper.get_logger("crawler_company_news")

TYPE = 36001
SOURCE =13022
URLS = []
CURRENT_PAGE = 1
linkPattern = "/article/\d+"
Nocontents = [
]
columns = [
    {"column": None, "max": 3},
]



def find_companyId(sourceId):
    if sourceId== "0" or sourceId==0:
        return None
    conn = db.connect_torndb()
    sc = conn.get("select * from source_company where source=%s and sourceId=%s", 13022, sourceId)
    conn.close()
    if sc is not None:
        if sc["companyId"] is not None:
            return sc["companyId"]
    return None


class newsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
            except:
                return False

            if j["msg"].strip() == "操作成功！":
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return True
            else:
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return False
        return False


def has_content(content):
    if content is not None:
        try:
            j = json.loads(content)
        except:
            logger.info("Not json content")
            logger.info(content)
            return False

        if j["code"] == 0:
            return True
        else:
            logger.info("code=%d, %s" % (j["code"], j["msg"]))
    else:
        logger.info("Fail to get content")

    return False



def process(content, companyId):

    j = json.loads(content)
    # logger.info(content)
    newses = j["data"]

    cnt = 0
    if len(newses) == 0:
        return cnt

    for news in newses:
        try:

            link = news["newsUrl"]
            title = news["title"]
            pdate = news["publishDateStr"]
            logger.info("news: %s|%s", title, link)

            if link is None: continue
            # check mongo data if link is existed
            mongo = db.connect_mongo()
            collection_news = mongo.article.news
            item1 = collection_news.find_one({"link": link})
            if title is not None:
                item2 = collection_news.find_one({"title": title})
            else: item2 = None
            mongo.close()
            if item1 is None and item2 is None:
                logger.info("new news")
                URLS.append({"link": link, "pdate": pdate})
            else:
                logger.info("existed news")
                if item1 is not None:
                    add_companyIds(link, companyId)
                if item2 is not None:
                    add_companyIds(item2["link"], companyId)
        except Exception, e:
            logger.info(e)
            logger.info("cannot get news data")
    return len(URLS)

def add_companyIds(link, companyId):
    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    item = collection_news.find_one({"link": link})
    # logger.info("companyId:%s", companyId)
    if item is not None and item.has_key("companyIds") and companyId not in item["companyIds"]:
        collection_news.update_one({"_id": item["_id"]}, {'$set': {"companyId":int(companyId)},'$addToSet': {"companyIds": int(companyId)}})
    mongo.close()

def run_news(companyId):
    logger.info("companyId:%s", companyId)
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        Newscrawler.crawlerNews(URL["link"], URL["pdate"])
        add_companyIds(URL["link"], companyId)


def run(crawler, rawId, concurrent_num):

    #get companyId
    companyId = find_companyId(rawId)
    if companyId is None:
        return

    while True:

        url = 'https://rong.36kr.com/n/api/company/%s/news' % (rawId)

        while True:
            result = crawler.crawl(url,agent=True)

            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], companyId)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        threads = [gevent.spawn(run_news, companyId) for i in xrange(concurrent_num)]
                        gevent.joinall(threads)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break
        break


def start_run(crawler, concurrent_num, flag, rawId):
    # global CURRENT_PAGE
    while True:
        logger.info("id %s %s start...", SOURCE, rawId)
        # crawler = newsCrawler()

        run(crawler, rawId, concurrent_num)

        break
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        # start_run(1,"incr",param)
    else:
        crawler = newsCrawler()

        while True:
            logger.info("crawler 36kr news start...")
            # ilists = []
            mongo = db.connect_mongo()
            collection = mongo.raw.projectdata
            rawcs= list(collection.find({"source": 13022,"newsProcessed":{"$ne":True}}, limit=1000))
            for rawc in rawcs:
                logger.info("need to crawler 36kr news:%s", rawc["key"])
                # ilists.append(int(investor["kr36InvestorId"]))
                start_run(crawler, 1, "incr", rawc["key"])
                collection.update_one({"_id": rawc["_id"]}, {"$set": {"newsProcessed": True}})

            mongo.close()
            logger.info("crawler end.")
            # break

            gevent.sleep(60 * 60)