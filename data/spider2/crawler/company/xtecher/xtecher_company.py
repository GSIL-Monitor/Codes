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

# logger
loghelper.init_logger("crawler_xtecher_news", stream=True)
logger = loghelper.get_logger("crawler_xtecher_news")

SOURCENAME = "xtecher"

SOURCE = 13821
TYPE = 36001
URLS = []


class Xtechercrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)  # todo

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find('<li class="contentBox">') >= 0 or content.find('非常抱歉，没有找到结果') >= 0:
                return True
            if content.find('<ul class="word_list">') >= 0:
                return True
            return False
        return False


def process(crawler):
    while True:
        if len(URLS) == 0: return
        linkDict = URLS.pop(0)

        while True:
            url = linkDict['href']
            result = crawler.crawl(url)
            if result['get'] == 'success':
                # d = pq(html.fromstring(result['content'].decode("utf-8")))
                #
                # title = linkDict['title']
                key = url.split('pid=')[-1]
                #
                # tags = []
                # for tag in d('.word_list').text().split():
                #     if tag.strip() not in tags: tags.append(tag)


                crawler.save(SOURCE, TYPE, url, key, result['content'])
                logger.info('saving %s %s %s %s\n%s', SOURCE, TYPE, url, key, '#' * 166)

                break


def run(crawler, concurrent_num,flag):
    page = 1
    while True:
        url = 'http://xtecher.com/Website/Search/searchProjectResult?&page=%s' % (page)

        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                # if result['content'].find('非常抱歉，没有找到结果')>0:
                #     break

                d = pq(html.fromstring(result['content'].decode("utf-8")))

                for item in d('.contentBox'):
                    title = d(item)('h4').text()
                    href = 'http://xtecher.com' + d(item)('.leftcontent > a').attr('href')
                    key = href.split('pid=')[-1]

                    # print (title), href, key

                    linkDict = {
                        "href": href,
                        "title": title,
                    }

                    mongo = db.connect_mongo()
                    collection = mongo.raw.projectdata

                    item = collection.find_one({"source": SOURCE,'type':TYPE,'key_int':int(key)})
                    if item is None or flag == 'all':
                        logger.info( 'not exists %s ,%s '%(href,title))
                        URLS.append(linkDict)
                    else:
                        logger.info('already exists %s , %s', href, title)
                    mongo.close()

                break

        if len(URLS) == 0:
            logger.info('page %s returns no fresh item', page)
            break

        threads = [gevent.spawn(process, crawler) for i in
                   xrange(concurrent_num)]
        gevent.joinall(threads)

        page += 1


def start_run(concurrent_num, flag):
    while True:
        logger.info("%s company %s start...", SOURCENAME, flag)

        xtechercrawler = Xtechercrawler()
        # download_crawler = download.DownloadCrawler(use_proxy=False)

        run(xtechercrawler, concurrent_num,flag)

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
            start_run(25, "incr")
        elif param == "all":
            start_run(25, "all")

    else:
        start_run(25, 'incr')
