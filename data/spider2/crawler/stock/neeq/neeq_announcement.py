# -*- coding: utf-8 -*-
import os, sys
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import  json,time,datetime

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db,extract

#logger
loghelper.init_logger("crawler_neeq_an", stream=True)
logger = loghelper.get_logger("crawler_neeq_an")

SOURCE=13400

class AnnounceCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        try:
            res = content.replace('null([', '')[:-2]
            j = json.loads(res)
            return True
        except Exception, ex:
            # logger.info(Exception, ":", ex)
            return False


def process(content):
    res = content.replace('null([', '')[:-2]
    j = json.loads(res)
    # logger.info(j)
    infos = j["listInfo"]["content"]
    cnt = 0
    if len(infos) == 0:
        return cnt
    mongo = db.connect_mongo()
    # collection = mongo.stock.neeq_announcement
    collection = mongo.stock.announcement
    for info in infos:
        try:
            stockid = info["companyCd"]
            stockName = info["companyName"]
            filelink = "http://www.neeq.com.cn" + info["destFilePath"]
            filetitle = info["disclosureTitle"]
            fileTime = extract.extracttime(str(info["upDate"]["time"]))
            logger.info("Stock: %s|%s, file: %s|%s|%s", stockid, stockName, filetitle, filelink, fileTime)
            item = collection.find_one({"link": filelink})
            if item is None:
                item = {
                    # "source": SOURCE,
                    # "sourceId": int(stockid),
                    # "title": filetitle,
                    # "link": filelink,
                    # "date": fileTime- datetime.timedelta(hours=8),
                    # "createTime": datetime.datetime.now()
                    'stockExchangeId': 1,
                    'source': 13400,
                    'stockSymbol': str(stockid),
                    'title': filetitle,
                    'link': filelink,
                    "date": fileTime - datetime.timedelta(hours=8),
                    'createTime': datetime.datetime.now(),
                }
                collection.insert(item)
                cnt+=1

            logger.info("Stock: %s|%s, file: %s|%s|%s", stockid, stockName, filetitle, filelink, fileTime)
        except Exception,e:
            logger.info(e)
            logger.info("cannot get info")
    mongo.close()
    return cnt

def run(crawler, startdate, maxpage, concurrent_num):
    global CURRENT_PAGE
    cnt = 1
    while True:
        key = CURRENT_PAGE
        if cnt == 0 or key > maxpage:return

        CURRENT_PAGE += 1
        url = 'http://www.neeq.com.cn/disclosureInfoController/infoResult.do?page=%s&disclosureType=5&startTime=%s' % (key,startdate)
        while True:
            result = crawler.crawl(url,agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'])
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                    else:
                        cnt = 0
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break



def start_run(concurrent_num, startdate, maxpage):
    global CURRENT_PAGE
    while True:
        logger.info("neeq announcement start...")
        announcecrawler = AnnounceCrawler()
        CURRENT_PAGE = 0
        run(announcecrawler, startdate, maxpage, concurrent_num)

        logger.info("announcement end.",)

        gevent.sleep(60*5)   #3 days

if __name__ == "__main__":
    start_run(1, "", 25)