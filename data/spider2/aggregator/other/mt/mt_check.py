# -*- coding: utf-8 -*-
import os, sys
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper, config
import db, name_helper, url_helper
import json, config, traceback, time, util
from bson.objectid import ObjectId
import random

# logger
loghelper.init_logger("mt_check", stream=True)
logger = loghelper.get_logger("mt_check")

mongo = db.connect_mongo()
collection = mongo['open-maintain'].task
collectionUser = mongo['open-maintain'].user
conn = db.connect_torndb()


def start_run():
    while True:
        items = list(collection.find({'processStatus': 1, 'auditProcess': {"$ne": 1}, 'active': 'Y'}).limit(1000))
        for i in items:
            user = collectionUser.find_one({'userId': i['taskUser']})
            checkRatio = user.get('checkRatio', 10)

            randomcnt = random.uniform(0, 100)
            if randomcnt <= checkRatio:
                logger.info('task:%s need to be audited', i['_id'], )
                collection.update_one({'_id': i['_id']}, {'$set': {'auditUser': user.get('supervisor', -666)}})

            logger.info('processed audit task:%s', i['_id'], )
            collection.update_one({'_id': i['_id']}, {'$set': {'auditProcess': 1}})

        time.sleep(60)


if __name__ == "__main__":
    while True:
        try:
            start_run()
        except Exception, e:
            logger.exception(e)
            # traceback.print_exc()
            time.sleep(1)
            start_run()
