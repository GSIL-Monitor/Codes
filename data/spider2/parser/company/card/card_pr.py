# -*- coding: utf-8 -*-
import random, math
import os, sys, datetime, re, json, time
import xlwt
import requests
from lxml import html
from pyquery import PyQuery as pq
import subprocess
import threading

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, extract, db, util, url_helper, download, traceback_decorator, email_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import proxy_pool

# logger
loghelper.init_logger("parser_qmp_investfirm", stream=True)
logger = loghelper.get_logger("parser_qmp_investfirm")



def save_item(item):
    tzs = item['data']['list']
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_person
    for tz in tzs:
        tz["personId"] = tz["id"]
        tz.pop("id")


        record = collection.find_one({'personId':tz["personId"]})
        if record is None:
            collection.insert_one(tz)
            logger.info('save persona :%s done'%(tz["name"]))
        else:
            # del record['_id']
            # logger.info(json.dumps(record,ensure_ascii=False,indent=2))
            logger.info('already exist')
    # collection_item = mongo.raw.qmp
    # collection_item.update({"_id": item["_id"]}, {"$set": {"processed": True}})
    mongo.close()


def take_items():
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp
    items = list(collection.find({'url':'http://vip.api.qimingpian.com/h/persons1','processed':None}))
    mongo.close()
    return items



def run():
    items = take_items()
    if len(items) == 0:
        logger.info('items lens == 0')
        return
    for item in items:
        if item['data']['list'] is None or len(item['data']['list']) == 0:
            logger.info("wrong: %s", item["_id"])
        save_item(item)

if __name__ == '__main__':
    run()