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
import config as tsbconfig
from common import dbutil
from common.algorithm import infix2prefix
from templates import generate_rule_based_query

import logging
import json
import pymongo
from abc import abstractmethod
from bson.objectid import ObjectId
from itertools import chain
from collections import Counter
from datetime import datetime, timedelta

from kafka import KafkaClient, SimpleProducer
from kafka.errors import FailedPayloadsError

producer_track = None

# logging
logging.getLogger('track').handlers = []
logger_track = logging.getLogger('track')
logger_track.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_track.addHandler(stream_handler)


def init_kafka():

    global producer_track

    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    producer_track = SimpleProducer(kafka)


class CompanyTracker(object):

    def __init__(self):

        global producer_track
        init_kafka()
        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        self.news_timeliness = 7

    @abstractmethod
    def feed(self, cid):
        pass

    def send_company_message_msg(self, mid):

        global producer_track
        try:
            producer_track.send_messages("track_message_v2",
                                         json.dumps({'id': mid, 'type': 'company_message', 'action': 'create'}))
            producer_track.send_messages("task_company",
                                         json.dumps({'source': 'track_company',
                                                     'id': dbutil.get_id_from_company_message(self.db, mid),
                                                     'detail': mid,
                                                     'posting_time': datetime.now().strftime('%Y-%m-%d:%H:%M:%S')}))
        except FailedPayloadsError, fpe:
            init_kafka()
            producer_track.send_messages("track_message_v2",
                                         json.dumps({'id': mid, 'type': 'company_message', 'action': 'create'}))
            producer_track.send_messages("task_company",
                                         json.dumps({'source': 'track_company',
                                                     'id': dbutil.get_id_from_company_message(self.db, mid),
                                                     'detail': mid,
                                                     'posting_time': datetime.now().strftime('%Y-%m-%d:%H:%M:%S')}))

    def send_investor_message_msg(self, mid):

        global producer_track
        try:
            producer_track.send_messages("track_message_v2",
                                         json.dumps({'id': mid, 'type': 'investor_message', 'action': 'create'}))
        except FailedPayloadsError, fpe:
            init_kafka()
            producer_track.send_messages("track_message_v2",
                                         json.dumps({'id': mid, 'type': 'investor_message', 'action': 'create'}))

    def send_topic_company_msg(self, cid, visible=True):

        global producer_track
        try:
            producer_track.send_messages("aggregator_v2",
                                         json.dumps({'id': cid, 'action': 'create', 'visible': visible}))
            producer_track.send_messages("task_company",
                                         json.dumps({'source': 'track_topic', 'id': cid, 'from': 'auto publish topic',
                                                     'posting_time': datetime.now().strftime('%Y-%m-%d:%H:%M:%S')}))
        except FailedPayloadsError, fpe:
            init_kafka()
            producer_track.send_messages("aggregator_v2",
                                         json.dumps({'id': cid, 'action': 'create', 'visible': visible}))
            producer_track.send_messages("task_company",
                                         json.dumps({'source': 'track_topic', 'id': cid, 'from': 'auto publish topic',
                                                     'posting_time': datetime.now().strftime('%Y-%m-%d:%H:%M:%S')}))

    def send_msg(self, topic, msg):

        global producer_track
        try:
            producer_track.send_messages(topic, msg)
        except FailedPayloadsError, fpe:
            init_kafka()
            producer_track.send_messages(topic, msg)

    def normalize_artifact_name(self, aname):

        return aname.replace(u'–', u'-').replace(u'－', u'-').replace(u'——', u'-').split(u'-')[0].strip()


class TopicTracker(object):

    def __init__(self):

        global logger_track

        self.news_timeliness = 7

        logger_track.info('Topic Tracker initing')
        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        self.topics_company = list(self.load_topics(1))
        self.topics_news = list(self.load_topics(2))
        init_kafka()
        logger_track.info('Topic Tracker inited, with %s general news trackers' % len(self.topics_news))
        logger_track.info('Topic Tracker inited, with %s general company trackers' % len(self.topics_company))

    def load_topics(self, topic_type):

        for tpid, auto_publish in dbutil.get_general_topics(self.db):
            dbutil.update_last_message_time(self.db, tpid)
            gtt = GeneralTrackTopic(tpid, auto_publish)
            if (gtt.get_topic_type() == topic_type) and gtt.valid():
                yield gtt

    def reload_topics(self):

        logger_track.info('Topic Tracker reloading, with %s general news trackers' % len(self.topics_news))
        logger_track.info('Topic Tracker reloading, with %s general company trackers' % len(self.topics_company))
        self.topics_company = list(self.load_topics(1))
        self.topics_news = list(self.load_topics(2))

    def fit_company_id(self, cid):

        for gtt in self.topics_company:
            # logger_track.info(gtt.tpid)
            yield gtt.tpid, gtt.fit_company(cid)

    def fit_news_id(self, nid):

        record = list(self.mongo.article.news.find({'_id': ObjectId(nid)}))[0]
        result = self.fit_news(record)
        return result if result else {'processed': 'old news'}

    def fit_news(self, record):

        if record.get('date') and record['date'] < (datetime.now()-timedelta(days=self.news_timeliness)):
            return
        for gtt in self.topics_news:
            yield gtt.tpid, gtt.fit_news(record)

    def fit_latest(self, hours=168, max_count=500):

        start = datetime.now() - timedelta(hours=hours)
        for task in list(self.mongo.task.news.find(
                {"processStatus": 1,
                 "createTime": {"$gt": start}}).sort("createTime", pymongo.DESCENDING).limit(max_count)):
            self.fit_news(list(self.mongo.article.news.find({'_id': ObjectId(task['news_id'])}))[0])


class GeneralTrackTopic(object):

    def __init__(self, tpid, auto_publish="P"):

        self.db = dbcon.connect_torndb()

        self.tpid = tpid
        self.features = self.__get_features()
        self.searches = self.__get_search_terms()
        self.topic_type = self.__classify_type()

        self.auto_publish = 'Y' if auto_publish == 'Y' else 'P'

    def __get_features(self):

        return dbutil.get_topic_dimension_tags(self.db, self.tpid)

    def __get_search_terms(self):

        return dbutil.get_topic_search_terms(self.db, self.tpid)

    def __classify_type(self):

        """
        type == 1: company oriented message
        type == 2: news oriented message
        """
        if self.searches:
            return 2
        if self.features and max(self.features.keys()) < 11500:
            return 1
        return 2

    def valid(self):

        if not (self.features or self.searches):
            return False
        return True

    def get_topic_type(self):

        return self.topic_type

    def fit_company(self, cid):

        global producer_track, logger_track
        company_features = set(dbutil.get_company_feature_tags(self.db, cid))
        # logger_track.info(company_features)
        # logger_track.info(self.features.values())
        for k, v in self.features.items():
            if not (set(v) & company_features):
                return False
        features_used = list(chain(*[tids for tids in self.features.values()]))
        # for detailid
        comment = dbutil.get_company_tags_comment(self.db, cid, features_used)
        if comment:
            tpmid = dbutil.update_topic_message(self.db, self.tpid, comment.get('message'), self.auto_publish,
                                                comment.get('relate_type'), comment.get('relate_id'),
                                                comment.get('detail_id'), comment.get('comments'))
            tpcid = dbutil.update_topic_company(self.db, self.tpid, cid, self.auto_publish)
        else:
            tpmid = dbutil.update_topic_message(self.db, self.tpid, u'添加了一家新公司', self.auto_publish, 60, cid)
            tpcid = dbutil.update_topic_company(self.db, self.tpid, cid, self.auto_publish)

        logger_track.info('%s seem to meet requirements, tpm %s, tpc %s, topic %s' % (cid, tpmid, tpcid, self.tpid))
        if tpmid:
            self.send_track_msg(tpmid, 'topic_message')
            if tpcid:
                self.send_track_msg(tpcid, 'topic_company')
                self.send_msg('task_company', json.dumps({'source': 'track_topic', 'id': cid,
                                                          'detail': tpcid, 'from': 'nlp'}))
            dbutil.update_topic_message_company(self.db, tpmid, tpcid)

        return True

    def fit_news(self, record):

        global producer_track, logger_track
        if record.get('processStatus', 0) != 1:
            return False
        news_features = set(record.get('features', set()))
        company_features = set(chain(*[dbutil.get_company_feature_tags(self.db, cid)
                                       for cid in record.get('companyIds')]))
        if not news_features:
            return False
        for k, v in self.features.items():
            if k >= 11500 and not (set(v) & news_features):
                return False
            if k < 11500 and not ((set(v) & company_features) or (set(v) & news_features)):
                return False

        # search dimension
        if self.searches:
            contents = ' '.join([item.get('content', '') for item in record.get('contents', [])])
            for term in self.searches:
                if term not in contents:
                    return False

        # update topic message
        tpmsg = dbutil.update_topic_message(self.db, self.tpid, record.get('title', ''),
                                            self.auto_publish, 10, record['_id'])
        # update topic message, topic company, send msg
        # if tpmsg and self.auto_publish == 'Y':
        if tpmsg:
            msg = {
                'type': 'topic_message',
                'id': tpmsg,
                'action': 'create',
                'from': 'nlp'
            }
            self.send_msg("track_message_v2", json.dumps(msg))
            # update topic company and send msg
            for cid in record.get('companyIds', []):
                tpc = dbutil.update_topic_company(self.db, self.tpid, cid, self.auto_publish)
                # if tpc and self.auto_publish == 'Y':
                if tpc:
                    msg = {
                        'type': 'topic_company',
                        'id': tpc,
                        'action': 'create',
                        'from': 'nlp'
                    }
                    # relate topic company and message
                    dbutil.update_topic_message_company(self.db, tpmsg, tpc)
                    self.send_msg("track_message_v2", json.dumps(msg))
                    self.send_msg('task_company', json.dumps({'source': 'track_topic', 'id': cid, 'detail': tpc}))
        return True

    def send_msg(self, topic, msg):

        global producer_track, logger_track
        try:
            producer_track.send_messages(topic, msg)
        except FailedPayloadsError, fpe:
            logger_track.exception('Kafka Payload Error, re-init')
            init_kafka()
            producer_track.send_messages(topic, msg)

    def send_track_msg(self, mid, m_type):

        msg = json.dumps({'id': mid, 'type': m_type, 'action': 'create', 'from': 'nlp'})
        self.send_msg('track_message_v2', msg)


class CompanyOrientedTopic(object):

    def __init__(self, tpid):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        self.tpid = tpid
        self.features = self.__get_features()
        self.tags = dbutil.get_topic_relevant_tags(self.db, self.tpid)
        topic_info = dbutil.get_topic_info(self.db, self.tpid)
        self.auto_expand = topic_info.autoExpand
        self.rules = self.__parse_topic_rule(topic_info.rule)

    def __get_features(self):

        return {k: v for k, v in dbutil.get_topic_dimension_tags(self.db, self.tpid).items() if k < 11500}

    def __parse_topic_rule(self, rule):

        if rule:
            rule = rule.replace(u'，', u',').replace(u'（', u'(').replace(u'）', u')').replace(u' ', u'').lower()
            if rule:
                return generate_rule_based_query(rule)
            return False
        else:
            return False

    def fit(self, client):

        if self.rules:
            codes = client.search('topic', query=self.rules).get('company', {}).get('data', [])
            if codes:
                codes.reverse()
                for code in codes:
                    flag = True
                    cid = self.db.get('select id from company where code=%s', code).id
                    company_features = set(dbutil.get_company_feature_tags(self.db, cid))
                    for k, v in self.features.items():
                        if not (set(v) & company_features):
                            flag = False
                            break
                    if flag:
                        dbutil.update_topic_company(self.db, self.tpid, cid)
        if self.auto_expand:
            self.expand()

    def fit_news(self):

        pass

    def fit_tags(self):

        # check_point = datetime.now() - timedelta(hours=2)
        for tpc in dbutil.get_topic_companies(self.db, self.tpid):
            for tid in self.tags:
                dbutil.update_company_tag(self.db, tpc.companyId, tid, 1.502)

    def fit_comps(self):

        companies = [c.companyId for c in dbutil.get_topic_companies(self.db, self.tpid)]
        for cid in companies:
            self.mongo.comps.candidates.update({'company': cid},
                                               {'$addToSet': {'candidates': {'$each': [(company, 0.5)
                                                                                       for company in companies
                                                                                       if cid != company]}}})

    def expand(self):

        companies = set([c.companyId for c in dbutil.get_topic_companies(self.db, self.tpid)])
        if len(companies) < 5:
            return
        candidates = [comps.get('candidates', [])
                      for comps in self.mongo.comps.candidates.find({'company': {'$in': list(companies)}})]
        candidates = map(lambda x: x[0], chain(*candidates))
        candidates = Counter([cid for cid in candidates if cid not in companies])
        comps = Counter([cid for cid in chain(*[dbutil.get_company_comps(self.db, cid) for cid in companies])
                         if cid not in companies])
        for comp in comps.most_common(min(len(companies)/2, 50)):
            if comp[1] > len(companies)/5:
                dbutil.update_topic_company(self.db, self.tpid, comp[0], confidence=0.51)
        for candidate in candidates.most_common(min(len(companies)/5, 30)):
            if candidate[1] > len(companies)*0.6:
                dbutil.update_topic_company(self.db, self.tpid, candidate[0], confidence=0.51)


class Industry(object):

    def __init__(self, idid):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        self.idid = idid
        self.tag = dbutil.get_industry_tag(self.db, self.idid)
        industry_info = dbutil.get_industry_info(self.db, self.idid)
        self.auto_expand = (industry_info.autoExpand == 'Y')
        self.company_rules = self.__parse_company_rule(industry_info.rule4company)

    def __parse_company_rule(self, rule):

        if rule:
            rule = rule.replace(u'，', u',').replace(u'（', u'(').replace(u'）', u')').replace(u' ', u'').lower()
            if rule:
                return generate_rule_based_query(rule)
            return False
        else:
            return False

    def fit_company(self, client):

        if self.tag:
            for cid, verify, modify in dbutil.get_company_from_tag(self.db, self.tag, with_verify=True):
                # active = 'Y' if (verify and verify == 'Y') else 'P'
                active = 'P'
                modify = modify if active == 'Y' else 139
                dbutil.update_industry_company(self.db, self.idid, cid, active=active, source='tag', modify=modify)
        if self.company_rules:
            codes = client.search('topic', query=self.company_rules).get('company', {}).get('data', [])
            if codes:
                codes.reverse()
                for code in codes:
                    cid = dbutil.get_id_from_code(self.db, code)
                    dbutil.update_industry_company(self.db, self.idid, cid, source='rule')
        if self.auto_expand:
            self.expand()

    def fit_news(self):

        companies = [c.companyId for c in dbutil.get_industry_companies(self.db, self.idid)]
        for news in self.mongo.article.news.find(
                {'processStatus': 1, 'companyIds': {'$in': companies}}).sort('_id', pymongo.DESCENDING).limit(300):
            try:
                news_date = news['date']+timedelta(hours=8)
            except:
                news_date = None
            dbutil.update_industry_news(self.db, self.idid, str(news['_id']), 'Y', news_date)
        if self.tag:
            for news in self.mongo.article.news.find(
                    {'processStatus': 1, 'features': self.tag}).sort('_id', pymongo.DESCENDING).limit(50):
                try:
                    news_date = news['date']+timedelta(hours=8)
                except:
                    news_date = None
                dbutil.update_industry_news(self.db, self.idid, str(news['_id']), 'Y', news_date)
        # clear invalid news
        news2check = dbutil.get_industry_news(self.db, self.idid)
        valid = self.mongo.article.news.find({'_id': {'$in': [ObjectId(nid) for nid in news2check]}, 'processStatus': 1,
                                              '$or': [{'companyIds': {'$in': companies}}, {'features': self.tag}]})
        valid = [str(record['_id']) for record in valid]
        for invalid in (set(news2check) - set(valid)):
            dbutil.update_industry_news(self.db, self.idid, invalid, 'P')

    def fit_tag(self):

        # update tag type
        if self.tag:
            original_type = dbutil.get_tag_info(self.db, self.tag, 'type')
            if original_type and original_type < 11011:
                dbutil.update_tag_type(self.db, self.tag, 11011, with_tag_id=True)
        # update company tag
        for tpc in dbutil.get_industry_companies(self.db, self.idid):
            if self.tag:
                dbutil.update_company_tag(self.db, tpc.companyId, self.tag, 1.502, verify='P')

    def fit_comps(self):

        companies = [c.companyId for c in dbutil.get_industry_companies(self.db, self.idid)]
        for cid in companies:
            self.mongo.comps.candidates.update({'company': cid},
                                               {'$addToSet': {'candidates': {'$each': [(company, 1)
                                                                                       for company in companies
                                                                                       if cid != company]}}})

    def expand(self):

        companies = set([c.companyId for c in dbutil.get_industry_companies(self.db, self.idid)])
        if len(companies) < 5:
            return
        candidates = [comps.get('candidates', [])
                      for comps in self.mongo.comps.candidates.find({'company': {'$in': list(companies)}})]
        candidates = map(lambda x: x[0], chain(*candidates))
        candidates = Counter([cid for cid in candidates if cid not in companies])
        comps = Counter([cid for cid in chain(*[dbutil.get_company_comps(self.db, cid) for cid in companies])
                         if cid not in companies])
        for comp in comps.most_common(min(len(companies)/2, 50)):
            if comp[1] > len(companies)/5:
                dbutil.update_industry_company(self.db, self.idid, comp[0], confidence=0.51, source='expand')
        for candidate in candidates.most_common(min(len(companies)/5, 30)):
            if candidate[1] > len(companies)*0.6:
                dbutil.update_industry_company(self.db, self.idid, candidate[0], confidence=0.51, source='expand')


if __name__ == '__main__':

    industry = Industry(260)
    industry.fit_news()