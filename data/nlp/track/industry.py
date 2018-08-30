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
from basic_track import Industry

import logging
import time

# logging
logging.getLogger('industry').handlers = []
logger_industry = logging.getLogger('industry')
logger_industry.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_industry.addHandler(stream_handler)


def update_industries():

    global logger_industry
    logger_industry.info('Start to process industries')
    while True:
        db = dbcon.connect_torndb()
        client = SearchClient()
        logger_industry.info('Model inited, start to update industries')
        for idid, _ in dbutil.get_industries(db):
            try:
                logger_industry.info('Processing %s' % idid)
                industry = Industry(idid)
                industry.fit_company(client)
                industry.fit_comps()
                industry.fit_tag()
                industry.fit_news()
                dbutil.update_industry_last_message_time(db, idid)
            except Exception, e:
                logger_industry.exception('%s failed, %s' % (idid, e))
        db.close()
        time.sleep(1800)


def test():

    global logger_industry
    db = dbcon.connect_torndb()
    client = SearchClient()
    logger_industry.info('Model inited, start to update company oriented topics')
    idid = 732
    industry = Industry(idid)
    industry.fit_company(client)
    industry.fit_comps()
    industry.fit_tag()
    industry.fit_news()
    dbutil.update_industry_last_message_time(db, idid)
    db.close()


if __name__ == '__main__':

    if sys.argv[1] == 'incr' or sys.argv[1] == 'incremental':
        update_industries()
    if sys.argv[1] == 'test':
        test()
