# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, random
from lxml import html
from pyquery import PyQuery as pq
import urllib2
import urllib
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

import cookielib, Cookie


reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,db

#logger
loghelper.init_logger("crawler_amac_fund", stream=True)
logger = loghelper.get_logger("crawler_amac_fund")

TYPE = 36001
SOURCE =13631
URLS = []
CURRENT_PAGE = 1



class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
            except:
                return False

            if j["totalPages"]>100:
                logger.info("totalPages=%s" % (j["totalPages"]))
                return True
            else:
                return False
        return False




class CsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, timeout=1)

        # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("私募基金公示 - 中国证券投资基金业协会") >= 0:
            return True

        return False



def run_cs(crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_cs(crawler, URL["id"], URL["fundName"])

def crawler_cs(crawler, id, name):

    logger.info("start crawler %s|%s", id, name)
    cs_url = 'http://gs.amac.org.cn/amac-infodisc/res/pof/fund/%s.html' % (id)
    # result = crawler.crawl(cs_url)
    retry = 0
    while True:
        result = crawler.crawl(cs_url)
        if result['get'] == 'success':
            save(SOURCE, TYPE, cs_url, id, result["content"])
            break
        if retry > 20:
            break

        retry += 1

        # time.sleep(random.randint(3,8))



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
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    item = collection.find_one({"source": SOURCE, "type": TYPE, "key": key})
    if item is None:
        collection.insert_one(collection_content)
        logger.info("Saved: %s", url)
    else:
        logger.info(item["source"])
    mongo.close()
    # logger.info("Saved: %s", url)


def process(content, flag):

    j = json.loads(content)
    # logger.info(content)
    companies = j["content"]

    cnt = 0
    if len(companies) == 0:
        return cnt

    for a in companies:
        try:

            id = a["id"]
            name = a["fundName"]
            logger.info("company: %s|%s", id, name)

            # check mongo data if link is existed
            mongo = db.connect_mongo()
            collection_news = mongo.raw.projectdata
            item = collection_news.find_one({"source": SOURCE, "key_int": int(id)})
            mongo.close()
            if item is None:
                URLS.append(a)
        except Exception, e:
            logger.info(e)
            logger.info("cannot get company data")
    return len(URLS)

def run(flag, listcrawler, concurrent_num):
    global CURRENT_PAGE
    cnt = 1
    while True:
        key = CURRENT_PAGE - 1

        if flag == "all":
            if key < 0:
                return
        else:
            if cnt == 0 or key < 0:
                return

        CURRENT_PAGE -= 1

        url = 'http://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand=0.8940836402483638&page=%s&size=200' % (key)
        data = '{}'
        headers = {"Content-Type": "application/json"}
        while True:
            result = listcrawler.crawl(url,agent=True, headers=headers, postdata=data)

            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh company", url, cnt)
                        logger.info(URLS)
                        threads = [gevent.spawn(run_cs, CsCrawler()) for i in xrange(concurrent_num)]
                        gevent.joinall(threads)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break
        # break

def get_total_page(listcrawler):
    url = 'http://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand=0.8940836402483638&page=0&size=200'
    data = '{}'
    headers = {"Content-Type": "application/json"}
    tp = None
    while True:
        result = listcrawler.crawl(url, agent=True, headers=headers, postdata=data)

        if result['get'] == 'success':
            j = json.loads(result["content"])
            tp = j["totalPages"]
            break
    return tp



def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s company %s start...", SOURCE, flag)
        listcrawler = ListCrawler()
        # companycrawler = CsCrawler()

        CURRENT_PAGE = get_total_page(listcrawler)
        if CURRENT_PAGE is not None:
            run(flag, listcrawler, concurrent_num)

        if flag == "incr":
            gevent.sleep(60*60)        #30 minutes
        else:
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(5, "all")
        else:
            link = param
            crawler_cs(CsCrawler(),link, "aaaaaa")

    else:
        start_run(3, "incr")