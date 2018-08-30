# -*- coding: utf-8 -*-
import os, sys
import datetime
import random

from pymongo import MongoClient
import pymongo
from distutils.version import LooseVersion
import json

reload(sys)
sys.setdefaultencoding("utf-8")
#
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, config, url_helper, util, db

# logger
loghelper.init_logger("appmini", stream=True)
logger = loghelper.get_logger("appmini")


def get_new_item(item, record):
    item = dict(item)
    record = dict(record)
    record.pop('createtime')
    if record.has_key('modifytime'):
        record.pop('modifytime')
    if record.has_key('updatedate'):
        record.pop('updatedate')
    item.pop('createtime')
    if item.has_key('modifytime'):
        item.pop('modifytime')
    if item == record:
        return item, 'same'
    logger.info(json.dumps(item,ensure_ascii=False,indent=2,cls=util.CJsonEncoder))
    logger.info(json.dumps(record,ensure_ascii=False,indent=2,cls=util.CJsonEncoder))
    for key in record.keys():
        if item.get(key) is None:
            item[key] = record[key]
    return item, 'diff'


def save(collection_market, source, item):
    # projection histories false 不显示历史字段
    record = collection_market.find_one({'name': item['name'], 'source': source}, projection={'histories': False})
    if record:
        _id = record.pop('_id')
        new_item, status = get_new_item(item, record)
        if status == 'diff':
            new_item['createtime'] = item['createtime']
            new_item['modifytime'] = datetime.datetime.now()
            if new_item.get('updatedate') is None:
                new_item['updatedate'] = datetime.datetime.now()
            collection_market.update_one({"_id": _id}, {'$set': new_item, '$addToSet': {"histories": record}})
            logger.info('new version ---> addtoset down')
        else:
            new_item['createtime'] = record['createtime']
            new_item['modifytime'] = datetime.datetime.now()
            collection_market.update_one({"_id": _id}, {'$set': new_item})
            logger.info('same version ---> update done')
    else:
        item["createtime"] = datetime.datetime.now()
        item["modifytime"] = datetime.datetime.now()
        if item.get('updatedate') is None:
            item["updatedate"] = datetime.datetime.now()
        try:
            collection_market.insert(item)
            logger.info('insert a new item down')
        except Exception, e:
            logger.info(e)



def merge(item):
    item = dict(item)
    for key in item.keys():
        if key in ['_id', 'rank', 'index', 'source', 'appid','updatedate']:
            item.pop(key)
    if item.has_key("screenshots") and len(item["screenshots"]) > 0:
        sshots = item["screenshots"]
        if sshots[0].find("bdimg") >= 0:
            # baidu image not work
            item["screenshots"] = []
    mongo = db.connect_mongo()
    collection = mongo.market.appmini
    miniapp = collection.find_one({'name':item['name']},projection={'histories':False})
    if miniapp is None:
        item["createtime"] = datetime.datetime.now()
        item["modifytime"] = item["createtime"]
        try:
            collection.insert(item)
            logger.info('insert a new miniapp down')
        except Exception,e:
            logger.info(e)
    else:
        _id = miniapp.pop('_id')
        new_app, status = get_new_item(item,miniapp)
        if status == 'diff':
            new_app['createtime'] = item['createtime']
            new_app['modifytime'] = datetime.datetime.now()
            collection.update_one({"_id": _id}, {'$set': new_app, '$addToSet': {"histories": miniapp}})
            logger.info('new version miniapp ---> addtoset down ')
        else:
            logger.info('no change')
            pass
    mongo.close()

if __name__ == '__main__':
    mongo = db.connect_mongo()
    collection = mongo.market.appmini_market
    items = list(collection.find({'source':16080}))
    for item in items:
        merge(item)
    mongo.close()





