# -*- coding: utf-8 -*-
import os, sys,random, datetime
import urllib2
import urllib
import json
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
import loghelper,util

#logger
loghelper.init_logger("crawler_boss_company", stream=True)
logger = loghelper.get_logger("crawler_boss_company")

DATE = None

class BossCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=15):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if title.find("BOSS直聘验证码") >= 0:
            #logger.info(content)
            return False
        if title.find("BOSS直聘-互联网招聘神器！") >= 0:
            return False
        if title.find("BOSS直聘") >= 0:
            return True
        #logger.info(content)
        return False



def has_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    temp = title.split("-")

    if len(temp) < 2:
        return False
    if temp[0].strip() == "BOSS直聘":
        return False
    return True

def process(g, crawler, url, key, content):
    #logger.info(content)
    if has_content(content):
        logger.info(key)
        crawler.save(g.SOURCE, g.TYPE, url, key, content)
        g.latestIncr()


def crawl(crawler, key, g):
    url = "https://www.zhipin.com/gongsi/%s.html?ka=company-intro" % key
    retry_times = 0
    retries = 0
    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            # logger.info(result["content"])
            try:
                process(g, crawler, url, key, result['content'])
            except Exception, ex:
                logger.exception(ex)
            break
        else:
            if result.has_key("content") is False or result["content"] is None or result["content"].strip() == "" or result["content"].find("</html>") == -1:
                continue
            d = pq(html.fromstring(result["content"]))
            title = d('head> title').text().strip()
            if title == "BOSS直聘-互联网招聘神器！":
                if retries >= 1:
                    break
                retries += 1

        retry_times += 1
        if retry_times > 30:
            break

def run(g, crawler):
    while True:
        if g.finish(num=20000):
            return
        key = g.nextKey()
        crawl(crawler, key, g)



def start_run(concurrent_num, flag):
    global DATE
    while True:
        dt = datetime.date.today()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        date_num = int(datestr) % 10
        logger.info("boss last back is %s", DATE)
        logger.info("boss company %s start for %s", flag, datestr)
        
        # if datestr != DATE and date_num == 4:
        #     logger.info("%s is 4! back to 2000", datestr)
        #     g = GlobalValues.GlobalValues(13055, 36001, flag, back=2000)
        #     DATE = datestr
        # else:
        g = GlobalValues.GlobalValues(13055, 36001, flag, back=0)

        #run(g, LagouCrawler())
        threads = [gevent.spawn(run, g, BossCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("boss company %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*30)        #30 minutes
        else:
            gevent.sleep(86400*3)   #3 days

        #break

if __name__ == "__main__":


    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(23, "all")
        else:
            key = str(int(param))
            g = GlobalValues.GlobalValues(13055, 36001, "incr", back=0)
            crawl(BossCrawler(), key, g)
    else:
        start_run(4, "incr")