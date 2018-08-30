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
loghelper.init_logger("crawler_leiphone_news", stream=True)
logger = loghelper.get_logger("crawler_leiphone_news")

NEWSSOURCE = "leiphone"

SOURCE = 13833
URLS = []


# categoryDict = {
#     u'深度': {'category': None, 'type': 60003},
#     u'思想': {'category': None, 'type': 60003},
#     u'资源': {'category': None, 'type': 60003},
# }


class Indexcrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout,use_proxy=1)
        # self.use_proxy = False  # TODO

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find('https:\/\/www.leiphone.com\/news\/') >= 0:
                return True
            else:
                print content
            return False
        return False


class Contentcrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)
        # self.use_proxy = False  # TODO

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find('<div class="lph-article-comView">') >= 0:
                return True
            return False
        return False


def process(crawler, outlink=None):
    while True:
        if outlink is None:
            if len(URLS) == 0: return
            linkDict = URLS.pop(0)
        else:
            linkDict = {
                "href": outlink,
                "post": None,
                "title": None
            }

        retries = 0
        while True:
            if retries > 10: break
            retries += 1
            download_crawler = download.DownloadCrawler(use_proxy=False)

            url = linkDict['href']
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                d = pq(html.fromstring(result['content'].decode("utf-8", 'ignore')))

                title = linkDict['title']
                if title is None:
                    title = d('h1.headTit').text().strip()
                key = url.split('/')[-1].split('.')[0]

                # category = d('.al-crumbs a:nth-child(2)').text()
                #
                # if categoryDict.has_key(category):
                #     type = categoryDict[category]['type']
                #     category = categoryDict[category]['category']
                # else:
                #     type = 60001
                #     category = None

                brief = d('.article-lead').text().replace('导语：', '')
                postraw = linkDict['post']

                tags = []
                for tag in d('.related-link a'):
                    t = tag.text.strip()
                    if t not in tags: tags.append(t)

                news_time = d('.inner .time').text()
                news_time = datetime.datetime.strptime(news_time, '%Y-%m-%d %H:%M')

                flag, domain = url_helper.get_domain(url)

                try:
                    key_int = int(key)
                except:
                    key_int = None
                category = None

                dnews = {
                    "date": news_time - datetime.timedelta(hours=8),
                    "title": title,
                    "link": url,
                    "createTime": datetime.datetime.now(),
                    "source": SOURCE,
                    "key": key,
                    "key_int": key_int,
                    "type": 60001,
                    "original_tags": tags,
                    "processStatus": 0,
                    # "companyId": None,
                    "companyIds": [],
                    "category": category,
                    "domain": domain,
                    "categoryNames": []
                }

                article = d('.lph-article-comView').html()
                contents = extract.extractContents(url, article)
                dcontents = []
                rank = 1
                for c in contents:
                    if c["type"] == "text":
                        if c["data"].find("未经授权禁止转载。详情见转载须知。") > 0: continue
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
                            (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler,
                                                                                        SOURCE, key, "news")
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
                dnews["brief"] = brief

                mongo = db.connect_mongo()
                collection_news = mongo.article.news
                # update link content with oldId
                item = collection_news.find_one({"link": url})
                if item is None:
                    nid = parser_mongo_util.save_mongo_news(dnews)
                    logger.info("Done: %s", nid)
                else:
                    logger.info("update %s", url)
                    # oldId = collection_news.find_one({"link": url})['_id']
                    # collection_news.delete_one({"link": url})
                    # dnews['_id'] = oldId
                    # collection_news.insert(dnews)
                mongo.close()
                logger.info("%s, %s, %s, %s, %s, %s, %s", key, title, news_time, category, " ".join(tags), brief, post)
                # logger.info("*************DONE*************")
                break
        if outlink is not None:
            break


def get_link(crawler, concurrent_num, contentcrawler):
    for page in xrange(10):
        url = 'http://www.leiphone.com/site/AjaxLoad/page/%s' % (page + 1)
        url = 'https://www.leiphone.com/site/AjaxLoad/page/%s' % (page + 1)
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                content = result['content'].decode('unicode_escape')  # .replace(' ','')
                d = pq(html.fromstring(content))

                for item in d('img.lazy'):
                    post = d(item).attr('data-original').replace('\\', '')
                    href = d(item.getparent()).attr('href').replace('\\', '')  # .replace('"','')
                    title = d(item).attr('title')  # .decode("unicode_escape")[1:][:-1]
                    # print href, title,post

                    linkDict = {
                        "href": href,
                        "title": title,
                        "post": post,
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
            logger.info('page %s got no fresh news,quiting............', page + 1)
            break

        threads = [gevent.spawn(process, contentcrawler) for i in
                   xrange(concurrent_num)]
        gevent.joinall(threads)


def start_run(concurrent_num, flag):
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        indexcrawler = Indexcrawler()
        contentcrawler = Contentcrawler()
        # download_crawler = download.DownloadCrawler(use_proxy=False)


        get_link(indexcrawler, concurrent_num, contentcrawler)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            logger.info('sleeping')
            gevent.sleep(60 * 8)  # 30 minutes
        else:
            return
            # gevent.sleep(86400*3)   #3 days

def trans_link():
    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    items = list(collection_news.find({"source": SOURCE}))
    for i in items:
        link = i['link'].replace('http:','https:')
        id = i['_id']
        print i['link']
        collection_news.update_one({'_id':id},{'$set':{'link':link}})



if __name__ == "__main__":
    # trans_link()
    start_run(1, 'incr')

    # URLS = [{
    #             'post': 'http://static.leiphone.com/uploads/new/article/pic/201701/586debbdc5c52.png?imageMogr2/thumbnail/!480x290r/gravity/Center/crop/480x290/quality/90',
    #             'href': 'http://www.leiphone.com/news/201701/Gc1cOK7JbVtqW6wI.html',
    #             'title': u'牵手英特尔、公布架构路线图，2017年的地平线要先“赚它一个亿”'}]
    # process(Contentcrawler())
