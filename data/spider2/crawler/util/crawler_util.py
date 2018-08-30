# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import urllib2
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))

import loghelper, db

#logger
loghelper.init_logger("crawler_util", stream=True)
logger = loghelper.get_logger("crawler_util")

#mongo
mongo = db.connect_mongo()
collection = mongo.raw.projectdata
trend_android_collection = mongo.trend.android
collection_news = mongo.article.news

def get_lastest_key_int_news(SOURCE, TYPE=0):
    if TYPE == 0:
        latest = list(collection_news.find({"source":SOURCE}).sort("key_int", pymongo.DESCENDING).limit(1))
    else:
        latest = list(collection_news.find({"source": SOURCE, "type": TYPE}).sort("key_int", pymongo.DESCENDING).limit(1))
    if len(latest) > 0:
        return latest[0]["key_int"]
    return None


def get_latest_key_int(SOURCE,TYPE):
    latest = list(collection.find({"source":SOURCE, "type":TYPE}).sort("key_int", pymongo.DESCENDING).limit(1))
    if len(latest) > 0:
        return latest[0]["key_int"]
    return None

def get(SOURCE, TYPE, key):
    item = collection.find_one({"source":SOURCE, "type":TYPE, "key":key})
    return item


def save_download(apkname, TYPE, download, score):
    dt = datetime.date.today()
    today = datetime.datetime(dt.year, dt.month, dt.day)
    r = trend_android_collection.find_one(({"appmarket":TYPE, "apkname": apkname, "date": today}))

    # insure download increasing
    dt2 = dt - datetime.timedelta(1)
    yesterday = datetime.datetime(dt2.year, dt2.month, dt2.day)
    r2 = trend_android_collection.find_one(({"appmarket": TYPE, "apkname": apkname, "date": yesterday}))

    if r2 is not None:
        if download < r2["download"]:
            download = r2["download"]

    if r is None:
        result = {
            "apkname": apkname,
            "date":today,
            "appmarket":TYPE,
            "download": download,
            "score":score
        }
        trend_android_collection.insert_one(result)
    else:
        result = {
            "download": download,
            "score":score
        }
        trend_android_collection.update_one({"_id": r["_id"]}, {'$set': result})


def save_comment(apkname, TYPE, comment):
    dt = datetime.date.today()
    today = datetime.datetime(dt.year, dt.month, dt.day)
    r = trend_android_collection.find_one(({"appmarket":TYPE, "apkname": apkname, "date": today}))

    if r is None:
        result = {
            "apkname": apkname,
            "date":today,
            "appmarket":TYPE,
            "comment": comment
        }
        trend_android_collection.insert_one(result)
    else:
        result = {
            "comment": comment
        }
        trend_android_collection.update_one({"_id": r["_id"]}, {'$set': result})


def save_download_comment(apkname, TYPE,  download, score, comment):
    dt = datetime.date.today()
    today = datetime.datetime(dt.year, dt.month, dt.day)
    r = trend_android_collection.find_one(({"appmarket":TYPE, "apkname": apkname, "date": today}))

    # insure download increasing
    dt2 = dt - datetime.timedelta(1)
    yesterday = datetime.datetime(dt2.year, dt2.month, dt2.day)
    r2 = trend_android_collection.find_one(({"appmarket": TYPE, "apkname": apkname, "date": yesterday}))

    if r2 is not None:
        if download < r2["download"]:
            download = r2["download"]

    if r is None:
        result = {
            "apkname": apkname,
            "date":today,
            "appmarket":TYPE,
            "download": download,
            "score":score,
            "comment":comment
        }
        trend_android_collection.insert_one(result)
    else:
        result = {
            "download": download,
            "score":score,
            "comment":comment
        }
        trend_android_collection.update_one({"_id": r["_id"]}, {'$set': result})