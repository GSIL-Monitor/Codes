# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, time
from lxml import html
from pyquery import PyQuery as pq
import requests

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download, traceback_decorator

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool

#logger
loghelper.init_logger("crawler_dailysocial_news", stream=True)
logger = loghelper.get_logger("crawler_dailysocial_news")

NEWSSOURCE = "dailysocial"
RETRY = 3
TYPE = 60004
SOURCE =13890
URLS = []
CURRENT_PAGE = 1
linkPattern = "/post/.*"
Nocontents = [
]
columns = [
    {"column": "post", "max": 1},
]




class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=10):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

        # 实现

    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
        title = d('head> title').text().strip()
        # logger.info("title: %s url: %s", title, url)
        if title.find("Dailysocial") >= 0:
            return True
        return False

class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
        title = d('head> title').text().strip()
        # logger.info("title: %s url: %s", title, url)
        if title.find("Dailysocial") >= 0:
            return True
        return False

def has_news_content(content):
    if content.find('sb-site'):
        return True
    return False

def process_news(column, d_map, content, download_crawler):
    if has_news_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        d = pq(html.fromstring(content.decode("utf-8", "ignore")))

        category = None
        categoryNames = []
        type = TYPE

        key = d('div#sb-site> article').attr('data-id')
        title = d('div#sb-site> article> section#article-header> h2> strong> a').text().strip()
        newspost = d('div#sb-site> article> section#article-image> div> figure> img').attr('src')
        logger.info('newspost:%s'%newspost)
        newsurl = d_map['link']

        (posturl, width, height) = parser_mysql_util.get_logo_id_new(newspost, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        tags = []
        brief = d("meta[name='description']").attr('content')
        post_time = d('div#sb-site> article> section#article-meta> span> em').text().strip()
        news_time = None
        is_re = re.search('(\d{2}-\d{2}-\d{4})', post_time)
        is_re2 = re.search('(\d) hours ago', post_time)
        if is_re:
            news_time = datetime.datetime.strptime(is_re.group(1), "%d-%m-%Y")
        elif is_re2:
            news_time = datetime.datetime.now() - datetime.timedelta(hours=int(is_re2.group(1)))
        elif post_time.find('a moment') >= 0:
            news_time = datetime.datetime.now()

        logger.info("%s, %s, %s, %s -> %s, %s", key, title, news_time, ":".join(tags), category, brief)

        article = d('div#sb-site> article> section#article-content> div.post-content> div.row').html()
        is_re3 = re.search("(<strong>DailySocial\.id.*?</p>)",article, re.S)
        if is_re3:
            article = article.replace(is_re3.group(1), '')
        contents = extract.extractContents(newsurl, article, document=False)

        flag, domain = url_helper.get_domain(newsurl)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": newsurl,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": None,
            "type": type,
            "original_tags": tags,
            "processStatus": 1,
            # "companyId": None,
            "companyIds": [],
            "category": category,
            "domain": domain,
            "categoryNames": categoryNames
        }
        dcontents = []
        rank = 1
        for c in contents:
            if c["data"].find("Also Read") >= 0 or c['data'].find('function()') >= 0:
                continue
            # if c['data'].find('caption') >= 0:
            #     c['data'] = c['data'].replace('caption','')

            if c["type"] == "text":
                dc = {
                    "rank": rank,
                    "content": c["data"],
                    "image": "",
                    "image_src": "",
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
        dnews["contents"] = dcontents
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
        # logger.info(json.dumps(dnews,ensure_ascii=False,indent=2,cls=util.CJsonEncoder))

        if title is not None and len(contents) > 0:
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s", nid)
            pass
        return

def crawler_news(column, crawler, d_map, download_crawler):
    # global Proxies
    retry = 0
    while True:
        # if Proxies is None:
            # Proxies = get_proxy(http_type='https')
        logger.info('---->retry:%d<----'%retry)
        try:
            newsurl = d_map['link']
            logger.info('crawl url:%s'%newsurl)
            result = crawler.crawl(newsurl, agent=True)
            if result['get'] == 'success':
                try:
                    process_news(column, d_map, result['content'], download_crawler)
                except Exception, ex:
                    logger.exception(ex)
                    raise ValueError('something wrong at process nrews')
                break
        except Exception,e:
            logger.info('cralwer_news requests error :%s'%e)
            # Proxies = get_proxy(http_type='https')
        retry += 1
        if retry > 20:
            break

def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL, download_crawler)

def process(content, flag):
    if content.find("col-md-12") >= 0:
        d = pq(html.fromstring(content.decode('utf-8','ignore')))
        for a in d('section#weeklyAndLatest> div> div> div.col-md-9> div.col-md-4'):
            link = d(a)('a').attr('href')
            title = d(a)('div.title').text().strip()
            if re.search(linkPattern, link) and title is not None and title.strip() != "":
                linknew = 'https://dailysocial.id' + link
                logger.info("Link: %s is right news link: %s", linknew, title,)
                mongo = db.connect_mongo()
                collection_news = mongo.article.news
                item = collection_news.find_one({"link": linknew})
                item2 = collection_news.find_one({"title": title})
                mongo.close()

                if ((item is None and item2 is None) or flag == "all") and linknew not in URLS:
                    linkmap = {
                        "link": linknew,
                        'title':title,
                    }
                    URLS.append(linkmap)
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

        url = 'https://dailysocial.id/business/?page=1'

        while True:
            result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        # logger.info(URLS)
                        run_news(column, newscrawler, download_crawler=None)
                except Exception, ex:
                    logger.exception(ex)
                    cnt = 0
                break

@traceback_decorator.try_except
def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    # global Proxies
    while True:
        # Proxies = get_proxy(http_type='https')
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            time.sleep(60*60*3)
        else:
            return


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(1, "all")
        else:
            link = param
            download_crawler = None
            crawler_news(None,NewsCrawler(),{'link':link , 'post':None} ,download_crawler)
    else:
        start_run(1, "incr")


