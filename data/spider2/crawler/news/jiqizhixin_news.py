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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

# logger
loghelper.init_logger("crawler_jiqizhixin_news", stream=True)
logger = loghelper.get_logger("crawler_jiqizhixin_news")

NEWSSOURCE = "jiqizhixin"

SOURCE = 13831
URLS = []

categoryDict = {
    u'深度': {'category': 60107, 'type': 60003},
    u'思想': {'category': 60107, 'type': 60003},
    u'资源': {'category': 60107, 'type': 60003},
}


class Hotcrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout, use_proxy=1)

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find('class="article-item__container') >= 0:
                return True
            return False
        return False


class Contentcrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout, use_proxy=1)

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find('<div class="article__content" id="js-article-content">') >= 0:
                return True
            return False
        return False


def process(crawler):
    while True:
        if len(URLS) == 0: return
        linkDict = URLS.pop(0)

        retry = 0

        while True:
            retry += 1
            if retry > 6: break
            download_crawler = download.DownloadCrawler(use_proxy=False)
            url = linkDict['href']
            result = crawler.crawl(url)
            if result['get'] == 'success':
                d = pq(html.fromstring(result['content'].decode("utf-8")))

                title = linkDict['title']
                key = url.split('/')[-1]

                category = d('.al-crumbs a:nth-child(2)').text()

                if categoryDict.has_key(category):
                    TYPE = categoryDict[category]['type']
                    category = categoryDict[category]['category']
                else:
                    TYPE = 60001
                    category = None

                brief = linkDict['brief']
                postraw = linkDict['post']

                tags = []
                # for tag in d('.tags').text().split():
                #     if tag.strip() not in tags: tags.append(tag)

                news_time = d('.article__published').eq(0).text()
                # news_time = datetime.datetime.strptime(' '.join(news_time.split(' ')[:2]), '%Y年%m月%d日 %H:%M')
                # news_time = datetime.datetime.strptime(news_time, '%Y/%m/%d %p %I:%M')
                news_time = datetime.datetime.strptime(news_time, '%Y/%m/%d %H:%M')

                flag, domain = url_helper.get_domain(url)
                dnews = {
                    "date": news_time - datetime.timedelta(hours=8),
                    "title": title,
                    "link": url,
                    "createTime": datetime.datetime.now(),
                    "source": SOURCE,
                    "key": key,
                    "key_int": None,
                    "type": TYPE,
                    "original_tags": tags,
                    "processStatus": 0,
                    # "companyId": None,
                    "companyIds": [],
                    "category": category,
                    "domain": domain,
                    "categoryNames": []
                }

                article = d('.article__content').html()
                contents = extract.extractContents(url, article)
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
                    dcontents.append(dc)
                    rank += 1
                dnews["contents"] = dcontents

                if brief is None or brief.strip() == "":
                    brief = util.get_brief_from_news(dcontents)

                # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
                (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key,
                                                                             "news")
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

                # brief=brief[:100]
                dnews["brief"] = brief

                mongo = db.connect_mongo()
                collection_news = mongo.article.news
                # update link content with oldId
                item = collection_news.find_one({"link": url})

                if len(dcontents) > 1:
                    if item is None:
                        # collection_news.insert(dnews)
                        nid = parser_mongo_util.save_mongo_news(dnews)
                        logger.info("Done: %s", nid)
                    else:
                        logger.info("update %s", url)
                        #     oldId = collection_news.find_one({"link": url})['_id']
                        #     collection_news.delete_one({"link": url})
                        #     dnews['_id'] = oldId
                        #     collection_news.insert(dnews)
                mongo.close()
                logger.info("%s, %s, %s, %s, %s, %s, %s", key, title, news_time, category, " ".join(tags), brief, post)
                logger.info("*************DONE*************")
                break


def get_link(crawler, concurrent_num, contentcrawler):
    for page in xrange(5):
        url = 'https://www.jiqizhixin.com/articles?page=%s' % (page + 1)
        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                d = pq(html.fromstring(result['content'].decode("utf-8")))

                for i in d('.news__item'):
                    key = d(i)('.article__title').attr('href').split('articles/')[-1]
                    title = d(i)('.article__title h2').text().strip()
                    post = d(i)('.article__cover').attr('style')
                    post = re.findall('(https?://.+)\?imageView', post)[0]

                    brief = d(i)('.article__info .article__summary').text()

                    # category = item['_category']['name']
                    # date = item['created_at']
                    #
                    # if not isinstance(date, datetime.datetime):
                    #     logger.info('%s not datetime', date)
                    #     date = extract.extracttime(date)

                    href = 'https://www.jiqizhixin.com/articles/%s' % key
                    linkDict = {
                        "href": href,
                        "title": title,
                        "post": post,
                        "brief": brief,
                    }

                    mongo = db.connect_mongo()
                    collection_news = mongo.article.news

                    item = collection_news.find_one({"link": href, 'title': title})
                    if item is None:
                        # logger.info( 'not exists %s ,%s '%(href,title))
                        URLS.append(linkDict)
                    else:
                        logger.info('already exists %s , %s', href, title)
                    mongo.close()

                break

        if len(URLS) == 0:
            logger.info('first page got no fresh news,quiting............')
            break

        threads = [gevent.spawn(process, contentcrawler) for i in
                   xrange(concurrent_num)]
        gevent.joinall(threads)


def get_homepage(crawler, concurrent_num, contentcrawler):
    url = 'https://www.jiqizhixin.com'
    while True:
        result = crawler.crawl(url)
        if result['get'] == 'success':
            d = pq(html.fromstring(result['content'].decode("utf-8")))
            pageLink = []
            for i in d('.article-item__container'):
                href = d(i)('.article-item__title').attr('href')
                if href.find('videos') >= 0: continue
                href = url + href

                if href in pageLink: continue
                pageLink.append(href)

                title = d(i)('.article-item__title').text().strip()

                post = d(i)('.article-item__cover img').attr('src')
                # post = re.findall('url\((https?://.+)\)', post)[0]

                # date=post.replace('.jpg','').split('/')[-1]

                linkDict = {
                    "href": href,
                    "title": title,
                    "post": post,
                    "brief": None,
                }
                # print linkDict


                mongo = db.connect_mongo()
                collection_news = mongo.article.news

                item = collection_news.find_one({"link": href, 'title': title})
                if item is None:
                    logger.info('not exists %s ,%s ' % (href, title))
                    URLS.append(linkDict)
                else:
                    logger.info('already exists %s , %s', href, title)
                mongo.close()

            break

    threads = [gevent.spawn(process, contentcrawler) for i in
               xrange(concurrent_num)]
    gevent.joinall(threads)


def get_hot(crawler, concurrent_num, contentcrawler):
    url = 'http://www.jiqizhixin.com'
    while True:
        result = crawler.crawl(url)
        if result['get'] == 'success':
            d = pq(html.fromstring(result['content'].decode("utf-8")))
            for i in d('.al-index-second-title'):
                href = d(i).parent().attr('href')
                href = url + href
                title = d(i)('h2').text().strip()

                pic = d(i).parent()('.al-replace-img').attr('style')
                post = re.findall('/{1,2}(.+\..{3,4})\)', pic)[0]
                if post.find('jiqizhixin.com') < 0:
                    post = url + '/' + post
                else:
                    post = 'http://' + post

                # date=post.replace('.jpg','').split('/')[-1]

                linkDict = {
                    "href": href,
                    "title": title,
                    "post": post,
                    "brief": None,
                }
                # print linkDict


                mongo = db.connect_mongo()
                collection_news = mongo.article.news

                item = collection_news.find_one({"link": href, 'title': title})
                if item is None:
                    logger.info('not exists %s ,%s ' % (href, title))
                    URLS.append(linkDict)
                else:
                    logger.info('already exists %s , %s', href, title)
                mongo.close()

            break

    threads = [gevent.spawn(process, contentcrawler) for i in
               xrange(concurrent_num)]
    gevent.joinall(threads)


def start_run(concurrent_num, flag):
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        hotcrawler = Hotcrawler()
        contentcrawler = Contentcrawler()
        # download_crawler = download.DownloadCrawler(use_proxy=False)

        # get_hot(hotcrawler, concurrent_num, contentcrawler)
        # get_link(hotcrawler, concurrent_num, contentcrawler)
        get_homepage(hotcrawler, concurrent_num, contentcrawler)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            logger.info('sleeping')
            gevent.sleep(60 * 8)  # 30 minutes
        else:
            return
            # gevent.sleep(86400*3)   #3 days


if __name__ == "__main__":
    start_run(1, 'incr')
