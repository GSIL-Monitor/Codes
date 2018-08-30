# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon

import pymongo
from copy import deepcopy
from datetime import datetime, timedelta


def analyze():

    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()
    xiniuoids = [item.id for item in db.query('select id from organization where name like "烯牛%%";')]
    nxinius = [item.userId for item in db.query('select distinct userId from user_organization_rel '
                                                'where organizationId not in %s;', xiniuoids)]

    cach_time = None
    pages = 10
    for record in mongo.log.api_log.find({'requestURL': '/api/company/track/getByTag',
                                          'time': {'$gt': datetime.strptime('2016-10-01', '%Y-%m-%d')},
                                          'userId': {'$in': nxinius}}).sort([('userId', pymongo.ASCENDING),
                                                                             ('time', pymongo.ASCENDING)]):

        uid = record['userId']
        # if uid == 19:
        #     print record

        # check if he reads
        # read_news = '/api/company/crawler/news/get'
        # next_move = mongo.log.api_log.find_one({'userId': uid, 'time': {'$gt': record['time']}})
        # if not next_move:
        #     continue
        # if (not (next_move['requestURL'] == read_news)) or (next_move['time'] - record['time']).total_seconds() > 1200:
        #     invalid += 1
        #     continue

        # if he reads
        if not cach_time:
            cach_time = deepcopy(record['time'])
            pages = 10
            continue
        if (record['time'] - cach_time).total_seconds() < 0:
            cach_time = None
            pages = 10
            # print 'Switch User'
            continue
        if record['data']['payload']['start'] > 0:
            pages = record['data']['payload']['start']
            continue
        else:
            read_period = min(timedelta(seconds=300), (record['time'] - cach_time))
            read_count = mongo.log.api_log.find({'userId': uid, 'requestURL': '/api/company/crawler/news/get',
                                                 'time': {'$gte': cach_time, '$lte': cach_time + read_period}}).count()
            if read_count == 0:
                cach_time = deepcopy(record['time'])
                pages = 10
                continue
            print uid, cach_time, read_count, pages
            cach_time = deepcopy(record['time'])
            pages = 10

if __name__ == '__main__':

    analyze()