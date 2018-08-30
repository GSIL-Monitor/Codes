# -*- coding: utf-8 -*-
import os, sys, datetime
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import pymongo
import website

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import util
import loghelper
import url_helper
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../screenshot'))
import screenshot_website


#logger
loghelper.init_logger("website_check", stream=True)
logger = loghelper.get_logger("website_check")

screenshot_crawler = screenshot_website.phantomjsScreenshot()
URLS = []
SCREENURLS = []

def screenshot_test(url,id):
    dest = "jpeg/"
    screenshot_crawler.run(url, id, dest, timeout=30)
    return id

def screenshot(url):
    dest = "jpeg/"
    mongo = db.connect_mongo()
    collection_website = mongo.info.website
    website = collection_website.find_one({"url": url})
    flag = True
    if website is not None:
        dt = datetime.datetime.today()
        month_first = datetime.datetime(dt.year, dt.month, 1)
        if website.has_key("screenshotIds") and len(website["screenshotIds"]) > 0:
            for sc in website["screenshotIds"]:
                if sc["screenshotDate"] == month_first:
                    logger.info("already screenshot for %s", month_first)
                    flag = False
        if flag is True:
            logger.info("%s need to do screenshot", website["redirect_url"])
            rurl = website["redirect_url"]
            id = str(website["_id"])
            screenshot_crawler.run(rurl, id, dest, timeout=22)
            screenshotId = None

            jpgfile = dest + id + '.jpg'
            if os.path.isfile(jpgfile):
                size = os.path.getsize(jpgfile)
                if size > 0:
                    screenshotId = screenshot_crawler.save(jpgfile, id)
                os.remove(jpgfile)

            if screenshotId is not None:
                item = {
                    "screenshotDate": month_first,
                    "screenshotId": screenshotId,
                    "screenshotTime": datetime.datetime.now()- datetime.timedelta(hours=8)
                }

                collection_website.update_one({"_id": website["_id"]},{"$addToSet": {"screenshotIds": item}})
            logger.info("%s screenshot finished with id:%s", website["redirect_url"], screenshotId)
    mongo.close()

def saveWebsite(item):
    mongo = db.connect_mongo()
    collection_website = mongo.info.website
    record = collection_website.find_one({"url": item["url"]})
    if record:
        _id = record.pop("_id")
        if record.has_key("404retryTimes"):
            collection_website.update_one({"_id": _id}, {'$set': {"404retryTimes.retryTimes": 0,
                                                                  "404retryTimes.lastretryTime": datetime.datetime.now()}})
            record.pop('404retryTimes')

        if record["httpcode"] != item["httpcode"] or \
           record.get("redirect_url") != item.get("redirect_url") or \
           record.get("title") != item.get("title"):
           # record.get("description") !=  item.get("description"):

            logger.info("Info changed for %s", item["url"])
            item["createTime"] = record["createTime"]
            item["modifyTime"] = datetime.datetime.now()
            item["websiteCheckTime"] = datetime.datetime.now()
            if record.has_key("screenshotIds") and len(record["screenshotIds"]) > 0:
                item["screenshotIds"] = record["screenshotIds"]
                record.pop("screenshotIds")
            histories = []
            if record.has_key("histories") and len(record["histories"]) > 0:
                histories.extend(record["histories"])
                record.pop("histories")
            histories.append(record)
            item["histories"] = histories
            collection_website.replace_one({"_id": _id}, item)


        #Set websiteCheckTime
        collection_website.update_one({"_id": _id}, {'$set': {"websiteCheckTime": datetime.datetime.now()}})

    # check
    for bbword in ["赌博","一夜情","裸聊","三级片","色情","葡京","床戏","黄色", "成人网站", "成人社区","成人电影","做爱","威尼斯"]:
        if item.has_key("description") is True and item["description"] is not None and item["description"].find(bbword) >= 0:
            update_website(item["url"])
            break
        if item.has_key("title") is True and item["title"] is not None and item["title"].find(bbword) >= 0:
            update_website(item["url"])
            break
        if item.has_key("tags") is True and item["tags"] is not None and item["tags"].find(bbword) >= 0:
            update_website(item["url"])
            break

    mongo.close()

def update_website(url):
    conn = db.connect_torndb()
    sql = "update artifact set active='N', modifyUser=-560 where link=%s and id>0"
    conn.update(sql, url)
    conn.close()

def setRetryTime(url):
    fail = False
    mongo = db.connect_mongo()
    collection_website = mongo.info.website
    website = collection_website.find_one({"url": url})
    if website is not None:
        if website.has_key("404retryTimes"):
            logger.info("Have tried 404 url :%s for :%s", url, website["404retryTimes"]["retryTimes"])
            if website["404retryTimes"]["retryTimes"] >= 2: fail = True
            else: collection_website.update_one({"url": url}, {'$set': {"404retryTimes.retryTimes": website["404retryTimes"]["retryTimes"]+1,
                                                                       "404retryTimes.lastretryTime": datetime.datetime.now()}})
        else:
            logger.info("New retry for 404 url: %s", url)
            item_retry = {"retryTimes": 1, "lastretryTime": datetime.datetime.now()}
            collection_website.update_one({"url": url}, {'$set': {"404retryTimes": item_retry}})
    mongo.close()
    return fail

def getWebsite():
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)
        # logger.info("Checking : %s", URL)
        retry = 0
        while True:
            logger.info("Checking : %s", URL)
            meta = website.get_meta_info(URL)
            if meta is None :
                if retry >= 2:
                    if setRetryTime(URL) is True:
                        logger.info("Retry time is 3")
                        meta = {
                            "url": URL,
                            "httpcode": 404
                        }
                        saveWebsite(meta)
                    break
                else:
                    retry += 1
                    continue
            else:
                saveWebsite(meta)
                # screenshot(URL)
                SCREENURLS.append(URL)
                break

def ssWebsite():
    while True:
        if len(SCREENURLS) == 0:
            return
        SCREENURL = SCREENURLS.pop(0)

        screenshot(SCREENURL)

def start_run(concurrent_num):
    while True:
        logger.info("website check start...")

        dt = datetime.date.today()
        today = datetime.datetime(dt.year, dt.month, dt.day)
        daysago = today - datetime.timedelta(days=15)
        minsago = today - datetime.timedelta(days=1)

        mongo = db.connect_mongo()
        collection_website = mongo.info.website
        webs = list(collection_website.find({"$and": [{"$or": [{"websiteCheckTime": None},{"websiteCheckTime": {"$lt":daysago}}]},
                                                      {"$or": [{"404retryTimes.lastretryTime": None},{"404retryTimes.lastretryTime": {"$lt": minsago}}]}],
                                             "url": {"$ne": None}
                                             }).limit(1000))

        # webs = list(collection_website.find({"websiteCheckTime": None}))
        mongo.close()

        for web in webs:
            url = web["url"]
            print url
            if url is None:
                continue
            URLS.append(url)
        # URLS.append("http://www.wenwo.com")
        logger.info("website num:%s", len(webs))
        threads = [gevent.spawn(getWebsite) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        # ssWebsite()

        logger.info("website check end.")
        # print webs
        # exit()
        if len(webs) == 0:
            # exit()
            gevent.sleep(60*20)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        start_run(20)
    else:
        URL = sys.argv[1]
        # meta = website.get_meta_info(URL)
        # if meta is None :
        #     meta = {
        #         "url": URL,
        #         "httpcode": 404
        #     }
        # saveWebsite(meta)
        screenshot_test(URL, "1")



