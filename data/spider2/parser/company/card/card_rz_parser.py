# -*- coding: utf-8 -*-
import os, sys, re
import time
import datetime
from bson.objectid import ObjectId
import json
from pypinyin import pinyin, lazy_pinyin
import pypinyin
import random
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, name_helper, url_helper, download, db


#logger
loghelper.init_logger("card_rz_parser", stream=True)
logger = loghelper.get_logger("card_rz_parser")


mongo = db.connect_mongo()
collection = mongo.raw.qmp_rz
# collection = mongo.raw.qmp_rz_parser

def card_rz_parser():
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_rz
    try:
        items = list(collection.find({'check':'N'}))
        # items = list(collection.find({'_id': ObjectId("5b399c5edeb47119d4f73a2b")}))
        for item in items:
            date = item['date']
            # country = item['country']
            lunci = item['lunci']
            page = item['page']
            collection.update({'_id':item['_id']},{'$set':{'check':'Y'}})
            logger.info('start to parse date:%s  | lunci:%s | page:%d'%(date,lunci,page))
            rzlist = item['content']['list']
            if len(rzlist) == 0:
                continue
            for rz in rzlist:
                if rz.has_key('yewu') and rz.has_key('luncis') and rz.has_key('product_id') and rz.has_key('lunci_count'):
                    rzitem = {}
                    rzitem.update(rz['yewu'])
                    if len(rz['luncis']) != 0:
                        rzitem.update(rz['luncis'][0])
                    rzitem['product_id'] = rz['product_id']
                    rzitem['lunci_count'] = rz['lunci_count']
                    # print(rzitem)
                    save_card_rz_parser(rzitem)
    except Exception,e:
        logger.info('mongo error:%s'%e)
    mongo.close()


def save_card_rz_parser(rzitem):
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_rz_parser
    try:
        product = rzitem['product']
        company = rzitem['company']
        jieduan = rzitem['jieduan']
        money = rzitem['money']
        item = collection.find_one({'product':product,'company':company,'jieduan':jieduan,'money':money})
        if item is None:
            collection.insert_one(rzitem)
            logger.info('product:%s | company:%s | lunci:%s | money:%s parse done'%(product,company,jieduan,money))
        # else:
        #     if product == '多听FM':
        #         print(item)
    except Exception, e:
        logger.info('mongo error:%s' % e)
    mongo.close()

if __name__ == '__main__':
    card_rz_parser()