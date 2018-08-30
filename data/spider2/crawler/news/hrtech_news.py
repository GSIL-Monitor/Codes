# -*- coding: utf-8 -*-
import os, sys, datetime, re, json
from lxml import html
from pyquery import PyQuery as pq
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, extract, db, util, url_helper, download, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util


# logger
loghelper.init_logger("crawler_hrtech_news", stream=True)
logger = loghelper.get_logger("crawler_hrtech_news")

NEWSSOURCE = "hrtech"
RETRY = 3
TYPE = 60001
SOURCE = 13844
URLS = []
links = []
CURRENT_PAGE = 1
Nocontents = [
]
columns = [
    {"column": "capital", "max": 2},
    {"column": "news", "max": 2},
]


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy = 1)

        # 实现
        # def is_crawl_success(self,url,content):
        #
        #     d = pq(html.fromstring(content.decode("utf-8")))
        #     title = d('head> title').text().strip()
        #     logger.info("title: %s url: %s", title, url)
        #     if title.find("hrtech") >= 0:
        #         return True
        #     if content.find("您没有权限预览该文章") >= 0:
        #         return True
        #     return False


def has_news_content(content):
    d = pq(html.fromstring(content.decode("utf-8", "ignore")))
    title = d('head> title').text().strip()
    temp = title.split("|")
    if len(temp) < 2:
        return False
    if temp[1].strip() == "":
        return False
    return True


def process_news(column, newsurl, content, newspost, download_crawler):
    logger.info('starting process_news %s', newsurl)
    # if has_news_content(content):
    if 1:
        download_crawler = download.DownloadCrawler(use_proxy=False)
        d = pq(html.fromstring(content.decode("utf-8", "ignore")))

        key = newsurl.split("/")[-1].replace('.html','')

        type = TYPE

        category = None

        # title = d('h1.entry-title').text().strip()
        title = d('div.news_detail_title> h2').text().strip()

        tags = []
        # articletags = d(".post-tags a")
        # if articletags is not None:
        #     for t in articletags:
        #         tag = d(t).text()#.split()
        #         if tag is not None and tag.strip() != "" and tag not in tags and tag != title:
        #             tags.append(tag.strip())

        # post = d('div#post_thumbnail> img').attr("src")
        # postraw = d(".content_box img").attr("src")
        postraw = newspost
        # if post is not None:
        #     post = "http://hrtech.com"+ post

        # brief = d("div.wcontent> p.wsub").text()
        brief = ''

        # news_time = extractArticlePublishedDate.extractArticlePublishedDate(newsurl, content)
        # news_time = None
        try:
            news_time = datetime.datetime.strptime(d("div.news_detail_author> span").eq(0).text(), '%Y年%m月%d日')
            dt = datetime.date.today()
            today = datetime.datetime(dt.year, dt.month, dt.day)
            if news_time is None or news_time == today:
                news_time = datetime.datetime.now()
        except:
            news_time = datetime.datetime.now()

        article = d('div.news_detail_con').html()
        contents = extract.extractContents(newsurl, article)

        logger.info("%s, %s, %s, %s -> %s, %s. %s", key, title, news_time, ":".join(tags), category, brief, postraw)
        # exit()
        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        if collection_news.find_one({"title": title}) is not None:
            mongo.close()
            logger.info('title:%s already exists' % title)
            return

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
            # "companyId": None,
            "companyIds": [],
            "category": category,
            "domain": domain,
            "categoryNames": []
        }
        dcontents = []
        rank = 1
        for c in contents:

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
                    (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler, SOURCE, key, "news")
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

            logger.info(c["data"])
            dcontents.append(dc)
            rank += 1
        dnews["contents"] = dcontents
        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        dnews["brief"] = brief

        # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
        (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None
        if post is None or post.strip() == "":
            post = util.get_posterId_from_news(dcontents)

        if download_crawler is None:
            dnews["post"] = post
        else:
            dnews["postId"] = post

        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)

        # update link content with oldId
        item = collection_news.find_one({"link": newsurl})
        if item is None:
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s", nid)
            pass
        else:
            logger.info("update %s", newsurl)
            # collection_news.update_many({'link': newsurl},{'$set': dnews})

            # oldId = collection_news.find_one({"link": newsurl})['_id']
            # collection_news.delete_one({"link": newsurl})
            # dnews['_id']=oldId
            # collection_news.insert(dnews)
        mongo.close()
        # logger.info("*************DONE*************")

    return


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL["post"], download_crawler)

        time.sleep(10)

def crawler_news(column, crawler, newsurl, newspost, download_crawler):
    headers = {"Cookie": "PHPSESSID=isgucca3h1it0ap4tkkhbt9963"}
    while True:
        result = crawler.crawl(newsurl, agent=True, headers=headers)
        if result['get'] == 'success':
            # logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'], newspost, download_crawler)
            except Exception, ex:
                logger.exception(ex)
            break


def process(content, flag):
    # j = json.loads(content)
    # logger.info(content)
    d = pq(html.fromstring(content.decode("utf-8","ignore")))
    htmls = d('ul.news_con> li')
    # htmls=[i for i in htmls if i.attr('href').find('/Xfeature/view?aid=')>=0]

    cnt = 0
    # if len(htmls) == 0 or htmls.find("div") == -1:
    #     return cnt
    for a in htmls:
        try:
            link = d(a)('div.tag-text-con> a').attr("href").strip()
            title = d(a)('div.tag-text-con> a').text().strip()
            post = d(a)('div.news_img_con> img').attr("src").strip()

            # logger.info(link)
            # if re.search(linkPattern, link) and title!='':
            if title != '':
                link = "http://www.hrtechchina.com" + link
                logger.info("Link: %s is right news link", link)

                # check mongo data if link is existed and title is the same
                mongo = db.connect_mongo()
                collection_news = mongo.article.news
                item = collection_news.find_one({"link": link, "title": title})
                item2 = collection_news.find_one({"title": title})
                mongo.close()

                if ((item is None and item2 is None) or flag == "all") and link not in links:
                    # if link not in links:
                    linkmap = {
                        "link": link,
                        "post": post
                    }
                    URLS.append(linkmap)
                    links.append(link)
            else:
                # logger.info(link)
                pass
        except:
            logger.info("cannot get link")
    return len(URLS)


def run(flag, column, newscrawler, concurrent_num, download_crawler):
    global CURRENT_PAGE
    cnt = 1
    while True:
        # key = (CURRENT_PAGE-1) * 15
        key = CURRENT_PAGE

        if flag == "all":
            if key > column["max"]:
                return
        else:
            # if cnt == 0 or key > column["max"]:
            if key > column["max"]:
                return

        CURRENT_PAGE += 1
        # if key == 0:
        #     key = "aa"
        if key == 1:
            url = "http://www.hrtechchina.com/category/%s" % column["column"]
        else:
            url = 'http://www.hrtechchina.com/category/%s/p/%s.html' % (column["column"],key)

        while True:
            result = newscrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)

                        # threads = [gevent.spawn(run_news, column, newscrawler, download_crawler) for i in
                        #            xrange(concurrent_num)]
                        # gevent.joinall(threads)
                        run_news(column, newscrawler, download_crawler)
                        # exit()
                except Exception, ex:
                    logger.exception(ex)
                    cnt = 0
                break


def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        newscrawler = NewsCrawler()

        download_crawler = download.DownloadCrawler(use_proxy=False)
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, newscrawler, concurrent_num, download_crawler)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            time.sleep(60 * 360)  # 30 minutes
        else:
            return
            # gevent.sleep(86400*3)   #3 days


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(3, "incr")
        elif param == "all":
            start_run(3, "all")
        else:
            link = param
            download_crawler = download.DownloadCrawler(use_proxy=False)
            crawler_news({}, NewsCrawler(), link, None, download_crawler)
    else:
        start_run(3, "incr")

        # crawler_news({"column": None, "max": 3}, NewsCrawler(), 'http://hrtech.com/Xfeature/view?aid=1603', None, download.DownloadCrawler(use_proxy=False))
