# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import config as tsbconfig
import db as dbcon
from basic_track import CompanyTracker
from common import dbutil

import json
from datetime import datetime, timedelta
from kafka import KafkaClient, SimpleProducer

# init kafka
url = tsbconfig.get_kafka_config()
kafka = KafkaClient(url)
producer_track = SimpleProducer(kafka)


class OnFundingCompanyTracker(CompanyTracker):

    """
    update every day
    """

    def __init__(self):

        CompanyTracker.__init__(self)
        self.check_period = 90
        self.today = datetime.now()
        self.yesterday = self.today - timedelta(days=1)

    def update_all_onfunding(self):

        global producer_track
        for fa in dbutil.get_all_FA(self.db, self.yesterday):
            cid = fa.companyId
            if not cid:
                continue
            msg = u'%s, %s开启了新一轮融资' % \
                  (dbutil.get_company_brief(self.db, cid), dbutil.get_company_name(self.db, cid))
            feed_back = dbutil.update_company_message(self.db, cid, msg, 8001, 80, fa.id)
            if feed_back:
                self.send_company_message_msg(feed_back)
                # investor track
            for iid in dbutil.get_company_investors(self.db, cid):
                imid = dbutil.update_investor_message(self.db, iid, msg, 8001, 80, fa.id)
                if imid:
                    dbutil.update_investor_message_detail(self.db, imid, cid)

    def update_all_afterfunding(self, today=None):

        today = datetime.today() if not today else today
        today = today.date()
        for repeat in xrange(1, 4):
            for funding in dbutil.get_funding_by_date(self.db, (today-timedelta(days=1+self.check_period*repeat),
                                                                today-timedelta(days=self.check_period*repeat))):
                # cid = funding.companyId
                copid = funding.corporateId
                for cid in dbutil.get_corporate_companies(self.db, copid):
                    latest = dbutil.get_corporate_latest_funding(self.db, copid)
                    if latest and latest.id == funding.id:
                        self.mongo.track.track.insert({
                            'topic_id': 6,
                            'company_id': cid,
                            'abstract':
                                u'%s距离上一次融资已经过去%s个月了' % (dbutil.get_company_name(self.db, cid), repeat*3),
                            'createTime': today
                        })


def makeup():

    from kafka import KafkaClient, SimpleProducer
    from kafka.errors import FailedPayloadsError

    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    producer_track = SimpleProducer(kafka)

    db = dbcon.connect_torndb()
    for cm in db.query('select * from company_message where trackdimension=8001'):
        if not cm.relateId:
            continue
        fa = db.get('select * from company_fa where id=%s;', cm.relateId)
        if not fa.createTime:
            continue
        if cm.createTime > (fa.createTime+timedelta(days=15)):
            continue
        else:
            db.execute('update company_message set active="P" where id=%s;', cm.id)
    for im in db.query('select * from investor_message where trackdimension=8001'):
        if not im.relateId:
            continue
        fa = db.get('select * from company_fa where id=%s;', im.relateId)
        if not fa.createTime:
            continue
        if im.createTime > (fa.createTime+timedelta(days=15)):
            continue
        else:
            db.execute('update investor_message set active="P" where id=%s;', im.id)


if __name__ == '__main__':

    print __file__
    makeup()
