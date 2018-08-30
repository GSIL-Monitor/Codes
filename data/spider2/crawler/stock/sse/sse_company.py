# -*- coding: utf-8 -*-
import os, sys
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey;

monkey.patch_all()
import json, time,datetime
from urllib import urlencode

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper

# logger
loghelper.init_logger("crawler_sse", stream=True)
logger = loghelper.get_logger("crawler_sse")

KEYS = []
DATE = None


class sseCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        try:
            # res = content.replace('null([', '')[:-2]
            j = json.loads(content)['result']

            if url.find('COMMON_SSE_ZQPZ_GP_GPLB_C') >= 0 and j[0].has_key('DUTY'):
                logger.info('baseinfo got incorrect return   %s %s %s %s\n%s', g.SOURCE, g.TYPE, url, key, '#' * 166)
                return False
            if url.find('COMMON_SSE_ZQPZ_GG_GGRYLB_L') >= 0 and len(j) > 0 and not j[0].has_key('START_TIME'):
                logger.info('executives got incorrect return   %s %s %s %s\n%s', g.SOURCE, g.TYPE, url, key,
                            '#' * 166)
                return False
            if url.find('COMMON_SSE_ZQPZ_GP_GPLB_AGSSR_C') >= 0 and len(j) > 0 and not j[0].has_key('LISTINGDATEA'):
                logger.info('listingDate got incorrect return   %s %s %s %s\n%s', g.SOURCE, g.TYPE, url, key,
                            '#' * 166)
                return False

            return True
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


def run_detail(g, crawler, urls, key):
    # result = crawler.crawl(url,agent=True)
    header = {
        'Referer': 'http://www.sse.com.cn/assortment/stock/list/info/company/index.shtml?COMPANY_CODE=%s' % key}

    content = {}
    for i in urls:
        while True:
            url = urls[i]
            result = crawler.crawl(url, headers=header, agent=True)
            if result['get'] == 'success':
                j = json.loads(result['content'])
                # print i
                content[i] = j['result']
                break
                # gevent.spawn(run_investor, g, crawler, url, key, num)
    process(g, crawler, url, key, content)


def parse_list(g, crawler, key, content):
    # res = content.replace('null([', '')[:-2]
    j = json.loads(content)

    items = j['result']
    if len(items) == 0:
        return 0
    logger.info('%s returns %s items', key, len(items))
    # num = 0
    for item in items:
        itemkey = item['COMPANY_CODE']

        url = 'http://query.sse.com.cn/commonQuery.do?'
        # header = {'Referer': 'http://www.sse.com.cn/assortment/stock/list/info/company/index.shtml?COMPANY_CODE=%s'%itemkey}

        urls = {}
        sqlIdDict = {'baseinfo': 'COMMON_SSE_ZQPZ_GP_GPLB_C',
                     'executives': 'COMMON_SSE_ZQPZ_GG_GGRYLB_L',
                     'listingDate': 'COMMON_SSE_ZQPZ_GP_GPLB_AGSSR_C',
                     }
        for i in sqlIdDict:
            payload = {
                'sqlId': sqlIdDict[i],
                'productid': itemkey,
            }
            # payloads.append(payload)
            urls[i] = (url + urlencode(payload))

        global totalcnt
        totalcnt += 1
        logger.info('%s %s %s', item['COMPANY_CODE'], item['COMPANY_ABBR'], totalcnt)
        # print (url,item['COMPANY_ABBR'],totalcnt)

        run_detail(g, crawler, urls, itemkey)

    return len(items)


def run(g, crawler):
    while True:
        if len(KEYS) == 0:
            return
        key = KEYS.pop(0)

        while True:
            payload = {
                'stockType': 1,
                'pageHelp.cacheSize': 1,
                'pageHelp.beginPage': key,
                'pageHelp.pageSize': 25,

            }
            header = {'Referer': 'http://www.sse.com.cn/assortment/stock/list/share'}
            url = "http://query.sse.com.cn/security/stock/getStockListData2.do?&"
            url = url + urlencode(payload)

            result = crawler.crawl(url, headers=header, agent=True)
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

        if datestr != DATE and dt.hour >= 21:
            KEYS = [i + 1 for i in range(1000)]
            totalcnt = 0
            startTime = time.time()

            logger.info("sse %s start...", flag)
            g = GlobalValues.GlobalValues(13401, 36001, flag)

            threads = [gevent.spawn(run, g, sseCrawler()) for i in xrange(concurrent_num)]
            gevent.joinall(threads)

            logger.info("sse %s end.", flag)
            DATE = datestr

        if flag == "incr":
            gevent.sleep(60 * 60)
        else:
            gevent.sleep(86400 * 3)  # 3 days


if __name__ == "__main__":
    start_run(25, "incr")

    # urls={'baseinfo':'http://query.sse.com.cn/commonQuery.do?sqlId=COMMON_SSE_ZQPZ_GP_GPLB_C&productid=600000',
    #       'excutives':'http://query.sse.com.cn/commonQuery.do?sqlId=COMMON_SSE_ZQPZ_GG_GGRYLB_L&productid=600000',
    #       }
    # run_detail(GlobalValues.GlobalValues(13401, 36001, "incr"), BaseCrawler.BaseCrawler(), urls, 600000)
