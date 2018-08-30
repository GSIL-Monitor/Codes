# -*- coding: utf-8 -*-
import os, sys
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
import loghelper

#logger
loghelper.init_logger("crawler_fellowPlus_investor", stream=True)
logger = loghelper.get_logger("crawler_fellowPlus_investor")

KEYS = [i for i in range(211,212)]


class FellowPlusCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        # logger.info("title: " + title)
        if title.find("FellowPlus") > 0:
            return True

        return False

# fc = FellowPlusCrawler()
# aa = fc.crawl("https://fellowplus.com/investors?page=1&per-page=10", agent=True)

def has_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    if title.find("FellowPlus") > 0:
        return True


def process(g, crawler, url, key, num, content):
    if has_content(content):
        crawler.save(g.SOURCE, g.TYPE, url, str(key)+'_'+str(num), content)
        # g.latestIncr()


def parse_investor(g, crawler, key, content):
    d = pq(content)
    users = d('.user-item')
    if len(users) == 0:
        return
    num = 0
    for user in users:
        num += 1
        user_link = pq(user)('a').attr('href')
        run_investor(g, crawler, user_link, key, num)


def run_investor(g, crawler, url, key, num):
    # result = crawler.crawl(url,agent=True)
    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            process(g, crawler, url, key, num, result['content'])
            break
            # gevent.spawn(run_investor, g, crawler, url, key, num)


def run(g, crawler):
    while True:
        # if key is None:
        #     if g.finish():
        #         return
        #     key = g.nextKey()
        if len(KEYS) == 0:
            return
        key = KEYS.pop(0)

        url = "https://fellowplus.com/investors?page=%s&per-page=10" % key
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
                    parse_investor(g, crawler, key, result['content'])
                except Exception, ex:
                    logger.exception(ex)
                break


def start_run(concurrent_num, flag):
    while True:
        logger.info("FellowPlus investor %s start...", flag)
        g = GlobalValues.GlobalValues(13042, 36004, flag)
        # fc = FellowPlusCrawler()
        # logger.info(g)
        # for i in range(concurrent_num):
        #     gevent.spawn(run, g, FellowPlusCrawler())
        # g.wait()
        threads = [gevent.spawn(run, g, FellowPlusCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("FellowPlus investor %s end.", flag)
        if flag == "incr":
            gevent.sleep(60*60*24)        #1 day
        else:
            gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    start_run(10, "all")