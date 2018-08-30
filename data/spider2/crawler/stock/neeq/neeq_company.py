# -*- coding: utf-8 -*-
import os, sys
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey;

monkey.patch_all()
import json, time, datetime

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper

# logger
loghelper.init_logger("crawler_neeq", stream=True)
logger = loghelper.get_logger("crawler_neeq")

KEYS = []
maxKey = 999999999
DATE = None


class NeeqCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self,use_proxy=1)

    # 实现
    def is_crawl_success(self, url, content):
        # logger.info(content)
        if content.find("null") == -1:
            return False
        try:
            res = content.replace('null([', '')[:-2]
            j = json.loads(res)
            if j is not None: return True
        except Exception, ex:
            # logger.info(Exception, ":", ex)
            try:
                res = content.replace('null(', '')[:-1]
                j = json.loads(res)
                code = url.split('zqdm=')[-1]
                if j is not None and j.get('baseinfo')['code'] == code:
                    return True
                else:
                    return False
            except Exception, ex:
                logger.info(Exception, ":", ex)
                return False
        return False


def has_content(content):
    res = content.replace('null(', '')[:-1]
    try:
        j = json.loads(res)
        return True
    except:
        return False


def process(g, crawler, url, key, content):
    if has_content(content):
        res = content.replace('null(', '')[:-1]
        j = json.loads(res)
        if j is None:
            logger.info(content)
            logger.info("****************")
            exit()
        crawler.save(g.SOURCE, g.TYPE, url, key, j)
        logger.info('saving %s %s %s %s\n%s', g.SOURCE, g.TYPE, url, key, '#' * 166)

        # global  totalCnt  #todo
        # totalCnt +=1
        # g.latestIncr()


def run_detail(g, crawler, url, key):
    # result = crawler.crawl(url,agent=True)
    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            process(g, crawler, url, key, result['content'])
            break
            # gevent.spawn(run_investor, g, crawler, url, key, num)


def parse_list(g, crawler, key, content):
    res = content.replace('null([', '')[:-2]
    j = json.loads(res)

    items = j['content']
    # num = 0
    if len(items) == 0:
        return
    # check if stock cnt is 20
    if len(items) != 20 and key < maxKey - 1:
        logger.info(content)
        logger.info("****************stock cnt isn't 20****************")
        exit()

    for item in items:
        itemkey = item['xxzqdm']
        url = 'http://www.neeq.com.cn/nqhqController/detailCompany.do?zqdm=%s' % itemkey
        run_detail(g, crawler, url, itemkey)


def run(g, crawler):
    while True:
        # if key is None:
        #     if g.finish():
        #         return
        #     key = g.nextKey()
        if len(KEYS) == 0:
            return
        key = KEYS.pop(0)
        url = "http://www.neeq.com.cn/nqxxController/nqxx.do?page=%s&typejb=T&sortfield=xxzqdm&sorttype=asc" % key
        # result = crawler.crawl(url,agent=True)

        # if result['get'] == 'success':
        #     parse_investor(g, crawler, key, result['content'])
        # #     process(g, crawler, url, key, result['content'])
        #     gevent.spawn(run, g, crawler)
        # else:
        #     gevent.spawn(run, g, crawler, key)

        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                # logger.info(result["content"])
                try:
                    parse_list(g, crawler, key, result['content'])
                except Exception, ex:
                    logger.info('111111111111111')
                    logger.exception(ex)
                break

        logger.info('cost %f secs ', time.time() - startTime, )
        # print totalCnt  # todo


def getKeys(crawler):
    global KEYS, maxKey
    while True:
        url = 'http://www.neeq.com.cn/nqxxController/nqxx.do?page=0&typejb=T&sortfield=xxzqdm&sorttype=asc'
        result = crawler.crawl(url,agent=True)
        if result['get'] == 'success':
            # logger.info(result["content"])
            res = result["content"].replace('null([', '')[:-2]
            j = json.loads(res)
            KEYS = [i for i in range(j['totalPages'])]
            maxKey = j['totalPages']
            break


def start_run(concurrent_num, flag):
    global DATE
    while True:
        dt = datetime.datetime.now()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        if datestr != DATE and dt.hour >= 20:
            getKeys(NeeqCrawler())
            logger.info("Neeq %s start...", flag)
            g = GlobalValues.GlobalValues(13400, 36001, flag)
            # logger.info(g)
            # for i in range(concurrent_num):
            #     gevent.spawn(run, g, FellowPlusCrawler())
            # g.wait()
            threads = [gevent.spawn(run, g, NeeqCrawler()) for i in xrange(concurrent_num)]
            gevent.joinall(threads)

            logger.info("Neeq %s end.", flag)
            DATE = datestr
            # print totalCnt  # todo
        if flag == "incr":
            gevent.sleep(60 * 60)
        else:
            gevent.sleep(86400 * 3)  # 3 days


if __name__ == "__main__":
    startTime = time.time()
    # totalCnt=0  #todo
    start_run(10, "incr")
