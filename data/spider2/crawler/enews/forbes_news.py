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
import loghelper, extract, db, util, url_helper, download, traceback_decorator

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool

# logger
loghelper.init_logger("crawler_forbes_news", stream=True)
logger = loghelper.get_logger("crawler_forbes_news")

NEWSSOURCE = "forbes"
RETRY = 3
TYPE = 60004
SOURCE = 13883
URLS = []
CURRENT_PAGE = 1
# https://www.avcj.com/avcj/news/3010878/gic-advises-caution-predicts-rising-global-volatility
linkPattern = "www.pintu360.com/a\d+.html"
Nocontents = [
]
columns = [
    {"column": "innovation", "max": 1, 'sourceValue': 'channel_74'},
    {"column": "entrepreneurs", "max": 1, 'sourceValue': 'channel_4'},
    {"column": "small-business", "max": 1, 'sourceValue': 'channel_21'},
    {"column": "investing", "max": 1, 'sourceValue': 'channel_72section_1089'},
    {"column": "crypto-blockchain", "max": 1, 'sourceValue': 'channel_72section_1095'},
    {"column": "fintech", "max": 1, 'sourceValue': 'channel_72section_1096'},
    {"column": "hedge-funds-private-equity", "max": 1, 'sourceValue': 'channel_72section_1094'},
]


class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=10):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

        # 实现

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j_content = json.loads(content)
            except Exception, E:
                logger.info(E)
                return False

            if j_content.has_key("promotedContent") is True:
                return True
        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        if content.find('article-container color-body font-body') >= 0:
            return True
        return False


def has_news_content(content):
    # d = pq(html.fromstring(content.decode("utf-8", "ignore")))
    if content.find('article-body fs-article fs-responsive-text'):
        return True
    return False


def process_news(column, j_content, content, download_crawler):
    if has_news_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        d = pq(html.fromstring(content.decode("utf-8", "ignore")))

        category = None
        categoryNames = []

        key = j_content['id']
        type = TYPE
        title = j_content['title']

        newspost = j_content.get('image')
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(newspost, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None

        tags = []
        brief = j_content['description']
        newsurl = j_content['uri']

        try:
            date = j_content['date']
            post_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(str(date)[:-3])))
            news_time = datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1)
            logger.info("news-time: %s", news_time)
        except Exception, e:
            logger.info(e)
            news_time = datetime.datetime.now()

        article = d('div.article-container').html()
        contents = extract.extractContents(newsurl, article,document=False)

        logger.info("%s, %s, %s, %s -> %s, %s", key, title, news_time, ":".join(tags), category, brief)
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
            if c["type"] == "text":
                if c["data"].find("Share to facebookShare to twitterShare to linkedin") >= 0:
                    c['data'] = c['data'].replace('Share to facebookShare to twitterShare to linkedin', '')
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


def get_proxy(http_type='http'):
    """
    获取可以访问的ip
    """

    proxy = {'type': http_type, 'anonymity': 'high'}
    url = "https://www.forbes.com/innovation/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }
    timeout = 20
    while True:
        logger.info("Start proxy_pool.get_single_proxy")
        proxy_ip = proxy_pool.get_single_proxy(proxy)

        if proxy_ip is None:
            logger.info("proxy_pool.get_single_proxy return None")
            continue
        proxies = {
            'https': proxy_ip['ip:port']
        }
        try:
            r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if r.text.find('Forbes Welcome') >= 0:
                logger.info('ip:%s for forbes' % proxy_ip['ip:port'])
                return proxies
        except Exception, e:
            logger.info('Proxy Exception:%s' % e)

def crawler_news(column, crawler, j_content, download_crawler):
    global Proxies
    retry = 0
    while True:
        try:
            newsurl = j_content['uri']
            content = requests.get(newsurl, proxies=Proxies, timeout=20).text
            if content.find('article-container color-body font-body') >= 0:
                try:
                    process_news(column, j_content, content, download_crawler)
                except Exception, ex:
                    logger.exception(ex)
                    raise ValueError('something wrong at process nrews')
                break
        except Exception,e:
            logger.info('cralwer_news requests error :%s'%e)
            Proxies = get_proxy(http_type='https')
        retry += 1
        if retry > 20:
            break


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)
        crawler_news(column, crawler, URL, download_crawler)


def process(r_content, flag):
    j_content = json.loads(r_content)
    contentPositions = j_content['promotedContent']['contentPositions']
    logger.info("Got %s news", len(contentPositions))
    cnt = 0
    if len(contentPositions) == 0:
        return cnt
    for content in contentPositions:
        try:
            title = content['title']
            link = content['uri']
            mongo = db.connect_mongo()
            collection_news = mongo.article.news
            item = collection_news.find_one({"title": title})
            item2 = collection_news.find_one({"link": link})
            mongo.close()
            if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                URLS.append(content)
        except Exception, ex:
            logger.exception(ex)
            continue
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

        url = "https://www.forbes.com/forbesapi/source/more.json?limit=10&source=stream&sourceType=channelsection&sourceValue=%s&start=1" % \
              column['sourceValue']

        while True:
            result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        # logger.info(URLS)
                        # threads = [gevent.spawn(run_news, column, newscrawler, download_crawler=None) for i in xrange(concurrent_num)]
                        # gevent.joinall(threads)
                        run_news(column, newscrawler, download_crawler=None)
                        # exit()
                except Exception, ex:
                    logger.exception(ex)
                    cnt = 0
                break

@traceback_decorator.try_except
def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    global Proxies
    while True:
        Proxies = get_proxy(http_type='https')
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            time.sleep(60 * 60 * 3)
        else:
            return


if __name__ == '__main__':
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(1, "all")
        # else:
        #     link = param
        #     download_crawler = None
        #     crawler_news({"column":"None"}, NewsCrawler(), link, None, '2018-07-17T05:31:39', download_crawler)
    else:
        start_run(1, "incr")



