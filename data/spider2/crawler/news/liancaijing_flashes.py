# -*- coding: utf-8 -*-
import os, sys, datetime, re, time
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, extract, db, util, url_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

# logger
loghelper.init_logger("crawler_liancaijing_newsf", stream=True)
logger = loghelper.get_logger("crawler_liancaijing_newsf")

NEWSSOURCE = "liancaijing"
RETRY = 3
TYPE = 60008
SOURCE = 13872
URLS = []
CURRENT_PAGE = 1
MAX_PAGE = 2
linkPattern = "liancaijing.com/alerts/\d+\.html"

columns = [
    {"column": "news", "max": 1},
]


class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find('class="fast-item') > 0:
            return True
        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)

        # 实现
        # def is_crawl_success(self, url, content):
        #     if content.find("</html>") == -1:
        #         return False
        #
        #     d = pq(html.fromstring(content.decode("utf-8")))
        #     title = d('head> title').text().strip()
        #     logger.info("title: %s url: %s", title, url)
        #     if title.find("车云") >= 0:
        #         return True
        #     return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    if title.find("车云") >= 0:
        return True
    return False


def process_news(newsurl, d):
    # if has_news_content(content):
    if 1:
        try:
            title = d('.head-line a span').text()[1:-1]
            url = newsurl
            key = url.split('/')[-1].replace('.html', '')

            post_time = d.attr('data-ymd') + ' ' + d('.head-line').text().split()[0]
            logger.info(post_time)
            news_time = datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M")

            logger.info("title:%s, date:%s", title, news_time)

            flag, domain = url_helper.get_domain(url)
            dnews = {
                "date": news_time - datetime.timedelta(hours=8),
                "title": title,
                "link": url,
                "createTime": datetime.datetime.now(),
                "source": SOURCE,
                "key": key,
                "key_int": int(key),
                "type": TYPE,
                "original_tags": [],
                "processStatus": 0,
                # "companyId":companyId,
                "companyIds": [],
                "category": None,
                "domain": domain,
                "categoryNames": []
            }

            dcontents = []
            description = d('.intro').next().text()
            if description is not None:
                dc = {
                    "rank": 1,
                    "content": "链财经快讯",
                    "image": "",
                    "image_src": "",
                }

                dcontents.append(dc)
                dc = {
                    "rank": 2,
                    "content": title,
                    "image": "",
                    "image_src": "",
                }
                dcontents.append(dc)
                dc = {
                    "rank": 3,
                    "content": description,
                    "image": "",
                    "image_src": "",
                }
                dcontents.append(dc)

                logger.info(description)

            dnews["contents"] = dcontents

            brief = util.get_brief_from_news(dcontents)

            post = util.get_posterId_from_news(dcontents)
            dnews["postId"] = post
            # dnews["post"] = post
            dnews["brief"] = brief
            if news_time > datetime.datetime.now():
                logger.info("Time: %s is not correct with current time", news_time)
                dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s", nid)
            # collection_news.insert(dnews)
        except:
            pass
    return


def process(content, flag):
    d = pq(html.fromstring(content.decode("utf-8")))
    for a in d('.fast-item'):
        link = d(a)('.head-line a').attr("href").strip()
        if re.search(linkPattern, link):
            logger.info("Link: %s is right news link", link)

            # check mongo data if link is existed
            mongo = db.connect_mongo()
            collection_news = mongo.article.news
            item = collection_news.find_one({"link": link})
            mongo.close()

            if (item is None or flag == "all") and link not in URLS:
                process_news(link, d(a))
        else:
            # logger.info(link)
            pass

    return len(URLS)


def run(flag, column, listcrawler, newscrawler, concurrent_num):
    global CURRENT_PAGE
    cnt = 1
    while True:
        key = CURRENT_PAGE

        if flag == "all":
            if key > column["max"]:
                return
        else:
            if cnt == 0 or key > column["max"]:
                return

        CURRENT_PAGE += 1

        url = "http://liancaijing.com/alerts"

        while True:
            result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        # threads = [gevent.spawn(run_news, column, newscrawler) for i in xrange(concurrent_num)]
                        # gevent.joinall(threads)
                        # exit()
                        run_news(column, newscrawler)
                except Exception, ex:
                    logger.exception(ex)
                    cnt = 0
                break
                # elif result['get'] == 'redirect' and r


def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = ListCrawler()
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            time.sleep(60 * 15)  # 30 minutes
        else:
            return
            # gevent.sleep(86400*3)   #3 days


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(1, "all")
            # else:
            #     link = param
            #     crawler_news({}, NewsCrawler(), link)
    else:
        start_run(1, "incr")
