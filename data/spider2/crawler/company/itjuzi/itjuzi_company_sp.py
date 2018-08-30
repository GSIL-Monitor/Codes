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
loghelper.init_logger("crawler_itjuzi_company_sp", stream=True)
logger = loghelper.get_logger("crawler_itjuzi_company_sp")


class ItjuziCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title == "找不到您访问的页面":
            #return True
            return False
        if title.find("IT桔子") >= 0:
            return True
        return False


def has_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    temp = title.split("|")
    if len(temp) != 2:
        return False
    if temp[1].strip() != "IT桔子":
        return False
    if temp[0].strip() == "":
        return False
    return True


def process(g, crawler, url, key, content):
    if has_content(content):
        crawler.save(g.SOURCE, g.TYPE, url, key, content)
        g.latestIncr()


def crawl(crawler, key ,g):
    url = "http://www.itjuzi.com/company/%s" % key
    retries = 0
    headers={}
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0'
    headers['User-Agent'] = user_agent
    while True:
        result = crawler.crawl(url, headers=headers)
        if result['get'] == 'success':
            #logger.info(result["content"])
            try:
                process(g, crawler, url, key, result['content'])
            except Exception,ex:
                logger.exception(ex)
            break
        else:
            if result.has_key("content") is False or result["content"] is None or result["content"].strip() == "" or result["content"].find("</html>") == -1:
                continue
            d = pq(html.fromstring(result["content"]))
            title = d('head> title').text().strip()
            if title == "找不到您访问的页面":
                if retries >= 2:
                    break
                retries += 1



def run(g, crawler):
    while True:
        if g.finish(num=25):
            return
        key = g.nextKey()
        crawl(crawler, key, g)


def start_run(concurrent_num, flag):
    while True:
        logger.info("Itjuzi company %s start...", flag)
        g = GlobalValues.GlobalValues(13030, 36001, flag)

        threads = [gevent.spawn(run, g, ItjuziCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Itjuzi company %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*50)        #30 minutes
        else:
            gevent.sleep(60*60)   #12 hour


if __name__ == "__main__":
    g = GlobalValues.GlobalValues(13030, 36001, "incr", back=0)
    crawler = ItjuziCrawler()
    for param in [58568, 21359, 58293, 23203, 21348, 54442, 21283, 53902, 53820, 21262, 53922, 58055, 55111, 58179, 54430, 21232, 58089, 57948, 20711, 21204, 54490, 30706, 58006, 57840, 21201, 21191, 21168, 21150, 21147, 21132, 21130, 21129, 21110, 21104, 21088, 21087, 55104, 21050, 21024, 21004, 55086, 35644, 20993, 54874, 20983, 54892, 20935, 20874, 41490, 20840, 20831, 20822, 20805, 20801, 20799, 53291, 20776, 20766, 20844, 20763, 54395, 54532, 20717, 20391, 20712, 20706, 20659, 20646, 20640, 20637, 20627, 20622, 20621, 20620, 20608, 20598, 54503, 53564, 53552, 53496, 53473, 53381, 53292, 54253, 53617, 20597, 20579, 20574, 44178, 53468, 54166, 53763, 53545, 53852, 53299, 20569, 20526, 20521, 20517, 20503, 20500, 44383, 53394, 20499, 20456, 20446, 20437, 53327, 20425, 20422, 53864, 53597, 53865, 20405, 20400, 8250, 8249, 20390, 53602, 53255, 53360, 26202, 20363, 26236, 26242, 11981, 28947, 26243, 20351, 20349, 20329, 26249, 20328, 26257, 20326, 26260, 20267, 53269, 20895, 36012, 20516, 31929, 32613, 31939, 31415, 30728, 30895, 28928, 28265, 23207, 19757, 18417, 18408, 18158, 5548, 14553, 9012, 149, 294, 240, 6806, 5735, 4437, 238]:
        key = str(int(param))
        # g = GlobalValues.GlobalValues(13030, 36001, "incr", back=0)
        crawl(crawler, key, g)
    # else:
    #     start_run(1, "incr")