# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config
import db, util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import parser_db_util
import pymongo

# logger
loghelper.init_logger("parser_qixin_r", stream=True)
logger = loghelper.get_logger("parser_qixin_r")

SOURCE = 13093  #
TYPE = 36008  # 工商


def update(name):
    mongo = db.connect_mongo()
    collection_name = mongo.info.gongshang_name
    collection = mongo.info.gongshang
    collection.delete_one({"name": name})
    collection_name.update_one({"name": name}, {'$set': {"lastCheckTime": None}})
    mongo.close()

def process():

    while True:
        mongo = db.connect_mongo()
        collection = mongo.info.gongshang
        items = list(collection.find({'invests.name.name':{'$exists':True}}))
        for item in items:
            name = item["name"]
            logger.info("updating %s",name)
            update(name)

        break



if __name__ == '__main__':
    while True:
        process()
        logger.info('end')
        time.sleep(60)
