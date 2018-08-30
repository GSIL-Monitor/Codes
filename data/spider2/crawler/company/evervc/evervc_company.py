# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, time
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey;

monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, extract, db, util, url_helper, download, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import crawler_util

# logger
loghelper.init_logger("crawler_evervc_company", stream=True)
logger = loghelper.get_logger("crawler_evervc_company")

SOURCENAME = "evervc"

SOURCE = 13838
URLS = []


class Evervccrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)  # todo

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find('<ol class="breadcrumb">') >= 0 or content.find('Opos，你访问的页面找不到了！') >= 0:
                return True
            elif content.find('btn-apply1 invest require_auth') >= 0 or content.find('btn-apply1-disabled') >= 0:
                return True
            else:
                logger.info('unsuccessful:%s', url)

            return False
        return False


def process(crawler):
    global UNAVAILABLE
    while True:
        if len(URLS) == 0: return
        linkDict = URLS.pop(0)

        while True:
            url = linkDict['href']
            result = crawler.crawl(url)
            if result['get'] == 'success':
                d = pq(html.fromstring(result['content'].decode("utf-8")))

                # title = linkDict['title']
                key = url.split('startups/')[-1]
                #
                # tags = []
                # for tag in d('.word_list').text().split():
                #     if tag.strip() not in tags: tags.append(tag)

                if result['content'].find(u'Opos，你访问的页面找不到了') >= 0:
                    type = -1  # 404
                    UNAVAILABLE += 1
                elif result['content'].find('btn-apply1 invest require_auth') >= 0:
                    type = -2  # 孵化器
                elif result['content'].find('btn-apply1-disabled') >= 0:
                    type = -3  # 已关闭孵化器
                else:
                    typeStr = d('.breadcrumb li:nth-child(2)').text().strip()
                    if typeStr == u'融资项目':
                        type = 36001
                    elif typeStr == u'投资机构':
                        type = 36003
                    else:
                        logger.info('new case:%s', url)
                        exit()

                crawler.save(SOURCE, type, url, key, result['content'])
                logger.info('saving %s %s %s %s\n%s', SOURCE, type, url, key, '#' * 166)

                break


def run_all(crawler, concurrent_num, flag, n):
    global UNAVAILABLE
    # page = crawler_util.get_latest_key_int(SOURCE,{'$gt':-10})
    page = crawler_util.get_latest_key_int(SOURCE, 36001)
    page = 71554 - 1
    while True:
        UNAVAILABLE = 0
        for i in range(n):
            page += 1
            href = 'http://www.evervc.com/startups/%s' % (page)
            title = ''

            linkDict = {
                "href": href,
                "title": title,
            }

            mongo = db.connect_mongo()
            collection = mongo.raw.projectdata

            key = page
            item = collection.find_one({"source": SOURCE, 'key_int': int(key)})
            if item is None or flag == 'all':
                logger.info('not exists %s ,%s ' % (href, title))
                URLS.append(linkDict)
            else:
                logger.info('already exists %s , %s', href, title)
            mongo.close()

        threads = [gevent.spawn(process, crawler) for i in
                   xrange(concurrent_num)]
        gevent.joinall(threads)

        if UNAVAILABLE == n:
            logger.info('over %s retries, stop ', n)
            break
        else:
            logger.info('keep trying due to only %s retries ', UNAVAILABLE)


def run(crawler, concurrent_num, flag, n):
    for page in range(n):
        page += 1
        url = 'http://www.evervc.com/today?page=%s' % (page)

        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                d = pq(html.fromstring(result['content'].decode("utf-8")))
                items = d('.eventset-latest-list li')
                for i in items:
                    href = 'http://www.evervc.com' + d(i)('.name a').attr('href').strip()
                    title = d(i)('.name a').text()

                    linkDict = {
                        "href": href,
                        "title": href,
                    }

                    mongo = db.connect_mongo()
                    collection = mongo.raw.projectdata

                    key = href.split('startups/')[-1]

                    item = collection.find_one({"source": SOURCE, 'key_int': int(key)})
                    if item is None or flag == 'all':
                        logger.info('not exists %s ,%s ' % (href, title))
                        URLS.append(linkDict)
                    else:
                        logger.info('already exists %s , %s', href, title)
                    mongo.close()

                break

        if len(URLS)==0:
            logger.info('page %s has no more fresh item',page)
            break

        threads = [gevent.spawn(process, crawler) for i in
                   xrange(concurrent_num)]
        gevent.joinall(threads)


def start_run(concurrent_num, flag, n):
    while True:
        logger.info("%s company %s start...", SOURCENAME, flag)

        evervccrawler = Evervccrawler()
        # download_crawler = download.DownloadCrawler(use_proxy=False)

        run(evervccrawler, concurrent_num, flag, n)

        logger.info("%s company %s end.", SOURCENAME, flag)

        # return

        if flag == "incr":
            logger.info('sleeping')
            gevent.sleep(60 * 8)  # 30 minutes
        else:
            return
            # gevent.sleep(86400*3)   #3 days


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(25, "incr",5)
        elif param == "all":
            start_run(25, "all",5)
        else:
            link = param
            URLS.append({'href':link})
            process(Evervccrawler())

    else:
        start_run(25, 'incr', 5)


