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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper
import random

# logger
loghelper.init_logger("crawler_szse", stream=True)
logger = loghelper.get_logger("crawler_szse")

KEYS = []
DATE = None


class szseCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find('400 Bad Request') >= 0: return False
        try:
            # res = content.replace('null([', '')[:-2]
            # j = json.loads(content)['result']

            if url.find('CATALOGID=1110') >= 0:
                if content.find('cls-data-table-common cls-data-table') >= 0:
                    return True
                else:
                    return False
            elif url.find('1743_detail_sme') >= 0:
                if content.find('cls-title-table-common cls-title-table') >= 0:
                    return True
                else:
                    return False
            else:
                return False
            return False
        except Exception, ex:
            logger.info(Exception, ":", ex)
            return False


def has_content(content):
    # res = content.replace('null(', '')[:-1]
    try:
        j = json.loads(content)
        logger.info('has content')
        return True
    except Exception, ex:
        print Exception, ":", ex
        logger.info('hasnt content')
        return False


def process(g, crawler, url, key, content):
    # if has_content(content):
    if 1:
        # j = json.loads(content)
        j = content

        crawler.save(g.SOURCE, g.TYPE, url, key, j)
        logger.info('saving %s %s %s %s\n%s', g.SOURCE, g.TYPE, url, key, '#' * 166)
        # g.latestIncr()


def run_detail(g, crawler, url, key):
    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            content = result['content'].decode('gbk')
            break
            # gevent.spawn(run_investor, g, crawler, url, key, num)
    process(g, crawler, url, key, content)


def parse_list(g, crawler, key, content):
    # res = content.replace('null([', '')[:-2]
    d = pq(html.fromstring(content.decode("gbk", "ignore")))

    items = d('.cls-data-table tr')
    if content.decode("gbk").find(u'没有找到符合条件的数据！') >= 0:
        return 0
    logger.info('%s returns %s items', key, len(items))
    # num = 0
    for i in items[1:]:
        itemkey = d(i)('td:nth-child(1)').text()
        name = d(i)('td:nth-child(2)').text()

        url = 'http://www.szse.cn/szseWeb/FrontController.szse?randnum=%s&ACTIONID=7&CATALOGID=1743_detail_sme&DM=%s' % (
            random.random(), itemkey)

        global totalcnt
        totalcnt += 1
        logger.info('%s %s %s', itemkey, name, totalcnt)

        run_detail(g, crawler, url, itemkey)

    return len(items[1:])


def run(g, crawler):
    while True:
        if len(KEYS) == 0:
            return
        key = KEYS.pop(0)

        while True:
            # payload = {
            #     'stockType': 1,
            #     'pageHelp.cacheSize': 1,
            #     'pageHelp.beginPage': key,
            #     'pageHelp.pageSize': 25,
            #
            # }
            # url = "http://www.szse.cn/szseWeb/FrontController.szse?"
            # url=url + urlencode(payload)
            url = 'http://www.szse.cn/szseWeb/FrontController.szse?randnum=%s&ACTIONID=7&CATALOGID=1110&tab1PAGENO=%s' % (
                random.random(), key)

            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                # logger.info(result["content"])
                try:
                    cnt = parse_list(g, crawler, key, result['content'])
                except Exception, ex:
                    print 'run error', key
                    logger.exception(ex)
                break

        if cnt == 0:
            print url, ' returns nothing'
            return
        logger.info('cost %f secs ', time.time() - startTime, )


def start_run(concurrent_num, flag):
    global KEYS, totalcnt, startTime
    global DATE
    while True:
        dt = datetime.datetime.now()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        if datestr != DATE and dt.hour >= 22:
            totalcnt = 0
            KEYS = [i + 1 for i in range(1000)]

            startTime = time.time()

            logger.info("szse %s start...", flag)
            g = GlobalValues.GlobalValues(13402, 36001, flag)

            threads = [gevent.spawn(run, g, szseCrawler()) for i in xrange(concurrent_num)]
            gevent.joinall(threads)

            logger.info("szse %s end.", flag)
            DATE = datestr

        if flag == "incr":
            gevent.sleep(60 * 60)
        else:
            gevent.sleep(86400 * 3)  # 3 days


if __name__ == "__main__":
    start_run(5, "incr")
    # start_run(25, "incr")

    # urls={'baseinfo':'http://query.szse.com.cn/commonQuery.do?sqlId=COMMON_SSE_ZQPZ_GP_GPLB_C&productid=600000',
    #       'excutives':'http://query.szse.com.cn/commonQuery.do?sqlId=COMMON_SSE_ZQPZ_GG_GGRYLB_L&productid=600000',
    #       }
    # run_detail(GlobalValues.GlobalValues(13401, 36001, "incr"), BaseCrawler.BaseCrawler(), urls, 600000)
