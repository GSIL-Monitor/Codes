# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../spider2'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon


def process_dup():

    mongo = dbcon.connect_mongo()
    for record in mongo.article.news.find():
        cids = record.get('companyIds', [])
        if not cids:
            continue
        if len(set(cids)) == len(cids):
            continue
        mongo.article.news.update({'_id': record['_id']}, {'$set': {'companyIds': list(set(cids))}})
        print record['_id']


if __name__ == '__main__':

    process_dup()