# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
import loghelper
from common import dbutil
# from task.news_postprocess import NewsTagger

import codecs
from bson import ObjectId
from datetime import datetime, timedelta
from pymongo import DESCENDING

loghelper.init_logger('tmp')
l = loghelper.get_logger('tmp')


def clean_dup():

    global l
    mongo = dbcon.connect_mongo()
    for t in mongo.task.company.aggregate([{'$match': {'processStatus': 0, 'no_share': False, 'taker': None,
                                                       'createTime': {'$lt': (datetime.now() - timedelta(days=1))}}},
                                           {'$group': {'_id': '$companyId', 'count': {'$sum': 1}}},
                                           {'$match': {'count': {'$gt': 1}}}]):
        l.info('Processing %s' % t)
        for st in sorted(mongo.task.company.find({'companyId': t['_id']}), key=lambda x: x['createTime'])[: -1]:
            mongo.task.company.update({'_id': st['_id']},
                                      {'$set': {'processStatus': 1, 'taker': 139, 'mark': 'dup201708'}})


def dump_news():

    mongo = dbcon.connect_mongo()
    with codecs.open('files/605266.txt', 'w', 'utf-8') as fo:
        for news in mongo.article.news.find({'features': 605266, 'processStatus': 1}):
            url = 'http://www.xiniudata.com/news/%s' % news['_id']
            fo.write('%s\t%s\t%s\t%s\n' % (news.get('title', ''), news.get('source', ''), news.get('createTime'), url))


def statistic_funding():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    news = [n.newsId for n in db.query('select newsId from funding where (active is null or active="Y") '
                                       'and newsId is not null order by id desc limit 5000')]
    print len(news), news[:2]
    news = [mongo.article.news.find_one({'_id': ObjectId(nid)}).get('date', False) for nid in news]
    print len(news), news[:2]
    news = [str(int(d.strftime('%H')) + 8) for d in news if d]
    with codecs.open('files/date', 'w', 'utf-8') as fo:
        fo.write('\n'.join(news))
    print mongo.task.news.find({'processStatus': 0}).count()


if __name__ == '__main__':

    print __file__
    statistic_funding()
    # dump_news()
    # makup4xiniu()
    # clean_0105()
    # clean_dup()
