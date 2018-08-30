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


def dump_search():

    mongo = dbcon.connect_mongo()
    resutls = set([record['data']['data']['input'] for record in
                   mongo.log.api_log.find({"requestURL": "/api/search/open", "userId": {'$ne': [12, 2, 214, 213]}})])
    mongo.close()
    with codecs.open('dumps/search.160830.log', 'w', 'utf-8') as fo:
        fo.write('\n'.join(resutls))


if __name__ == '__main__':

    dump_search()
