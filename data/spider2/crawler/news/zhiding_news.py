# -*- coding: utf-8 -*-
import os, sys, json, re
import datetime
import requests
from lxml import html
from pyquery import PyQuery as pq
import gevent
import time
import uuid

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
loghelper.init_logger("crawler_zhiding_news", stream=True)
logger = loghelper.get_logger("crawler_zhiding_news")

NEWSSOURCE = 'zhiding'
RETRY = 3
TYPE = 60005
SOURCE = 13877
URLS = []
linkPattern = "http://.*?\.zhiding\.cn/.*"
Maxpage = 3


class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=10, use_proxy=True):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout, use_proxy=use_proxy)

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find('qu_left') >= 0:
                return True
            return False
        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=10, use_proxy=True):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout, use_proxy=use_proxy)

    def is_crawl_success(self, url, content):
        content = content.decode('gbk').encode('utf8')
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("至顶网") >= 0:
            return True
        return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    if d('h1').attr('class').find('foucs_title') >= 0:
        return True
    return False


def process_news(newsurl, content, newspost, download_crawler):
    if has_news_content(content):
        logger.info('here')

        d = pq(html.fromstring(content.decode('utf-8', 'ignore')))

        category = None
        categoryNames = []
        Type = TYPE
        tags = []
        brief = None


        title = d('h1').text().strip()
        if title is None or title == "":
            return
        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        if collection_news.find_one({'title': title}) is not None:
            mongo.close()
            return

        # "http://security.zhiding.cn/security_zone/2018/0424/3106026.shtml"
        # "http://digital.zhiding.cn/2018/0424/3106025.shtml"
        rekey = re.search('http://.*?zhiding.cn/.*?\d{4}/\d{4}/(\d*)\.shtml', newsurl)
        key = rekey.group(1)
        logger.info('key:%s', key)

        try:
            (posturl, width, height) = parser_mysql_util.get_logo_id_new(newspost, download_crawler, SOURCE, key, "news")
        except:
            posturl = None
        if posturl is not None:
            post = str(posturl)
        else:
            post = None


        try:
            timetext = d('div.qu_zuo> p').eq(0).text().strip()
            retime = re.search('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',timetext)
            if retime:
                post_time = retime.group(1)
            else:
                res = re.search(u'(\d{4})年(\d+)月(\d+)日', timetext)
                year = res.group(1)
                month = res.group(2)
                if len(month) == 1:
                    month = '0' + month
                day = res.group(3)
                if len(day) == 1:
                    day = '0' + day
                post_time = '{}-{}-{}'.format(year, month, day)
            news_time = extract.extracttime(post_time)
        except Exception as e:
            logger.info(e)
            news_time = datetime.datetime.now()
        if news_time is None:
            news_time = datetime.datetime.now()
        # logger.info('time:%s',news_time)

        article = d('div.qu_ocn').html()
        contents = extract.extractContents(newsurl, article,document=True)

        flag, domain = url_helper.get_domain(newsurl)

        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": newsurl,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": int(key),
            "type": Type,
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


def crawler_news(newsurl, newspost, newscrawler, download_crawler):
    retry = 0
    while True:
        result = newscrawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            try:
                process_news(newsurl, result['content'].decode('gbk').encode('utf8'), newspost, download_crawler)
            except Exception, ex:
                logger.exception(ex)
            break
        retry += 1
        if retry > 3: break


def run_news(newscrawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)
        crawler_news(URL['link'], URL['post'], newscrawler, download_crawler)


def process(content, flag):
    if content.find("qu_loop") >= 0:
        d = pq(html.fromstring(content.decode('utf-8', 'ignore')))
        for lis in d('div.qu_loop'):
            try:
                href = d(lis)('b> a').attr('href').strip()
                link = href
                if re.search(linkPattern, link):
                    title = d(lis)('b> a').text().strip()
                    logger.info("title:%s", title)

                    post = None
                    img_url = d(lis)('a> img').attr('src')
                    if img_url:
                        post = 'http:' + img_url.strip()
                        # logger.info('post:%s',post)

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

            except Exception as e:
                logger.info(e)
                logger.info("cannot get link")
    return len(URLS)


def run(flag, listcrawler, newscrawler, download_crawler, page):
    cnt = 1
    while True:
        url = "http://www.zhiding.cn/lists-0-1-%s-0-0.htm" % page
        if cnt == 0:
            return
        while True:
            result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'].decode('gbk').encode('utf8'), flag)
                    logger.info(cnt)

                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        run_news(newscrawler, download_crawler)

                except Exception, ex:
                    logger.exception(ex)
                    cnt = 0
                    break
                return


def start_run(flag):
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        download_crawler = download.DownloadCrawler(use_proxy=False)

        page = 1
        while page <= Maxpage:
            run(flag, listcrawler, newscrawler, download_crawler, page)
            page += 1

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            time.sleep(60 * 30)
        else:
            return


if __name__ == '__main__':
    flag = 'incr'
    start_run(flag)
