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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, extract, db, util, url_helper, download, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import crawler_util

# logger
loghelper.init_logger("crawler_zhihu_daily", stream=True)
logger = loghelper.get_logger("crawler_zhihu_daily")

SOURCENAME = "zhihu_daily"

SOURCE = 13610
TYPE = 'story'
URLS = []


class Zhihucrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)  # todo

    def is_crawl_success(self, url, content):
        if content is not None:
            if url.find('story') >= 0:
                pattern = '<div class="content">'
            else:
                pattern = '<div class="box">'

            if content.find(pattern) >= 0:
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

                # title = linkDict['title']
                key = linkDict['key']
                #
                # tags = []
                # for tag in d('.word_list').text().split():
                #     if tag.strip() not in tags: tags.append(tag)

                save(SOURCE, TYPE, url, key, result['content'])
                logger.info('saving %s %s %s %s\n%s', SOURCE, TYPE, url, key, '#' * 166)

                break


def run(crawler, concurrent_num, flag):
    if True:
        url = 'http://daily.zhihu.com/'

        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                d = pq(html.fromstring(result['content'].decode("utf-8")))
                items = d('.box')
                for i in items:
                    href = 'http://daily.zhihu.com' + d(i)('a').attr('href').strip()
                    title = d(i)('.title').text()
                    key = href.split('story/')[-1]

                    linkDict = {
                        "href": href,
                        "title": href,
                        "key": key,
                    }

                    mongo = db.connect_mongo()
                    collection = mongo.zhihu.raw

                    item = collection.find_one({"source": SOURCE, 'key_int': int(key)})
                    if item is None or flag == 'all':
                        logger.info('not exists %s ,%s ' % (href, title))
                        URLS.append(linkDict)
                    else:
                        logger.info('already exists %s , %s', href, title)
                    mongo.close()

                break

        threads = [gevent.spawn(process, crawler) for i in
                   xrange(concurrent_num)]
        gevent.joinall(threads)


def start_run(concurrent_num, flag):
    while True:
        logger.info("%s %s start...", SOURCENAME, flag)

        zhihucrawler = Zhihucrawler()
        # download_crawler = download.DownloadCrawler(use_proxy=False)

        run(zhihucrawler, concurrent_num, flag)

        logger.info("%s %s end.", SOURCENAME, flag)

        # return

        if flag == "incr":
            logger.info('sleeping')
            gevent.sleep(60 * 30)  # 30 minutes
        else:
            return
            # gevent.sleep(86400*3)   #3 days


def save(SOURCE, TYPE, url, key, content):
    logger.info("Saving: %s", url)
    try:
        key_int = int(key)
    except:
        key_int = None

    collection_content = {
        "date": datetime.datetime.now(),
        "source": SOURCE,
        "type": TYPE,
        "url": url,
        "key": key,
        "key_int": key_int,
        "content": content
    }

    mongo = db.connect_mongo()
    collection = mongo.zhihu.raw
    if collection.find_one({"source": SOURCE, "type": TYPE, "key": key}) is not None:
        collection.delete_one({"source": SOURCE, "type": TYPE, "key": key})
    collection.insert_one(collection_content)
    mongo.close()
    logger.info("Saved: %s", url)

if __name__ == "__main__":
    default_num = 1
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(default_num, "incr")
        elif param == "all":
            start_run(default_num, "all")
        else:
            link = param
            URLS.append({'href': link})
            process(Zhihucrawler())

    else:
        start_run(default_num, 'incr')
