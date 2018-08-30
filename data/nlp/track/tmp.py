# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil

import codecs
from datetime import datetime, timedelta


def modify_im():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    start = datetime.now() - timedelta(days=180)
    for news in mongo.article.news.find({'features': 578351, 'createTime': {'$gt': start}}):
        for iid in news.get('investorIds', []):
            dbutil.update_investor_message(db, iid, news.get('title', ''), 1005, 10, str(news['_id']), active='Y')
    db.close()


def check_apprank():

    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()
    today = datetime.today()
    todays = list(mongo.trend.appstore_rank.find({'date': {'$gt': (today - timedelta(days=1)), '$lte': today},
                                                  'rank': {'$lte': 500}}))
    yesterdays = list(mongo.trend.appstore_rank.find({'date': {'$gt': (today - timedelta(days=2)),
                                                                '$lt': (today - timedelta(days=1))},
                                                      'rank': {'$lte': 500}}))
    newin = {}
    first = set()
    yesterdays = set(item['trackId'] for item in yesterdays)
    day_thirday = today - timedelta(days=30)
    for item in filter(lambda x: x['trackId'] not in yesterdays, todays):
        mongo.temp.appstore.insert_one({'type': 3017, 'createTime': today, 'item': item})
        for aid in dbutil.get_artifacts_from_iOS(db, item['trackId']):
            newin[aid] = item
            previous = mongo.trend.appstore_rank.find({'trackId': item['trackId'], 'genre': item['genre'],
                                                       'type': item['type'], 'rank': {'$lt': 500}}).count()
            if previous == 1:
                cid = dbutil.get_artifact_company(db, aid)
                print aid, dbutil.get_company_code(db, cid)
                first.add(cid)
    print len(newin), len(first)
    print '\n'.join(['http://pro.xiniudata.com/validator/#/company/%s/overview' % dbutil.get_company_code(db, cid) for cid in first])


if __name__ == '__main__':

    modify_im()
    # check_apprank()
