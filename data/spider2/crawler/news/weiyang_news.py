# -*- coding: utf-8 -*-
import os, sys, json, re
import datetime
from lxml import html
from pyquery import PyQuery as pq
import gevent
import time



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



NEWSSOURCE = "weiyang"
RETRY = 3
TYPE = 60005
SOURCE = 13874
URLS = []
CURRENT_PAGE = 1
# http://www.weiyangx.com/279645.html
linkPattern = "weiyangx.com/\d+.html"
Nocontents = [
]
columns = [

    {"column": "investment-and-financing", "max": 1},
]


class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=10, use_proxy=True):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout, use_proxy=use_proxy)

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find('id="category-posts-list"') >= 0:
                return True
            return False
        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=10, use_proxy=True):
        BaseCrawler.BaseCrawler.__init__(self,timeout=timeout, use_proxy=use_proxy)

    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("未央网") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    temp = title.split(" ")
    if len(temp) < 2:
        return False
    return True


def process_news(column, newsurl, content, newspost, download_crawler):
    if has_news_content(content):
        logger.info('here')

        d = pq(html.fromstring(content.decode("utf-8", 'ignore')))

        if d.text().find('embed') >= 0:  # 排除视频文章
            logger.info('not article:%s'%newsurl)
            return

        category = None
        categoryNames = []

        key = newsurl.split("/")[-1].replace(".html", "")

        type = TYPE

        title = d('h1').text().strip()

        if title is None or title == "":
            return

        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        if collection_news.find_one({'title': title}) is not None:
            mongo.close()
            return

        try:
            (posturl, width, height) = parser_mysql_util.get_logo_id_new(newspost, download_crawler, SOURCE, key, "news")
        except:
            posturl = None
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
            post_time_1 = d("div.wyt-post-content-meta> div> p ").find('span').text().strip()
            post_time_2 = d("div.wyt-post-content-meta> div").find('p').next().text().strip()
            if post_time_1:
                post_time = post_time_1
            else:
                post_time = post_time_2

            if re.match('\d{2}-\d{2}', post_time):  # 匹配 03-19格式
                post_time = str(time.localtime()[0])+'-' + post_time

            news_time = extract.extracttime(post_time)
            logger.info("news-time: %s", news_time)
        except Exception, e:
            logger.info(e)
            news_time = datetime.datetime.now()

        if news_time is None:
            news_time = datetime.datetime.now()

        article = d('article.wyt-post-content').html()

        contents = extract.extractContents(newsurl, article,document=True)

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

        if contents[0]['type'] == 'img':
            del contents[0]

        for c in contents:
            # logger.info("%s-%s",c["type"],c["data"])
            if c['type'] == 'text':

                if re.match('^\d+$', c['data']) or c['data'].find('收藏') >= 0 or c['data'].find('投融资') >= 0 or c['data'].find('阅读时间') >= 0 \
                        or c['data'].find('违者必究') >= 0 or c['data'].find('微信公众号') >= 0 or c['data'].find('微信扫描') >= 0 \
                        or c['data'].find('点击获取完整版报告') >= 0 or c['data'].find('作者原创，微信号') >= 0:
                    continue

                # if c['data'].find('译者') >= 0:
                #     c['data'] = c['data'].split(' ')[0]
                #
                # if c['data'].find('来源') >= 0:
                #     c['data'] = c['data'].split('|')[0]

                if c['data'].find('| 未央网') >= 0:
                    c['data'] = c['data'].replace('| 未央网',' ')

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
            # logger.info(c["data"])
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
        if retry > 3: break


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL["post"], download_crawler)


def process(content, flag):
    if content.find("category-posts-list") >= 0:
        d = pq(html.fromstring(content.decode("utf-8","ignore")))

        for li in d('div.category-post-node'):
            try:
                href = d(li)('a').attr("href").strip()
                link = href

                if re.search(linkPattern, link):

                    title = d(li)('h2').text().strip()
                    logger.info("title:%s", title)

                    post = None
                    img_url = d(li)('a> div').attr('data-original')
                    if img_url:
                        post = img_url.strip()

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

def run(flag, column, listcrawler, newscrawler, download_crawler):
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

        url = "http://www.weiyangx.com/category/%s/page/%s" % (column['column'], key)

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

def start_run(flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        download_crawler = download.DownloadCrawler(use_proxy=False)

        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler,  download_crawler)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            gevent.sleep(60*8)
        else:
            return


if __name__ == '__main__':
    flag = 'incr'

    start_run(flag)
