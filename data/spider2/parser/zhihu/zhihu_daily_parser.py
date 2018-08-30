# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
import traceback
from pymongo import MongoClient
import pymongo
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import config
import db
import extract, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util
import util, url_helper

# logger
loghelper.init_logger("zhihu_daily_parser", stream=True)
logger = loghelper.get_logger("zhihu_daily_parser")

# mongo
mongo = db.connect_mongo()
collection = mongo.zhihu.raw
collectionDaily = mongo.zhihu.daily
collectionNews = mongo.article.news

SOURCE = 13610
TYPE = 60005


def save(dic):
    def mongo_save(collection):
        if collection.find_one({'link': dic['link']}) is None:
            logger.info('%s not exists %s', collection.name, dic['link'])
            dic["imgChecked"] = True
            value = parser_mongo_util.get_simhash_value(dic.get("contents", []))
            dic["simhashValue"] = value
            collection.insert_one(dic)
            return 1
        else:
            logger.info('%s already exists %s', collection.name, dic['link'])
            return 0

    save1 = mongo_save(collectionDaily)
    save2 = mongo_save(collectionNews)
    if save1 == 0 and save2 == 0: exit()


def parse(item, download_crawler):
    if item == None:
        return
    logger.info('processing %s', item['url'])

    def mongo_detect(collection):
        if collection.find_one({'link': item['url']}) is not None:
            logger.info('%s already got %s, skip', collection.name, item['url'])
            return 0
        else:
            return 1

    if mongo_detect(collectionDaily) == 0 and mongo_detect(collectionNews) == 0:
        collection.update({"_id": item["_id"]}, {"$set": {"parsed": True}})
        return

    d = pq(html.fromstring(item['content'].decode("utf-8")))
    title = d('.headline-title').text()
    if title.find(u'这里是广告') >= 0 or title.find(u'如何正确地吐槽') >= 0 or title.find(u'广告·') >= 0:
        collection.update({"_id": item["_id"]}, {"$set": {"parsed": True}})
        logger.info('%s is ad,continue', item['url'])
        return

    originalLink = d('.view-more a').attr('href')
    if originalLink:
        type = 2 if originalLink.find('zhuanlan') >= 0  else 1
    else:
        type = 3

    author = d('.author').text().replace('，', '')
    authorBrief = d('.bio').text()
    questionTitle = d('.question-title').text()

    img = d('.img-wrap img').attr('src')
    # posturl = parser_mysql_util.get_logo_id(img, download_crawler, SOURCE, item['key'], "news")
    (posturl, width, height) = parser_mysql_util.get_logo_id_new(img, download_crawler, SOURCE, item['key'], "news")
    if posturl is not None:
        post = str(posturl)
    else:
        post = None

    # flag, domain = url_helper.get_domain(item['url'])

    result = {
        "dailyType": type,
        "link": item['url'],
        "createTime": datetime.datetime.now(),
        "date": datetime.datetime.now() - datetime.timedelta(hours=8),
        "title": title,
        "questionTitle": questionTitle,
        "originalLink": originalLink,
        "author": author,
        "authorBrief": authorBrief,
        "processStatus": 0,
        "source": SOURCE,
        "type": TYPE,
        "key": item['key'],
        "key_int": int(item['key']),
        "postId": post,
        "domain": "daily.zhihu.com",
    }

    # contents
    article = d('.answer  .meta+.content').html()
    contents = extract.extractContents(item['url'], article)

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
                                                                            item['key'], "news")
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
    result["contents"] = dcontents

    brief = util.get_brief_from_news(dcontents)
    result["brief"] = brief

    save(result)
    collection.update({"_id": item["_id"]}, {"$set": {"parsed": True}})
    logger.info('parsed %s', item['url'])


def start_run():
    download_crawler = download.DownloadCrawler(use_proxy=False)

    while True:
        logger.info("Begin...")
        items = list(collection.find({"source": SOURCE, "parsed": {"$ne": True}}).limit(100))
        for item in items:
            parse(item, download_crawler)
            # break
        logger.info("End.")
        # break
        if len(items) == 0:
            time.sleep(60)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        param = sys.argv[1]
        key = param

        item = collection.find_one({"source": SOURCE, 'key_int': int(key)})
        parse(item, download.DownloadCrawler(use_proxy=False))
    else:
        start_run()
