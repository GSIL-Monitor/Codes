# -*- coding: utf-8 -*-
import os, sys
from lxml import html
from pyquery import PyQuery as pq


import json, time, datetime
from urllib import urlencode

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, db, extract

# logger
loghelper.init_logger("crawler_szse_an", stream=True)
logger = loghelper.get_logger("crawler_szse_an")


class AnnounceCrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=20):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    # 实现
    def is_crawl_success(self, url, content):
        try:

            res = content.replace('var szzbAffiches=', '')[:-2]
            # logger.info(res)
            contentnew = eval(res.decode("gbk").strip())
            logger.info(contentnew)
            if len(contentnew) > 0:
                logger.info(len(contentnew))
                return True
            else:
                return False
        except Exception, ex:
            logger.info(ex)
            return False


def process(content):
    cnt = 0
    res = content.replace('var szzbAffiches=', '')[:-2]
    # logger.info(res)
    infos = eval(res.decode("gbk").strip())
    # logger.info(contentnew)
    cnt=0
    if len(infos) == 0:
        return 0
    for info in infos:
        # logger.info(info)
        # logger.info(type(info))
        if len(info) < 4:
            continue
        try:
            stockid = info[0]
            filelink = "http://disclosure.szse.cn/" + info[1]
            filetitle = info[2]
            fileTime = extract.extracttime(info[-1])


            content = {
                'stockExchangeId':3,
                'source': 13402,
                'stockSymbol': str(stockid),
                'title': filetitle,
                'link': filelink,
                "date": fileTime - datetime.timedelta(hours=8),
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

        dt = datetime.datetime.now()
        datestr = datetime.datetime.strftime(dt, '%Y%m%d%H%M')

        CURRENT_PAGE += 1
        # header = {'Referer': 'http://www.sse.com.cn/disclosure/listedinfo/announcement/'}
        url = 'http://disclosure.szse.cn//disclosure/fulltext/plate/szlatest_24h.js?ver=%s' % datestr



        while True:
            result = crawler.crawl(url, agent=True)
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
        logger.info("szse announcement start...")
        announcecrawler = AnnounceCrawler()
        CURRENT_PAGE = 0
        run(announcecrawler, startdate, maxpage, concurrent_num)

        logger.info("announcement end.", )

        time.sleep(60*12)   #3 days


if __name__ == "__main__":
    start_run(1, "", 1)

