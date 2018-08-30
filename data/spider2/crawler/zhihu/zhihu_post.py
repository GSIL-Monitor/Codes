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
import loghelper, extract, db, util, url_helper, extractArticlePublishedDate
import download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import crawler_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

# logger
loghelper.init_logger("crawler_zhihu_post", stream=True)
logger = loghelper.get_logger("crawler_zhihu_post")

SOURCENAME = "zhihu_post"

SOURCE = 13612
TYPE = 60007
URLS = []

mongo = db.connect_mongo()
collectionUser = mongo.zhihu.user
collectionPost = mongo.zhihu.post
collectionNews = mongo.article.news


class Zhihucrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)  # todo

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find(u'你正在使用的浏览器版本过低，将不能正常浏览和使用知乎') >= 0:
                logger.info(content)
                return False
            elif url.find('api') >= 0:
                try:
                    json.loads(content)
                    return True
                except:
                    return False
            else:
                if content.find('id="data"') >= 0:
                    return True
                else:
                    logger.info(content)
                    return False
            return False
        return False


# def processContent(crawler, download_crawler):
#     while True:
#         if len(URLS) == 0: return
#         linkDict = URLS.pop(0)
#
#         while True:
#             url = linkDict['href']
#             result = crawler.crawl(url)
#             if result['get'] == 'success':
#                 d = pq(html.fromstring(result['content'].decode("utf-8")))
#
#                 article = d('.QuestionAnswer-content .RichContent-inner span').html()
#                 contents = extract.extractContents(item['url'], article)
#
#                 dcontents = []
#                 rank = 1
#                 for c in contents:
#
#                     if c["type"] == "text":
#                         dc = {
#                             "rank": rank,
#                             "content": c["data"],
#                             "image": "",
#                             "image_src": "",
#                         }
#                     else:
#                         if download_crawler is None:
#                             dc = {
#                                 "rank": rank,
#                                 "content": "",
#                                 "image": "",
#                                 "image_src": c["data"],
#                             }
#                         else:
#                             imgurl = parser_mysql_util.get_logo_id(c["data"], download_crawler, SOURCE, linkDict['key'],
#                                                                    "news")
#                             if imgurl is not None:
#                                 dc = {
#                                     "rank": rank,
#                                     "content": "",
#                                     "image": str(imgurl),
#                                     "image_src": "",
#                                 }
#                             else:
#                                 continue
#
#                     # logger.info(c["data"])
#                     dcontents.append(dc)
#                     rank += 1
#                 linkDict["contents"] = dcontents
#
#                 save(SOURCE, TYPE, url, key, result['content'])
#                 logger.info('saving %s %s %s %s\n%s', SOURCE, TYPE, url, key, '#' * 166)
#
#                 break


def process(result, code, flag, download_crawler):
    d = pq(html.fromstring(result['content'].decode("utf-8")))

    data = d('#data').attr('data-state')
    j = json.loads(data)
    # print data
    # exit()

    posts = j['entities']['articles']
    for key, a in posts.items():
        # url = 'https://www.zhihu.com/question/%s/answer/%s' % (a['question']['id'], a['id'])
        url = a['url']

        title = a['title']
        if title is None or title == '':
            logger.info('%s has no title,continue', url)
            continue

        def mongo_detect(collection):
            item = collection.find_one({"link": url})
            if item is None:
                logger.info('%s not exists %s|%s', collection.name, a['id'], a['title'])
                return 1
            else:
                if time.mktime(item['updatedTime'].timetuple()) != a['updated'] or flag == 'all':
                    logger.info('%s new update %s|%s', collection.name, a['id'], a['title'])
                    return 2
                else:
                    logger.info('%s no update %s|%s', collection.name, a['id'], a['title'])
                    return 0

        if mongo_detect(collectionPost) == 0 and mongo_detect(collectionNews) == 0: continue

        flag, domain = url_helper.get_domain(url)
        answerDict = {
            "link": url,
            "title": a['title'],
            "date": datetime.datetime.fromtimestamp(a['created']) - datetime.timedelta(hours=8),
            "author_code": code,
            "author": a['author']['name'],
            # "brief": a['excerpt'],
            "source": SOURCE,
            "type": TYPE,
            "key": str(a['id']),
            "key_int": int(a['id']),
            "vote_up": int(a['voteupCount']),
            "updatedTime": datetime.datetime.fromtimestamp(a['updated']),
            "createdTime": datetime.datetime.fromtimestamp(a['created']),
            "detectTime": datetime.datetime.now(),
            "processStatus": 0,
            "domain": domain,
        }

        # content
        article = a['content']
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
                    (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler, SOURCE,
                                                                                a['id'], "news")
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
        answerDict["contents"] = dcontents

        brief = util.get_brief_from_news(dcontents)
        answerDict["brief"] = brief

        postraw = a['imageUrl']

        (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key,
                                                                     "news")
        if posturl is not None:
            post = str(posturl)
        else:
            post = None
        if post is None or post.strip() == "":
            post = util.get_posterId_from_news(dcontents)

        if download_crawler is None:
            answerDict["post"] = post
        else:
            answerDict["postId"] = post

        if code == 'xi-niu-shu-ju':
            answerDict['source'] = 13613
            answerDict['domain'] = 'xiniudata.com'

        def mongo_save(collection):
            logger.info('using db:%s', collection.name)
            item = collection.find_one({"link": url})
            if item is None:
                logger.info('insert %s|%s', a['id'], a['title'])
                answerDict["createTime"] = datetime.datetime.now()
                answerDict["imgChecked"] = True
                value = parser_mongo_util.get_simhash_value(answerDict.get("contents", []))
                answerDict["simhashValue"] = value
                collection.insert_one(answerDict)
            else:
                if time.mktime(item['updatedTime'].timetuple()) != a['updated'] or flag == 'all':
                    logger.info('new update %s|%s', a['id'], a['title'])
                    collection.update_one({"link": url}, {'$set': {'contents': dcontents,
                                                                   "updatedTime": datetime.datetime.fromtimestamp(
                                                                       a['updated']),
                                                                   "detectTime": datetime.datetime.now()}})
                else:
                    logger.info('no update %s|%s', a['id'], a['title'])
                    collection.update_one({"link": url},
                                          {'$set': {"detectTime": datetime.datetime.now()}})

        mongo_save(collectionPost)
        mongo_save(collectionNews)

        logger.info('processed %s|%s \n', a['id'], a['title'])


def run(crawler, concurrent_num, codes, flag, download_crawler):
    for code in codes:
        userType = collectionUser.find_one({'code': code})['userType']
        if userType == 'people':
            url = 'https://www.zhihu.com/people/%s/pins/posts' % code
        elif userType == 'organization':
            url = 'https://www.zhihu.com/org/%s/posts' % code
        else:
            logger.info('new userType:%s', userType)
            exit()

        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                process(result, code, flag, download_crawler)

                break

                # threads = [gevent.spawn(process, crawler) for i in
                #            xrange(concurrent_num)]
                # gevent.joinall(threads)


def start_run(concurrent_num, codes, flag):
    download_crawler = None
    download_crawler = download.DownloadCrawler(use_proxy=1)

    if len(codes) == 0:
        codesMongo = list(collectionUser.find())
        codes = [i['code'] for i in codesMongo]

    while True:
        logger.info("%s  start...", SOURCENAME)

        zhihucrawler = Zhihucrawler()
        # download_crawler = download.DownloadCrawler(use_proxy=False)

        run(zhihucrawler, concurrent_num, codes, flag, download_crawler)

        logger.info("%s end.", SOURCENAME)

        # return

        if flag == "incr":
            logger.info('sleeping')
            gevent.sleep(60 * 60)  # 30 minutes
        else:
            return
            # gevent.sleep(86400*3)   #3 days


def process_xiniu(result, code, flag, download_crawler):
    j = json.loads(result['content'])
    posts = j['data']
    code = 'xi-niu-shu-ju'

    for a in posts:
        # url = 'https://www.zhihu.com/question/%s/answer/%s' % (a['question']['id'], a['id'])
        url = a['url']
        key = a['id']

        title = a['title']
        if title is None or title == '':
            logger.info('%s has no title,continue', url)
            continue

        def mongo_detect(collection):
            item = collection.find_one({"link": url})
            if item is None:
                logger.info('%s not exists %s|%s', collection.name, a['id'], a['title'])
                return 1
            else:
                if time.mktime(item['updatedTime'].timetuple()) != a['updated'] or flag == 'all':
                    logger.info('%s new update %s|%s', collection.name, a['id'], a['title'])
                    return 2
                else:
                    logger.info('%s no update %s|%s', collection.name, a['id'], a['title'])
                    return 0

        if mongo_detect(collectionPost) == 0 and mongo_detect(collectionNews) == 0: continue

        flag, domain = url_helper.get_domain(url)
        answerDict = {
            "link": url,
            "title": a['title'],
            "date": datetime.datetime.fromtimestamp(a['created']) - datetime.timedelta(hours=8),
            "author_code": code,
            "author": a['author']['name'],
            # "brief": a['excerpt'],
            "source": SOURCE,
            "type": TYPE,
            "key": str(a['id']),
            "key_int": int(a['id']),
            "vote_up": int(a['voteup_count']),
            "updatedTime": datetime.datetime.fromtimestamp(a['updated']),
            "createdTime": datetime.datetime.fromtimestamp(a['created']),
            "detectTime": datetime.datetime.now(),
            "processStatus": 0,
            "domain": domain,
        }

        # content
        article = a['content']
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
                    (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler, SOURCE,
                                                                                a['id'], "news")
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
        answerDict["contents"] = dcontents

        brief = util.get_brief_from_news(dcontents)
        answerDict["brief"] = brief

        postraw = a['image_url']
        if download_crawler is not None:
            posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
            if posturl is not None:
                post = str(posturl)
            else:
                post = None
        else:
            post = None
        if post is None or post.strip() == "":
            post = util.get_posterId_from_news(dcontents)

        if download_crawler is None:
            answerDict["post"] = post
        else:
            answerDict["postId"] = post

        if code == 'xi-niu-shu-ju':
            answerDict['source'] = 13613
            answerDict['domain'] = 'xiniudata.com'

        def mongo_save(collection):
            logger.info('using db:%s', collection.name)
            item = collection.find_one({"link": url})
            if item is None:
                logger.info('insert %s|%s', a['id'], a['title'])
                answerDict["createTime"] = datetime.datetime.now()
                answerDict["imgChecked"] = True
                value = parser_mongo_util.get_simhash_value(answerDict.get("contents", []))
                answerDict["simhashValue"] = value
                collection.insert_one(answerDict)
            else:
                if time.mktime(item['updatedTime'].timetuple()) != a['updated'] or flag == 'all':
                    logger.info('new update %s|%s', a['id'], a['title'])
                    collection.update_one({"link": url}, {'$set': {'contents': dcontents,
                                                                   "updatedTime": datetime.datetime.fromtimestamp(
                                                                       a['updated']),
                                                                   "detectTime": datetime.datetime.now()}})
                else:
                    logger.info('no update %s|%s', a['id'], a['title'])
                    collection.update_one({"link": url},
                                          {'$set': {"detectTime": datetime.datetime.now()}})

        mongo_save(collectionPost)
        mongo_save(collectionNews)

        logger.info('processed %s|%s \n', a['id'], a['title'])


def run_xiniu(crawler=Zhihucrawler()):
    url = 'https://www.zhihu.com/api/v4/members/xi-niu-shu-ju/articles?include=data%5B*%5D.comment_count%2Ccan_comment%2Ccomment_permission%2Ccontent%2Cvoteup_count%2Ccreated%2Cupdated%2Cupvoted_followees%2Cvoting%2Creview_info%3Bdata%5B*%5D.author.badge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20&sort_by=created'
    data = {'authorization': "oauth c3cef7c66a1843f8b3a9e6a1e3160e20"}

    while True:
        result = crawler.crawl(url, headers=data, agent=True)
        if result['get'] == 'success':
            process_xiniu(result, code='xi-niu-shu-ju', flag='incr',
                          download_crawler=download.DownloadCrawler(use_proxy=1))
            break


if __name__ == "__main__":
    default_num = 1
    # codes = ['xi-niu-shu-ju', 'cheng-yi-nan', 'nishu-think']
    codes = ['xi-niu-shu-ju', 'cheng-yi-nan', 'nishu-think', 'zhouyuan', 'imike', 'zhangleo', 'amuro1230', 'ourdearamy',
             'keso', 'fenng', 'patrickluo', 'hecaitou', 'ccat', 'xu-xiao-ping-87', 'xie-man-zi', 'neil-shen', 'charlie',
             'ji-yue', 'shao-yi-bo', 'davidsu', 'benye', 'xiaohong-chen', 'lina', 'cai-wen-sheng',
             'kaifulee', 'imike', 'li-feng', 'gao-xiang', 'zheng-lan', 'stevenhubin', 'billhan', 'lili', 'Joeydai',
             'larapan', 'wu-wen-wei', 'allen-zhu', 'huangdoc', 'wangyi', 'zhang-kai-feng', 'summy',
             'chang-bin', 'yu-yi-duo', 'liuyiang', 'marui', 'feng-hua-wei', 'zhutianyu', 'xu-chen', 'dong',
             'wayneshiong', 'huang-sheng-li', 'tong-shi-hao-hans', 'zhang-zhi-yong', 'zhou-kui']
    # codes = ['zhouyuan']
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == 'all':
            start_run(default_num, codes, 'all')
        if param == 'xiniu':
            run_xiniu()
        else:
            start_run(default_num, [param], 'incr')
    else:
        start_run(default_num, codes, 'incr')
