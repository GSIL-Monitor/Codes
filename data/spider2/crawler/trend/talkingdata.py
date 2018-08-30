# -*- coding: utf-8 -*-
import requests
import os, sys
import datetime
from pyquery import PyQuery as pq
from lxml import html
import json
from pymongo import MongoClient
import gevent
from gevent import monkey;

monkey.patch_all()
import math

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, db

# logger
loghelper.init_logger("crawler_talkingdata_trend", stream=True)
logger = loghelper.get_logger("crawler_talkingdata_trend")

reload(sys)
sys.setdefaultencoding("utf-8")


class TalkingdataCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):

        try:
            json.loads(content)
            return True
        except:
            return False


class TalkingdataIdCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)  # todo

    def is_crawl_success(self, url, content):
        if content.find('<div class="app-menu">') == -1:
            return False
        return True


def save(data):
    # print 'saving ',data['subCategoryId'],data['startDate'],data['freqId'],data['ranking']
    mongo = db.connect_mongo()
    collection = mongo.trend.tkdataApp_rank
    collectionMapping = mongo.trend.tkdataApp_mapping
    if collection.find_one({"subCategoryId": data['subCategoryId'],
                            "startDate": data['startDate'],
                            "freqId": data['freqId'],
                            'ranking': data['ranking']}) is not None:
        collection.delete_one({"subCategoryId": data['subCategoryId'],
                               "startDate": data['startDate'],
                               "freqId": data['freqId'],
                               'ranking': data['ranking']})

    # apkname
    # logger.info(data['appId'])
    if data['appId'] is not None:
        mapping = collectionMapping.find_one({'appId': data['appId']})
        if mapping is None:
            apkname = getApkName(data.get('appName'))
            logger.info('app:%s %s|apkName:%s', data['appId'], data.get('appName'), apkname)
            save_mapping(data['appId'], data.get('appName'), apkname)
        else:
            apkname = mapping['apkName']
        data['apkname'] = apkname
    collection.insert_one(data)
    mongo.close()


def process_detail(category, subCategory, startDate, endDate, typeId, dateType, crawler):
    start, cnt = 0, 0
    while True:
        url = 'http://mi.talkingdata.com/rank/coverage.json?date=%s&typeId=%d&rankType=a&dateType=%s&rankingStart=%s' % (
            startDate, typeId, dateType, start)
        logger.info('start get %s' % url)
        start += 100

        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                logger.info('successfully get %s' % url)
                jsons = json.loads(result['content'])
                # print 'totally %d items ' % len(jsons)

                for i in jsons:
                    freqdic = {
                        'w': [1, 'weekly']
                        , 'm': [2, 'monthly']
                        , 'q': [3, 'quarterly']
                    }
                    freqId = freqdic[dateType][0]
                    freqName = freqdic[dateType][1]

                    data = {
                        'category': category,
                        'subCategory': subCategory,
                        'subCategoryId': typeId,
                        'startDate': datetime.datetime.strptime(startDate, '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S"),
                        'endDate': datetime.datetime.strptime(endDate, '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S"),
                        'freqId': freqId,
                        'freqName': freqName,
                    }

                    data.update(i)
                    # print data
                    save(data)
                    # logger.info('saving data of %s' % url)

                logger.info('finished %s with %d new items' % (url, len(jsons)))
                cnt += len(jsons)
                break

        if len(jsons) < 100: break
    return cnt


def run_process(category, subCategory, startDate, endDate, typeId, dateType, crawler, retry=0):
    mongo = db.connect_mongo()
    collection = mongo.trend.tkdataApp_rank
    if collection.find_one(
            {"subCategoryId": typeId,
             "startDate": datetime.datetime.strptime(startDate, '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S"),
             "endDate": datetime.datetime.strptime(endDate, '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S")}) is not None:
        mongo.close()
        logger.info('already exists %s %s %s !!!!' % (typeId, startDate, dateType))
        return 0
    mongo.close()

    cnt = process_detail(category, subCategory, startDate, endDate, typeId, dateType, crawler)

    if cnt == 0 and dateType == 'w' and (
                datetime.datetime.today() - datetime.datetime.strptime(startDate, '%Y-%m-%d')).days <= 30:
        return 999999

    return cnt

    # if cnt == 0 and dateType == 'w' and retry < 6:
    #     logger.info("%s %s has no json", startDate, dateType)
    #     startDate = datetime.datetime.strptime(startDate, '%Y-%m-%d') + datetime.timedelta(days=-7)
    #     endDate = datetime.datetime.strptime(endDate, '%Y-%m-%d') + datetime.timedelta(days=-7)
    #     logger.info("change to %s %s", startDate, dateType)
    #     retry += 1
    #
    #     cnt=run_process(category, subCategory, startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d"), typeId,
    #                    dateType, crawler, retry)
    # elif retry==6 :
    #     return 1
    # else:
    #     return cnt


def run(crawler, flag):
    if len(dicts) == 0: return
    eachtype = dicts.pop(0)
    for eachfreq in ['w', 'm', 'q']:
        # for eachfreq in ['w']:
        startDate = datetime.date.today()

        while True:
            startDate, endDate = get_date(eachfreq, startDate)
            cnt = run_process(eachtype['category'], eachtype['subCategory'], startDate, endDate,
                              eachtype['subCategoryId'],
                              eachfreq, crawler)

            if cnt == 0 or (flag == 'incr' and cnt != 999999):  # 999999 means weekly returns 0 (within 30 days)
                break
            startDate = datetime.datetime.strptime(startDate, '%Y-%m-%d')


def get_date(dateType, today):
    if dateType == 'w':
        startDate = today - datetime.timedelta(days=today.weekday() + 7)
        endDate = today - datetime.timedelta(days=today.weekday() + 1)
    elif dateType == 'm':
        endDate = datetime.date(today.year, today.month, 1) - datetime.timedelta(days=1)
        startDate = datetime.date(endDate.year, endDate.month, 1)
    elif dateType == 'q':
        quarterNum = int(math.ceil(float(today.month) / 3)) - 1
        quarterDic = {1: 1, 2: 4, 3: 7, 0: 10}
        year = today.year if quarterNum > 0 else today.year - 1

        startDate = datetime.date(year, quarterDic[quarterNum], 1)
        endDate = startDate - datetime.timedelta(days=-31 * 3)
        endDate = datetime.date(endDate.year, endDate.month, 1) - datetime.timedelta(days=1)

    return startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d")


def start_run(concurrent_num, flag):
    while True:
        logger.info("Takingdata trend start...")
        # thread = gevent.spawn(run, g, MindstCrawler())

        threads = [gevent.spawn(run, TalkingdataCrawler(), flag) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        if len(dicts) == 0:
            logger.info("Takingdata trend end.")

            gevent.sleep(60 * 60 * 12)  # half day
            global dicts
            dicts = getId()


def getId():
    crawler = TalkingdataIdCrawler()
    url = 'http://mi.talkingdata.com/app-rank.html'
    # res = requests.get(url).text
    while True:
        result = crawler.crawl(url)
        if result['get'] == 'success':
            idDict = []
            d = pq(html.fromstring(result['content']))
            categories = d('.app-menu > ul > li')
            categoryDic = {}

            for eachcategory in categories:
                d1 = pq(eachcategory)
                category = d1('span').text()
                categoryId = int(d1('span').attr('td-data'))
                categoryDic[categoryId] = category

            categories2 = d('.app-menu > ol ')
            print len(categories2)
            for c in categories2:
                d = pq(c)
                categoryId = int(d.attr('td-parent'))
                category = categoryDic[categoryId]

                subCategories = d('li')

                for eachsubCategory in subCategories:
                    d = pq(eachsubCategory)
                    subCategory = d('a').text()
                    subCategoryId = d('a').attr("td-data")

                    dict = {}
                    dict['category'] = category
                    dict['subCategory'] = subCategory
                    dict['subCategoryId'] = int(subCategoryId)
                    for i in dict:
                        print i, dict[i]

                    idDict.append(dict)
            break
    logger.info('totally %d types' % len(idDict))
    return idDict


# mapping
def getApkName(shortName):
    mongo = db.connect_mongo()
    collection = mongo.market.android
    android = collection.find_one({'name': shortName})
    apkname = android['apkname'] if android is not None else None
    mongo.close()
    return apkname


def save_mapping(appId, appName, apkName):
    mongo = db.connect_mongo()
    collection = mongo.trend.tkdataApp_mapping

    if collection.find_one({'appId': appId}) is None:
        logger.info('inserting tkdataApp_mapping appId:%s', appId)
        collection.insert_one({'apkName': apkName,
                               'name': appName,
                               'appId': appId
                               })
    else:
        logger.info('updating tkdataApp_mapping appId:%s', appId)
        collection.update_one({'appId': appId},
                              {'$set': {
                                  'name': appName,
                                  'apkName': apkName}
                              }
                              )
    mongo.close()


def map_old():
    mongo = db.connect_mongo()
    collection_tk = mongo.trend.tkdataApp_rank
    appIds = collection_tk.distinct('appId')
    disAppIds = mongo.trend.tkdataApp_mapping.distinct('appId')
    actualAppIds = [i for i in appIds if i not in disAppIds]
    print len(actualAppIds)

    for ai in actualAppIds:
        logger.info('start process appid:%s', ai)
        an = collection_tk.find_one({'appId': ai}).get('appName', 'unknown')
        apkname = getApkName(an.strip())
        logger.info('app:%s %s|apkName:%s', ai, an, apkname)
        save_mapping(ai, an, apkname)

    mongo.close()


if __name__ == "__main__":
    # dicts = [{'category': u'通讯社交', 'subCategoryId': 2, 'subCategory': u'即时通讯'}]
    # start_run(10, "all")
    # exit()

    dicts = getId()
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(10, "incr")
        elif param == "all":
            start_run(10, "all")
    else:
        start_run(10, "incr")
