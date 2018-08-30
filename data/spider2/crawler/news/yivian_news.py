# -*- coding: utf-8 -*-
import os, sys, json, re
import datetime
from lxml import html
from pyquery import PyQuery as pq
import gevent

# from gevent import monkey;monkey.patch_all()

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
loghelper.init_logger("crawler_yivian_news", stream=True)
logger = loghelper.get_logger("crawler_yivian_news")


NEWSSOURCE = "yivian"
RETRY = 3
TYPE = 60005
SOURCE = 13873
URLS = []
CURRENT_PAGE = 1
# https://yivian.com/news/42576.html
linkPattern = "yivian.com/\w+/\d+\.html"
Nocontents = [
]
columns = [

    {"column": "news", "max": 3},
    {'column':'capital',"max": 3}
]


class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=10, use_proxy=True):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout, use_proxy=use_proxy)

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find('class="post-content"') >= 0:
                return True
            return False
        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=10, use_proxy=True):
        BaseCrawler.BaseCrawler.__init__(self,timeout=timeout, use_proxy=use_proxy)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("映维") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    temp = title.split("|")
    if len(temp) < 2:
        return False
    return True


def process_news(column, newsurl, content, newspost, download_crawler):
    if has_news_content(content):
        logger.info('here')

        d = pq(html.fromstring(content.decode("utf-8", 'ignore')))

        category = None
        categoryNames = []

        key = newsurl.split("/")[-1].replace(".html", "")

        type = TYPE

        title = d('div.post-inner> h1').text().strip()

        if title is None or title == "":
            return

        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        if collection_news.find_one({'title': title}) is not None:
            mongo.close()
            return

        (posturl, width, height) = parser_mysql_util.get_logo_id_new(newspost, download_crawler, SOURCE, key, "news")

        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        tags = []
        articletags = d("meta[name='keywords']").attr('content')
        if articletags is not None:
            for tag in articletags.split(","):
                if tag is not None and tag.strip() != "" and tag not in tags and tag != title:
                    tags.append(tag)

        try:
            brief = d("meta[name='description']").attr("content")
        except:
            brief = None

        try:
            post_time = d("p.post-byline> time.published").text().strip()

            logger.info('时间：%s' % post_time)

            p = re.compile(u'(年|月)')
            post_time = p.sub('-', post_time).replace('日', '')

            logger.info(post_time)
            news_time = extract.extracttime(post_time)
            logger.info("news-time: %s", news_time)
        except Exception, e:
            logger.info(e)
            news_time = datetime.datetime.now()

        if news_time is None:
            news_time = datetime.datetime.now()

        article = d('div.entry-inner').html()

        contents = extract.extractContents(newsurl, article)

        logger.info("%s, %s, %s, %s -> %s, %s. %s", key, title, news_time, ":".join(tags), category, brief, post)

        flag, domain = url_helper.get_domain(newsurl)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": newsurl,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": int(key),
            "type": type,
            "original_tags": tags,
            "processStatus": 0,
            "companyIds": [],
            "category": category,
            "domain": domain,
            "categoryNames": categoryNames,
        }
        dcontents = []
        rank = 1
        for c in contents:

            if c['data'].find('文章相关引用及参考') >= 0 or c['data'].find('读者QQ群') >= 0:
                continue

            if c['type'] == 'text':
                dc = {
                    'rank': rank,
                    'content': c['data'],
                    'image': '',
                    'image_src': '',
                }
            else:
                if download_crawler is None:
                    dc = {
                        "rank": rank,
                        "content": "",
                        "image": "",
                        "image_src": c["data"],
                    }
                else:
                    (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler, SOURCE,
                                                                                key, "news")
                    if imgurl is not None:
                        dc = {
                            "rank": rank,
                            "content": "",
                            "image": str(imgurl),
                            "image_src": "",
                            "height": int(height),
                            "width": int(width)
                        }
                    else:
                        continue

            dcontents.append(dc)
            rank += 1

        dnews['contents'] = dcontents

        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        if post is None or post.strip() == "":
            post = util.get_posterId_from_news(dcontents)

        if download_crawler is None:
            dnews["post"] = post
        else:
            dnews["postId"] = post
        dnews["brief"] = brief

        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)

        logger.info(json.dumps(dnews, ensure_ascii=False, cls=util.CJsonEncoder))

        if title is not None and len(contents) > 0:
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s", nid)
            pass
        mongo.close()


def crawler_news(column, crawler, newsurl, newspost, download_crawler):
    retry = 0
    while True:
        result = crawler.crawl(newsurl, agent=True)

        if result['get'] == 'success':
            try:
                process_news(column, newsurl, result['content'], newspost, download_crawler)
            except Exception, ex:
                logger.exception(ex)
            break
        retry += 1
        if retry > 20: break


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL["post"], download_crawler)


def process(content, flag):
    if content.find("article") >= 0:
        d = pq(html.fromstring(content.decode("utf-8","ignore")))

        for li in d('div>article'):
            try:
                href = d(li)('h2>a').attr("href").strip()
                link = href

                if re.search(linkPattern, link):

                    title = d(li)('h2>a').text()
                    logger.info("title:%s", title)
                    post = d(li)('div.post-thumbnail> a> img').attr('src')

                    mongo = db.connect_mongo()
                    collection_news = mongo.article.news
                    item = collection_news.find_one({"link": link})
                    item2 = collection_news.find_one({"title": title})
                    mongo.close()
                    if ((item is None and item2 is None) or flag == 'all') and link not in URLS:
                        linkmap = {
                            'link': link,
                            'post': post
                        }
                        URLS.append(linkmap)

                else:
                    pass
            except Exception, e:
                logger.info(e)
                logger.info('cannot get link')

    return len(URLS)

def run(flag, column, listcrawler, newscrawler, concurrent_num, download_crawler):
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

        url = "https://yivian.com/%s/page/%s" % (column['column'], key)

        while True:
            result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    logger.info(cnt)

                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        run_news(column, newscrawler, download_crawler)


                except Exception, ex:
                    logger.exception(ex)
                    cnt = 0
                break

def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        download_crawler = download.DownloadCrawler(use_proxy=False)

        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num, download_crawler)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            gevent.sleep(60*8)
        else:
            return


if __name__ == '__main__':
    flag = 'incr'
    concurrent_num = 1
    start_run(concurrent_num, flag)
