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
loghelper.init_logger("crawler_zhihu_answer", stream=True)
logger = loghelper.get_logger("crawler_zhihu_answer")

SOURCENAME = "zhihu_answer"

SOURCE = 13611
TYPE = 60007
URLS = []

mongo = db.connect_mongo()
collectionUser = mongo.zhihu.user
collectionAnswer = mongo.zhihu.answer
collectionNews = mongo.article.news


class Zhihucrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)  # todo

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find(u'你正在使用的浏览器版本过低，将不能正常浏览和使用知乎') >= 0:
                logger.info(content)
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
#                             (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler,
#                                                                                         SOURCE, linkDict['key'], "news")
#
#                             if imgurl is not None:
#                                 dc = {
#                                     "rank": rank,
#                                     "content": "",
#                                     "image": str(imgurl),
#                                     "image_src": "",
#                                     "height": int(height),
#                                     "width": int(width)
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

    # user baseinfo
    user = j['entities']['users'][code]

    # if download_crawler is not None:
    #     post = parser_mysql_util.get_logo_id(user['avatarUrl'], download_crawler, SOURCE, code, "user")
    # else:
    #     post = user['avatarUrl']
    post = user['avatarUrl']

    try:
        location = user['locations'][0]['name']
    except:
        location = None

    if user['userType'] == 'people':
        business = user.get('business')
        if business: business = business.get('name')
    else:
        business = user['industryCategory']

    userDic = {
        "name": user['name'],
        "code": code,
        "brief": user['headline'],
        "avatarUrl": post,
        "location": location,
        "business": business,
        "following": user['followingCount'],
        "follower": user['followerCount'],
        "favoriteCount": user['favoriteCount'],
        "favoritedCount": user['favoritedCount'],
        "thankedCount": user['thankedCount'],
        "voteupCount": user['voteupCount'],
        "gender": user['gender'],
        "userType": user['userType'],
        "modifyTime": datetime.datetime.now()
    }

    if collectionUser.find_one({"code": code}) is None:
        collectionUser.insert_one({"code": code, "createTime": datetime.datetime.now()})

    result = collectionUser.update_one({"code": code}, {'$set': userDic})

    if result.matched_count != 1:
        logger.info('code:%s found not 1 item', code)
        exit()

    answers = j['entities']['answers']
    for key, a in answers.items():
        url = 'https://www.zhihu.com/question/%s/answer/%s' % (a['question']['id'], a['id'])

        def mongo_detect(collection):
            item = collection.find_one({"link": url})
            if item is None:
                logger.info('%s not exists %s|%s', collection.name, a['id'], a['question']['title'])
                return 1
            else:
                if time.mktime(item['updatedTime'].timetuple()) != a['updatedTime'] or flag == 'all':
                    logger.info('%s new update %s|%s', collection.name, a['id'], a['question']['title'])
                    return 2
                else:
                    logger.info('%s no update %s|%s', collection.name, a['id'], a['question']['title'])
                    return 0

        if mongo_detect(collectionAnswer) == 0 and mongo_detect(collectionNews) == 0: continue

        flag, domain = url_helper.get_domain(url)
        answerDict = {
            "link": url,
            "questionTitle": a['question']['title'],
            "title": a['question']['title'],
            "date": datetime.datetime.fromtimestamp(a['updatedTime']) - datetime.timedelta(hours=8),
            "author_code": code,
            "author": user['name'],
            # "brief": a['excerpt'],
            "source": SOURCE,
            "type": TYPE,
            "key": str(a['id']),
            "key_int": int(a['id']),
            "question_key": str(a['question']['id']),
            "question_key_int": int(a['question']['id']),
            "vote_up": int(a['voteupCount']),
            "updatedTime": datetime.datetime.fromtimestamp(a['updatedTime']),
            "createdTime": datetime.datetime.fromtimestamp(a['createdTime']),
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
                    key = a['id']
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
        answerDict["contents"] = dcontents

        brief = util.get_brief_from_news(dcontents)
        answerDict["brief"] = brief

        def mongo_save(collection):
            logger.info('using db:%s', collection.name)
            item = collection.find_one({"link": url})
            if item is None:
                logger.info('insert %s|%s', a['id'], a['question']['title'])
                answerDict["createTime"] = datetime.datetime.now()
                answerDict["imgChecked"] = True
                value = parser_mongo_util.get_simhash_value(answerDict.get("contents", []))
                answerDict["simhashValue"] = value
                collection.insert_one(answerDict)
            else:
                if time.mktime(item['updatedTime'].timetuple()) != a['updatedTime'] or flag == 'all':
                    logger.info('new update %s|%s', a['id'], a['question']['title'])
                    collection.update_one({"link": url}, {'$set': {'contents': dcontents,
                                                                   "updatedTime": datetime.datetime.fromtimestamp(
                                                                       a['updatedTime']),
                                                                   "detectTime": datetime.datetime.now()}})
                else:
                    logger.info('no update %s|%s', a['id'], a['question']['title'])
                    collection.update_one({"link": url},
                                          {'$set': {"detectTime": datetime.datetime.now()}})

        mongo_save(collectionAnswer)
        mongo_save(collectionNews)

        logger.info('processed %s|%s \n', a['id'], a['question']['title'])


def run(crawler, concurrent_num, codes, flag, download_crawler):
    for code in codes:
        url = 'https://www.zhihu.com/people/%s/answers' % code

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
    # codes=['alexjiang','keso'] #'alexjiang' return fake user data
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == 'all':
            start_run(default_num, codes, 'all')
        else:
            start_run(default_num, [param], 'incr')
    else:
        start_run(default_num, codes, 'incr')
