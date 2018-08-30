# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

import db as dbcon

import datetime
import logging
import json
import requests


# logging
logging.getLogger('search_functionality').handlers = []
logger_functionality = logging.getLogger('search_functionality')
logger_functionality.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_functionality.addHandler(stream_handler)


class FunctionalityTester():

    def __init__(self, server=1):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo().log
        self.server = {
            1: '10.27.73.209:5001',
            2: '10.27.73.237:5001',
            'dev': '10.44.202.51:5001',
            'local': '0.0.0.0:5007'
        }[server]

    def test_tags(self):

        """
        results of tag searches cannot be to few
        """

        global logger_functionality
        url = 'http://%s/api/search/general' % self.server
        for tag in self.db.query('select name from tag where type in (11012, 11011, 11010, 11100, 11200);'):
            try:
                logger_functionality.info('%s processed' % tag)
                r = json.loads(requests.post(url, json={"input": tag.name, "filter": {}}).text)
                if r['company']['count'] < 5:
                    self.mongo.search_functionality.insert({
                        'search': tag,
                        'status': 0,
                        'date': datetime.datetime.now(),
                        'type': 'tag mismatch'
                    })
            except Exception, e:
                self.mongo.search_functionality.insert({
                    'search': tag,
                    'status': 0,
                    'date': datetime.datetime.now(),
                    'type': 'tag failure',
                    'exception': e
                })
                logger_functionality.exception('Failed %s, %s' % (tag, e))


if __name__ == '__main__':

    ft = FunctionalityTester()
    ft.test_tags()