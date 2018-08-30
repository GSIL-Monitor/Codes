# -*- coding: utf-8 -*-
import os, sys
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey;

monkey.patch_all()
import json, time, datetime
from urllib import urlencode

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, db, extract

# logger
loghelper.init_logger("crawler_sse_an", stream=True)
logger = loghelper.get_logger("crawler_sse_an")


class AnnounceCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        try:
            res = content  # .replace('null([', '')[:-2]
            j = json.loads(res)
            return True
        except Exception, ex:
            # logger.info(Exception, ":", ex)
            return False


def process(content):
    res = content  # .replace('null([', '')[:-2]
    j = json.loads(res)
    logger.info(j)
    infos = j["result"]
    cnt=0
    if len(infos) == 0:
        return 0
    for info in infos:
        try:
            stockid = info["security_Code"]
            filelink = "http://static.sse.com.cn" + info["URL"]
            filetitle = info["title"]
            fileTime = info["SSEDate"]

            print datetime.datetime.now()

            content = {
                # 'source': 13401,
                # 'sourceId': int(stockid),
                # 'title': filetitle,
                # 'link': filelink,
                # "date": datetime.datetime.now() - datetime.timedelta(hours=8),
                # 'createTime': datetime.datetime.now(),
                'stockExchangeId': 2,
                'source': 13401,
                'stockSymbol': str(stockid),
                'title': filetitle,
                'link': filelink,
                "date": datetime.datetime.now() - datetime.timedelta(hours=8),
                'createTime': datetime.datetime.now(),
            }

            # check mongo data if link is existed
            mongo = db.connect_mongo()

            collection = mongo.stock.announcement
            item = collection.find_one({"link": filelink})
            if item is None:
                collection.insert(content)
                cnt+=1
            else:
                logger.info("already exists file: %s", filelink)

            mongo.close()

            logger.info("Stock: %s, file: %s|%s|%s", stockid, filetitle, fileTime, filelink)
        except Exception, e:
            logger.info(e)
            logger.info("cannot get info")
    return cnt


def run(crawler, startdate, maxpage, concurrent_num):
    global CURRENT_PAGE
    cnt = 1
    while True:
        key = CURRENT_PAGE + 1
        if cnt == 0 or key > maxpage: return

        CURRENT_PAGE += 1
        header = {'Referer': 'http://www.sse.com.cn/disclosure/listedinfo/announcement/'}
        url = 'http://query.sse.com.cn/infodisplay/queryLatestBulletinNew.do?'

        payload = {
            # '_': '1484116459145',
            'beginDate': (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d"),
            'endDate': datetime.date.today().strftime("%Y-%m-%d"),
            #  'isPagination': 'true',
            #  'jsonCallBack': 'jsonpCallback47501',
            'pageHelp.beginPage': CURRENT_PAGE,
            'pageHelp.cacheSize': '1',
            #  'pageHelp.endPage': '5',
            #  'pageHelp.pageNo': '1',
            'pageHelp.pageSize': '25',
            'reportType': 'ALL'
            #  'pageHelp.pageCount': '50',
        }

        url += urlencode(payload)

        while True:
            result = crawler.crawl(url, headers=header, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'])
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)

                        # threads = [gevent.spawn(run_news, column, newscrawler, download_crawler) for i in xrange(concurrent_num)]
                        # gevent.joinall(threads)
                        # exit()
                except Exception, ex:
                    logger.exception(ex)
                    cnt = 0
                break


def start_run(concurrent_num, startdate, maxpage):
    global CURRENT_PAGE
    while True:
        logger.info("sse  announcement start...")
        announcecrawler = AnnounceCrawler()
        CURRENT_PAGE = 0
        run(announcecrawler, startdate, maxpage, concurrent_num)

        logger.info("announcement end.", )

        gevent.sleep(60*5)   #3 days


if __name__ == "__main__":
    start_run(1, "", 100)

