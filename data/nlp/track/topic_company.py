# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../search'))

import db as dbcon
from common import dbutil
from client import SearchClient
from basic_track import CompanyOrientedTopic

import logging
import time

# logging
logging.getLogger('track').handlers = []
logger_track = logging.getLogger('track')
logger_track.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_track.addHandler(stream_handler)


def update_company_oriented_topics():

    global logger_track
    while True:
        db = dbcon.connect_torndb()
        client = SearchClient()
        logger_track.info('Model inited, start to update company oriented topics')
        for tpid, _ in dbutil.get_general_topics(db, 902):
            try:
                logger_track.info('Processing %s' % tpid)
                cot = CompanyOrientedTopic(tpid)
                cot.fit(client)
                cot.fit_tags()
                cot.fit_comps()
            except Exception, e:
                logger_track.exception('%s failed, %s' % (tpid, e))
        db.close()
        time.sleep(3600)


def test():

    global logger_track
    db = dbcon.connect_torndb()
    client = SearchClient()
    logger_track.info('Model inited, start to update company oriented topics')
    cot = CompanyOrientedTopic(88)
    cot.fit(client)
    db.close()


if __name__ == '__main__':

    if sys.argv[1] == 'cot':
        update_company_oriented_topics()
    if sys.argv[1] == 'test':
        test()