# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
import config as tsbconfig
from basic_track import CompanyTracker
from common import dbutil, dicts

import time
import json
import urlparse
import logging
import pandas as pd
from math import log10
from itertools import chain
from datetime import datetime, timedelta
from kafka import KafkaClient, SimpleProducer
from kafka.errors import FailedPayloadsError

# logging
logging.getLogger('track').handlers = []
logger_track = logging.getLogger('track')
logger_track.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_track.addHandler(stream_handler)


producer_track = None


# init kafka
def init_kafka():

    global producer_track
    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    producer_track = SimpleProducer(kafka)


class NewsCompanyTracker(CompanyTracker):

    def __init__(self):

        """
        update every 2 hour
        """

        CompanyTracker.__init__(self)
        self.trusted_source = dicts.get_trust_news_source()
        self.check_period = 2  # check every 2 hour
        init_kafka()

    def feed(self, cid, today=None):

        global producer_track, logger_track
        today = datetime.today() if not today else today

        feeded = False
        for record in self.mongo.article.news.find({
            'companyId': cid,
            'createTime': {'$gt': (today-timedelta(hours=self.check_period)), '$lte': today}
        }):
            if urlparse.urlparse(record['link']).netloc in self.trusted_source:
                track_msg_id = str(self.mongo.track.track.insert({
                    'topic_id': 1,
                    'company_id': cid,
                    'abstract': record['title'],
                    'createTime': today,
                    'contents': record['_id']
                    # 'contents': {
                    #     0: {
                    #         'type': 'news',
                    #         'content': record['_id']
                    #     }
                    # }
                }))
                try:
                    producer_track.send_messages("track_message",
                                                 json.dumps({'id': track_msg_id, 'type': 'track', 'topic_id': 1}))
                except FailedPayloadsError, fpe:
                    logger_track.exception('Kafka Failed Payload Error')

                feeded = True

        return feeded


class NewsSummaryCompanyTracker(CompanyTracker):

    """
    update every month
    """
    def __init__(self):

        CompanyTracker.__init__(self)
        self.abstract = u'本月%s共有%s篇新闻报道'

    def feed(self, cid, today=None):

        global producer_track
        today = datetime.today() if not today else today

        df = pd.DataFrame(list(self.mongo.article.news.find({
            'companyId': cid,
            'createTime': {'$gt': (today-timedelta(days=30)), '$lte': today}
        })))
        if df.shape[0] == 0:
            return

        # news_list = {0: {
        #     'type': 'text',
        #     'content': self.abstract % (dbutil.get_company_name(self.db, cid), df.shape[0])}}
        news_list = list()
        for index, row in enumerate(df.iterrows()):
            news_list.append(row[1]._id)
            # news_list[index+1] = {
            #     'type': 'news',
            #     'content': row[1]._id
            # }
        track_msg_id = str(self.mongo.track.track.insert({
            'topic_id': 2,
            'company_id': cid,
            'abstract': self.abstract % (dbutil.get_company_name(self.db, cid), df.shape[0]),
            'createTime': today,
            'contents': news_list
        }))
        producer_track.send_messages("track_message", json.dumps({'id': track_msg_id, 'type': 'track', 'topic_id': 2}))
        return True


class NewsFundingCompanyTracker(CompanyTracker):

    """
    update every check_period hour
    """
    def __init__(self):

        CompanyTracker.__init__(self)
        self.check_period = 2
        init_kafka()

    def feed_incremental(self):

        global producer_track, logger_track
        fundings = dbutil.get_untracked_fundings(self.db)
        for funding in fundings:
            try:
                logger_track.info('Processing track %s' % funding.id)
                cid, corpid, fid, funding_date = funding.companyId, funding.corporateId, funding.id, funding.fundingDate
                # for cid in dbutil.get_corporate_companies(self.db, copid):
                # none funding date
                if not funding_date:
                    dbutil.mark_funding_tracked(self.db, fid)
                    logger_track.info('%s not funding date' % fid)
                    continue
                # funding date older than 1 year
                # if funding_date < datetime.now() - timedelta(days=365):
                #     dbutil.mark_funding_tracked(self.db, fid)
                #     logger_track.info('%s funding date 1 year ago' % fid)
                #     continue
                # check if publish date is older than 7 days
                if funding.publishDate and funding.publishDate < datetime.now() - timedelta(days=7):
                    dbutil.mark_funding_tracked(self.db, fid)
                    logger_track.info('%s funding published 7 days ago' % fid)
                    continue
                # check if there is publish date
                if not funding.publishDate:
                    dbutil.mark_funding_tracked(self.db, fid)
                    logger_track.info('%s funding no published date' % fid)
                    continue
                # check if this funding is a new funding
                latest = dbutil.get_corporate_latest_funding(self.db, corpid)
                if latest and latest.fundingDate > funding_date:
                    dbutil.mark_funding_tracked(self.db, fid)
                    logger_track.info('%s not new, funding id %s, had %s' % (cid, fid, latest.id))
                    continue
                if latest and latest.fundingDate == funding_date and not latest.id == fid:
                    dbutil.mark_funding_tracked(self.db, fid)
                    logger_track.info('%s not new, funding id %s, had %s' % (cid, fid, latest.id))
                    continue
                # only from ipo
                sources = dbutil.get_company_source(self.db, cid)
                if len(sources) == 1 and len(sources & {13400, 13401, 13402}) == 1:
                    dbutil.mark_funding_tracked(self.db, fid)
                    logger_track.info('%s just IPO, funding id %s' % (cid, fid))
                    continue
                name = dbutil.get_company_name(self.db, cid)
                abstract = u'%s获得新一轮融资' % name

                track_msg_id = str(self.mongo.track.track.insert({
                    'topic_id': 3,
                    'company_id': cid,
                    'abstract': abstract,
                    'createTime': datetime.today()
                }))

                self.track_funding(cid, track_msg_id, fid, abstract)
                self.track_funding_for_investor_message(cid, fid, dbutil.get_funding_investor_ids(self.db, fid),
                                                        funding.round, abstract)
                dbutil.mark_funding_tracked(self.db, fid)
                logger_track.info('%s tracked, funding id %s' % (cid, fid))
            except Exception, e:
                logger_track.exception('Failed %s, %s' % (funding.id, e))

    def track_funding(self, cid, track_msg_id, fid, abstract):

        global producer_track
        try:
            producer_track.send_messages("track_message", json.dumps({'id': track_msg_id, 'type': 'track',
                                                                      'topic_id': 3, 'funding_id': fid}))
            feed_back = dbutil.update_company_message(self.db, cid, abstract, 7002, 70, fid)
            if feed_back:
                self.send_company_message_msg(feed_back)
        except FailedPayloadsError, fpe:
            logger_track.exception('Kafka FailedPayloadsError, re-init')
            init_kafka()
            producer_track.send_messages("track_message", json.dumps({'id': track_msg_id, 'type': 'track',
                                                                      'topic_id': 3, 'funding_id': fid}))
            feed_back = dbutil.update_company_message(self.db, cid, abstract, 7002, 70, fid)
            if feed_back:
                self.send_company_message_msg(feed_back)

    def track_funding_for_investor_message(self, cid, fid, iids, funding_round, abstract):

        investor_names = ','.join([dbutil.get_investor_name(self.db, i) for i in iids])
        # 7002
        for iid in iids:
            im = dbutil.update_investor_message(self.db, iid, abstract, 7002, 70, fid, active='Y')
            if im:
                self.send_investor_message_msg(im)
        # 7005 and 7006
        previous_fundings = [funding.id for funding in dbutil.get_company_funding(self.db, cid) if funding.id < fid]
        previous_iids = chain(*[dbutil.get_funding_investor_ids(self.db, funding) for funding in previous_fundings])
        if previous_iids:
            if funding_round == 1110:
                msg = u'%s完成IPO' % dbutil.get_company_name(self.db, cid)
                dimension = 7005
            elif funding_round == 1120:
                msg = u'%s被%s收购' % (dbutil.get_company_name(self.db, cid), investor_names)
                dimension = 7005
            else:
                dimension = 7006
            for iid in previous_iids:
                if dimension == 7006:
                    msg = u'%s已投项目, %s' % (dbutil.get_investor_name(self.db, iid), abstract)
                im = dbutil.update_investor_message(self.db, iid, msg, dimension, 70, fid)
                if im:
                    self.send_investor_message_msg(im)

    def feed(self, cid, today=None):

        global producer_track
        today = datetime.today() if not today else today
        timeperiod = (today-timedelta(hours=self.check_period), today)
        fundings = dbutil.get_company_funding(self.db, cid, timeperiod)
        if not fundings or len(fundings) < 1:
            return

        name = dbutil.get_company_name(self.db, cid)
        abstract = u'%s获得新一轮融资' % name
        funding = self.__process_amount(fundings[0])
        if funding:
            abstract = u'%s, 融资额%s' % (abstract, funding)

        track_msg_id = str(self.mongo.track.track.insert({
            'topic_id': 3,
            'company_id': cid,
            'abstract': abstract,
            'createTime': today
        }))
        producer_track.send_messages("track_message", json.dumps({'id': track_msg_id, 'type': 'track', 'topic_id': 3}))

    def feed_latest(self, period=90):

        global logger_track
        start = datetime.now() - timedelta(days=90)
        for funding in self.db.query('select * from funding where (active is null or active="Y") '
                                     'and createTime>%s;', start):
            pass

    def __process_amount(self, funding):

        if (not funding.investment) or funding.investment == 0:
            return False

        if funding.currency == 3030:
            currency = u'新币'
        elif funding.currency == 3010:
            currency = u'美元'
        else:
            currency = u'人民币'

        if funding.precise == 'Y':
            return u'%s%s' % (funding.investment, currency)
        else:
            level = int(log10(funding.investment))
            if level == 6:
                return u'数十万%s' % currency
            elif level == 7:
                return u'数百万%s' % currency
            elif level == 8:
                return u'数千万%s' % currency
            else:
                return False


def c1():

    global logger_track
    nct = NewsCompanyTracker()
    db = dbcon.connect_torndb()
    for cid in dbutil.get_all_company_id(db):
        nct.feed(cid)
    logger_track.info('tracked')


if __name__ == '__main__':

    print __file__

    if sys.argv[1] == 'c1':
        c1()