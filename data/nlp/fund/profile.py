# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import db as dbcon
import loghelper
from common import dbutil

import json
from datetime import datetime, timedelta

loghelper.init_logger("investor_profile", stream=True)
logger_ip = loghelper.get_logger('investor_profile')


class InvestorProfile(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()

    def generate_keywords(self):

        global logger_ip
        y2017 = datetime.strptime('2017-01-01', '%Y-%m-%d')
        y2018 = datetime.strptime('2018-01-01', '%Y-%m-%d')
        day30 = datetime.now() - timedelta(days=30)
        day90 = datetime.now() - timedelta(days=90)
        day180 = datetime.now() - timedelta(days=180)
        for iid, name in dbutil.get_all_investor(self.db):
            try:
                # regular, for all portfolio
                dbutil.update_investor_profile(self.db, iid, 2018,
                                               json.dumps(dbutil.get_investor_profile(self.db, iid, y2018)))
                dbutil.update_investor_profile(self.db, iid, 2017,
                                               json.dumps(dbutil.get_investor_profile(self.db, iid, y2017, y2018)))
                dbutil.update_investor_profile(self.db, iid, 0,
                                               json.dumps(dbutil.get_investor_profile(self.db, iid)))
                dbutil.update_investor_profile(self.db, iid, 1,
                                               json.dumps(dbutil.get_investor_profile(self.db, iid, day90)))
                dbutil.update_investor_profile(self.db, iid, 2,
                                               json.dumps(dbutil.get_investor_profile(self.db, iid, day180)))
                dbutil.update_investor_profile(self.db, iid, 3,
                                               json.dumps(dbutil.get_investor_profile(self.db, iid, day30)))
                logger_ip.info('Processed, %s, %s' % (iid, name))
                # just for blockchain portfolio
                dbutil.update_investor_profile(self.db, iid, 0, json.dumps(dbutil.get_investor_profile(
                    self.db, iid, y2018, portfolio_tag=175747, ignore_tags={175747})), 175747)
                dbutil.update_investor_profile(self.db, iid, 1, json.dumps(dbutil.get_investor_profile(
                    self.db, iid, day90, portfolio_tag=175747, ignore_tags={175747})), 175747)
                dbutil.update_investor_profile(self.db, iid, 2, json.dumps(dbutil.get_investor_profile(
                    self.db, iid, day180, portfolio_tag=175747, ignore_tags={175747})), 175747)
                logger_ip.info('Processed blockchain tags, %s, %s' % (iid, name))
            except Exception, e:
                logger_ip.info('Failed, %s, %s' % (iid, e))

    def test(self):

        curr_year = datetime.strptime('2017-01-01', '%Y-%m-%d')
        cids1 = dbutil.get_investor_portfilio(self.db, 2164, (curr_year, datetime.now().strftime('%Y-%m-%d')), 175747)
        cids2 = dbutil.get_investor_portfilio(self.db, 2164, (curr_year, datetime.now().strftime('%Y-%m-%d')))
        print len(cids1), len(cids2)
        print cids1
        print dbutil.get_investor_profile(self.db, 2164, curr_year, portfolio_tag=175747)
        dbutil.update_investor_profile(self.db, 2164, 0,
                                       json.dumps(dbutil.get_investor_profile(self.db, 2164,
                                                                              curr_year, portfolio_tag=175747)), 175747)


if __name__ == '__main__':

    print __file__
    ip = InvestorProfile()
    # ip.test()
    ip.generate_keywords()
