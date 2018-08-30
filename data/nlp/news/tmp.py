# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon

import codecs
from datetime import datetime


def dump():

    mongo = dbcon.connect_mongo()
    start, end = datetime.strptime('20180401', '%Y%m%d'), datetime.strptime('20180601', '%Y%m%d')
    for tag in [128, 578353]:
        with codecs.open('dumps/%s.txt' % tag, 'w', 'utf-8') as fo:
            for news in mongo.article.news.find({"features": tag, "processStatus": 1,
                                                 "date": {'$gte': start, '$lt': end}}):
                url = 'http://www.xiniudata.com/news/%s' % news['_id']
                fo.write('%s\t%s\t%s\t%s\n' % (url, news['title'], news['source'], news['date']))


if __name__ == '__main__':

    dump()

