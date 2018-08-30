# -*- coding: utf-8 -*-
import os, sys

import datetime, time
import json, re, copy

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config
import db, util


def patch(collection):
    items = list(collection.find({}))
    for item in items:
        sourceId_str = str(item['sourceId']) if item['source'] != 13402 else item['stockwebsite'].split('code=')[-1]
        collection.update_one({'_id': item['_id']}, {'$set': {'sourceId_str': sourceId_str}})


if __name__ == '__main__':
    # mongo
    mongo = db.connect_mongo()

    for name in ['neeq', 'sse', 'szse']:
    # for name in ['szse']:
        collection = mongo['stock'][name]
        patch(collection)
