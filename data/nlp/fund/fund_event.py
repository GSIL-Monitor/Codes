# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil
from common.chunk import SentenceChunker
from common.feed import NewsFeeder
from news.mentioned import CompanyLinker
from fund_classify import get_fund_classifier

import re
import time
import logging
import pymongo
from itertools import chain
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# logging
logging.getLogger('fund_event').handlers = []
logger_fe = logging.getLogger('fund_event')
logger_fe.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_fe.addHandler(stream_handler)


class NoEventDetectError(Exception):

    def __init__(self):

        Exception.__init__(self)


class FundEvent(object):

    def __init__(self):

        global logger_fe
        self.mongo = dbcon.connect_mongo()
        self.db = dbcon.connect_torndb()

        self.fund_transformer, self.fund_classifier = get_fund_classifier()
        self.company_linker = CompanyLinker()
        self.sentence_chunker = SentenceChunker()
        self.news_feeder = NewsFeeder()

        self.fund_tips = [u'融资', u'投资', u'融资方', u'投资方', u'领投', u'跟投']
        self.round_tips = [u'A轮', u'B轮', u'C轮', u'D轮', u'Pre-A', u'A+轮', u'天使轮', u'天使融资', u'B+轮', u'种子轮',
                           u'战略融资', u'战略性融资', u'战略投资', u'IPO']
        self.amount_tips = [u'数千万', u'数百万', u'数十万', u'上百万', u'上千万', u'上亿', u'几十万', u'几百万', u'几千万',
                            u'百万级', u'千万级', u'亿级',
                            u'\d+\.*\d*万', u'\d+\.*\d*百万', u'\d+\.*\d*千万', u'\d+\.*\d*亿']
        self.currency_tips = [u'人民币', u'美元', u'美金']

        self.company_size = 5
        self.brief_size = 5

        self.life_circle = 50
        self.max_life = 50

        logger_fe.info('Fund event extract model inited')

    def process_all(self):

        global logger_fe
        while True:
            # for record in list(self.mongo.article.news.find({'type': {'$in': [60001, 60005]},
            #                                                  'date': {'$gt': eightmon}})):
            for record in list(self.mongo.article.news.find({'type': {'$in': [60001, 60005]}, 'fund_extract': None})):
            # eh = datetime.utcnow() - timedelta(hours=19)
            # for task in list(self.mongo.task.news.find({"createTime": {"$gt": eh}})):
            #     record = list(self.mongo.article.news.find({'_id': ObjectId(task['news_id'])}))[0]
                if record.get('source', 0) == 13022:
                    self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'fund_extract': -2}})
                    continue
                if record.get('date') and record.get('date') < datetime.now() - timedelta(days=30):
                    self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'fund_extract': -3}})
                    continue
                if self.life_circle <= 0:
                    self.reload_models()
                    logger_fe.info('Model reloaded')
                try:
                    self.process_piece(record['_id'], record)
                    logger_fe.info('%s processed' % record['_id'])
                    self.life_circle -= 1
                except NoEventDetectError, nede:
                    logger_fe.exception('%s not extracted, %s' % (record['_id'], nede))
                    self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'fund_extract': -1}})
                except Exception, e:
                    logger_fe.exception('%s failed, %s' % (record['_id'], e))
            time.sleep(300)
            logger_fe.info('Nice sleep')

    def reload_models(self):

        self.life_circle = self.max_life
        self.company_linker = CompanyLinker()

    def process_piece(self, nid, given_record=None):

        global logger_fe

        record = self.mongo.article.news.find({'_id': nid}).limit(1)[0] if not given_record else given_record
        if record.get('category', 0) == 60101 and \
                ((record.get('category_confidence') is None) or record.get('category_confidence', 0) == 1):
            is_fund = True
        else:
            # is_fund = True
            label = self.fund_classifier.predict(
                self.fund_transformer.transform([' '.join(self.news_feeder.feed(record))]))[0]
            is_fund = True if label == 1 else False
        logger_fe.info('Processing %s, fund %s' % (nid, is_fund))

        if is_fund:
            try:
                results = self.extract_from_contents(**record)
            except TypeError:
                raise NoEventDetectError()
            # results['news_id'] = [str(nid)]
            # results['createTime'] = datetime.now() - timedelta(hours=8)
            # results['news_date'] = record['date']
            # results['processStatus'] = 0
            results['news_id'] = str(nid)
            results['createTime'] = datetime.utcnow()
            results['news_date'] = record['date']
            results['processStatus'] = int(0)
            results['type'] = 'fund'
            results['investorIds'] = []
            results['sectors'] = record.get('sectors', [])
            results['category'] = record.get('category', [])
            # self.mongo.raw.funding.insert_one(results)
            # self.mongo.task.news.insert_one(results)
            self.mongo.task.news.update({'news_id': str(record['_id'])}, results, True)
            self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'fund_extract': 1}})
        else:
            task = self.__generate_news_task(record)
            if task:
                self.mongo.task.news.update({'news_id': str(record['_id'])}, task, True)
            self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'fund_extract': 0}})

    def __generate_news_task(self, record):

        if record.get('type', 0) != 60001:
            return False

        companies = map(lambda y: y[0],
                        sorted(self.company_linker.find_candidates(record).items(), key=lambda x: -x[1]))[:5]
        cids = map(lambda x: int(x), chain(*[dbutil.get_id_from_name(self.db, name) for name in companies]))
        trusted_cid = record.get('companyId', False)
        if trusted_cid and trusted_cid not in cids:
            cids.append(trusted_cid)
        task = {'news_id': str(record['_id']),
                'news_date': record['date'],
                'type': 'check',
                'investorIds': [],
                'companyIds': cids,
                'createTime': datetime.now() - timedelta(hours=8),
                'sectors': record.get('sectors', []),
                'category': record.get('category', []),
                'processStatus': int(0)}
        return task

    def extract_from_contents(self, **kwargs):

        results = {}

        # data with format of a mongodb news record
        data = dict(kwargs)

        # splits all sentences
        contents = [piece.get('content') for piece in data.get('contents') if piece.get('content', '').strip()]
        sentences = list(self.sentence_chunker.chunk(data.get('title'), *contents))
        # find all company candidates
        company_candidates = self.company_linker.find_candidates(data)
        company_re = '|'.join(company_candidates.keys()).replace('.', '\.').replace('*', '\*')\
            .replace('+', '\+').replace('?', '\?').replace('(', '\(').replace(')', '\)')

        # fund event sentences
        event_sentences = [i for i in xrange(len(sentences)) if self.__is_event_sentence(sentences[i])]

        # extract company candidates, fund round, fund amount, fund currency
        for event_index in event_sentences:
            results.setdefault('companyIds', []).extend(
                re.findall(company_re, sentences[event_index]))
            rounds = re.findall('|'.join(self.round_tips), sentences[event_index])
            amounts = re.findall('|'.join(self.amount_tips), sentences[event_index])
            supports = re.findall('|'.join(self.fund_tips), sentences[event_index])
            currency = re.findall('|'.join(self.currency_tips), sentences[event_index])
            support = sum([int(len(item) > 0) for item in [rounds, amounts, currency, supports]])
            if sentences[event_index] in set(item.get('brief') for item in results.get('items', [])):
                continue
            results.setdefault('items', []).append({'brief': sentences[event_index],
                                                    'round': ' '.join(rounds),
                                                    'amount': ' '.join(amounts),
                                                    'currency': ' '.join(currency),
                                                    'sort': support + len(sentences[event_index])/1000.0})

        # add some candidates if needed
        company_found = len(set(results.get('companyIds', [])))
        if company_found < self.company_size:
            results.setdefault('companyIds', []).extend(
                map(lambda y: y[0], sorted(company_candidates.iteritems(),
                    key=lambda x: -x[1])[:(self.company_size-company_found)]))

        # organize
        if results:
            results['companyIds'] = [int(cid) for cid in set(chain(*[dbutil.get_id_from_name(self.db, name)
                                                                     for name in set(results.get('companyIds', []))
                                                                     if name.strip()]))]
            results['items'] = sorted(results.get('items'),
                                      key=lambda x: x.get('sort', 0), reverse=True)[:self.brief_size]

        return results

    def __is_event_sentence(self, sentence):

        for fund_tip in self.fund_tips:
            if fund_tip in sentence:
                return True
        for round_tip in self.round_tips:
            if round_tip in sentence:
                return True
        return False

if __name__ == '__main__':

    print __file__

    fe = FundEvent()
    fe.process_all()
    # fe.process_piece(ObjectId('57ce684d4877af20e02b12a6'))