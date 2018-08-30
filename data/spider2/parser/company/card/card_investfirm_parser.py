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
    tzs = item['data']['touzi1']
    ticket = item['postdata']['ticket']
    id = item['postdata']['id']
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_tz_parser
    for tz in tzs:
        tz.update({'ticket':ticket})
        tz.update({'id':id})
        product = tz['product']
        lunci = tz['lunci']
        date = tz['tzdate']

        record = collection.find_one({'ticket':ticket,'id':id,'product':product,'lunci':lunci,'tzdate':date})
        if record is None:
            collection.insert_one(tz)
            logger.info('save product:%s | lunci:%s done'%(product,lunci))
        else:
            del record['_id']
            logger.info(json.dumps(record,ensure_ascii=False,indent=2))
            # logger.info('done')
    collection_item = mongo.raw.qmp
    collection_item.update({"_id": item["_id"]}, {"$set": {"processed": True}})
    mongo.close()


def take_items():
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp
    items = list(collection.find({'url':'http://vip.api.qimingpian.com/d/j3tz_touzi2','processed':None}))
    mongo.close()
    return items



def run():
    items = take_items()
    if len(items) == 0:
        logger.info('items lens == 0')
        return
    for item in items:
        if item['data']['touzi1'] is None:
            continue
        save_item(item)

if __name__ == '__main__':
    run()