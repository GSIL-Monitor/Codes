# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from fundtag import FundingClassifier
from common import dbutil, dicts
from common.chunk import SentenceChunker
from common.feed import NewsFeeder
from common.dsutil import FrozenLenList
from news.mentioned import CompanyLinker
from task.news_postprocess import NewsTagger
from score.similar_news import ScorerNews

import re
import time
import codecs
import logging
import pymongo
from copy import copy
from itertools import chain
from collections import Counter
from datetime import datetime, timedelta

import fasttext

# logging
logging.getLogger('task_news').handlers = []
logger_tn = logging.getLogger('task_news')
logger_tn.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_tn.addHandler(stream_handler)


viptag_model = os.path.join(os.path.split(os.path.realpath(__file__))[0], '../keywords/models/20180319.bin')


class NoEventDetectError(Exception):

    def __init__(self):

        Exception.__init__(self)


class NewsTask(object):

    def __init__(self):

        global logger_tn, viptag_model
        self.mongo = dbcon.connect_mongo()
        self.db = dbcon.connect_torndb()

        # self.fund_transformer, self.fund_classifier = get_fund_classifier()
        self.funding_clf = FundingClassifier()
        self.company_linker = CompanyLinker()
        self.sentence_chunker = SentenceChunker()
        self.snscorer = ScorerNews()
        self.news_feeder = NewsFeeder()
        self.news_tagger = NewsTagger()
        self.viptag_clf = fasttext.load_model(viptag_model)
        self.tags_l2 = dicts.get_vip_succession()
        self.trusted_fund_source = [13800]
        self.non_trusted_fund_source = [13848, 13866]
        self.important_sources = dicts.get_important_news_source()
        self.tags = self.load_tags()

        category_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'files/category')
        self.categories = {int(line.split('#')[0]): line.strip().split('#')[1].split(',')
                           for line in codecs.open(category_file, encoding='utf-8') if not line.startswith('#')}

        self.fund_tips = [u'融资', u'融资方', u'领投', u'跟投']
        self.fund_keywords = [u'融资', u'融资方', u'领投', u'跟投', u'投资', u'收购']
        self.round_tips = [u'A轮', u'B轮', u'C轮', u'D轮', u'Pre-A', u'A+轮', u'天使轮', u'天使融资', u'B+轮', u'种子轮',
                           u'战略性融资', u'战略投资', u'IPO']
        self.amount_tips = [u'数千万', u'数百万', u'数十万', u'上百万', u'上千万', u'上亿', u'几十万', u'几百万', u'几千万',
                            u'百万级', u'千万级', u'亿级',
                            u'\d+\.*\d*万', u'\d+\.*\d*百万', u'\d+\.*\d*千万', u'\d+\.*\d*亿']
        self.currency_tips = [u'人民币', u'美元', u'美金']

        self.company_size = 5
        self.brief_size = 5
        self.tags_l2_min_appearance = 3

        self.life_circle = 25
        self.max_life = 100

        self.latest_funding_companies = FrozenLenList(200)
        self.date_3_days_ago = datetime.utcnow() - timedelta(days=3)

        logger_tn.info('Fund event extract model inited')

    def process_all(self):

        global logger_tn
        while True:
            for record in list(self.mongo.article.news.find({'type': {'$in': [60001, 60003, 60005, 60006,
                                                                              60007, 60008, 60009]},
                                                             'fund_extract': None}).sort('createTime',
                                                                                         pymongo.DESCENDING)):
                if record.get('source', 0) == 13022:
                    self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'fund_extract': -2}})
                    continue
                if record.get('date') and record.get('date') < datetime.now() - timedelta(days=7):
                    self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'fund_extract': -3}})
                    continue
                if self.life_circle <= 0:
                    self.reload_models()
                    logger_tn.info('Model reloaded')
                try:
                    logger_tn.info('Processing, %s' % record['_id'])
                    self.process_piece(record['_id'], record)
                    logger_tn.info('%s processed' % record['_id'])
                    self.life_circle -= 1
                except NoEventDetectError, nede:
                    logger_tn.exception('%s not extracted, %s' % (record['_id'], nede))
                    self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'fund_extract': -1}})
                except Exception, e:
                    logger_tn.exception('%s failed, %s' % (record['_id'], e))
            time.sleep(300)
            logger_tn.info('Nice sleep')

    def load_tags(self):

        global logger_tn
        try:
            tags = {dbutil.get_tag_info(self.db, tid, 'name'): tid for tid in dbutil.get_industry_tags(self.db) if tid}
            logger_tn.info('Tags: %s' % ','.join(tags.keys()))
        except Exception, e:
            tags = {}
            logger_tn.exception('Fail to load tags, due to %s' % e)
        return tags

    def reload_models(self):

        self.life_circle = self.max_life
        self.company_linker = CompanyLinker()
        self.tags = self.load_tags()

        self.date_3_days_ago = datetime.utcnow() - timedelta(days=3)
        for funding in dbutil.get_funding_by_date(self.db, (self.date_3_days_ago, datetime.now())):
            if funding and funding.companyId:
                self.latest_funding_companies.append(funding.companyId)

    def process_piece(self, nid, given_record=None):

        global logger_tn

        record = self.mongo.article.news.find({'_id': nid}).limit(1)[0] if not given_record else given_record

        # generate report task
        if record.get('type', 0) == 60006:
            task = {
                'news_id': record['_id'],
                'news_date': record['date'],
                'type': 'report',
                'createTime': datetime.utcnow(),
                'processStatus': int(0)
            }
            self.mongo.task.news.update({'news_id': str(record['_id'])}, task, True)
            self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'fund_extract': 0}})
            return

        # fund classify
        if record.get('category', 0) == 60101 and \
                ((record.get('category_confidence') is None) or record.get('category_confidence', 0) == 1):
            is_fund, strict = True, False
        elif record.get('source', 0) in self.non_trusted_fund_source:
            is_fund, strict = False, True
        elif record.get('source', 0) in self.trusted_fund_source:
            is_fund, strict = True, False
        else:
            # label = self.fund_classifier.predict(
            #     self.fund_transformer.transform([' '.join(self.news_feeder.feed(record))]))[0]
            label = self.funding_clf.predict(record)
            is_fund = True if label == 1 else False
            strict = True
        is_fund_before_review = copy(is_fund)
        is_fund = self.__review_fund(is_fund, record, strict)
        logger_tn.info('Processing %s, fund %s, before review %s' % (nid, is_fund, is_fund_before_review))

        # task base
        if is_fund:
            task = self.__generate_fund_task(record)
            self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'fund_extract': 1}})
        else:
            task = self.__generate_news_task(record)
            if not task:
                self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'fund_extract': -6,
                                                                                 "processStatus": -7}})
                logger_tn.info('Classify as buyao news, %s' % nid)
                return
            self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'fund_extract': 0}})
        task['categories'] = self.classify_category(record, task.get('categories', []))
        # tags
        tags = []
        tags.extend(self.classify_tags(record))
        # sectors
        try:
            tags.extend(self.classify_sector_tags(record, task.get('categories')))
        except Exception, e:
            logger_tn.exception('Fail to classify sector for %s' % record['_id'])
        task['newsTags'] = tags
        # sentiment
        task['sentiment'] = 578361
        # investorIds
        task['investorIds'] = []
        # dups company ids
        task['companyIds_139'] = copy(task.get('companyIds'))

        self.mongo.task.news.update({'news_id': str(record['_id'])}, task, True)
        self.news_tagger.label_11800_record(record, record['_id'])

        # relevant news
        # relevant = self.snscorer.get_similar_news(nid)
        # relevant = [str(task['_id'])
        #             for task in [self.mongo.task.news.find_one({'news_id': str(r)}) for r in relevant] if task]
        # if relevant:
        #     self_id = str(self.mongo.task.news.find_one({'news_id': str(record['_id'])})['_id'])
        #     relevant.append(self_id)
        #     for tnid in set(relevant):
        #         my_relevant = set(relevant)
        #         my_relevant.remove(tnid)
        #         self.mongo.task.news.update({'_id': ObjectId(tnid)}, {'$set': {'relevant': list(my_relevant)}})

    def __review_fund(self, is_fund, record, strict):

        if not is_fund:
            return is_fund
        if not strict:
            return is_fund
        # other non fund source
        if record.get('source', 0) not in self.trusted_fund_source:
            try:
                task = self.extract_funding_from_contents(**record)
                if task and task.get('items'):
                    return True
                return False
            except TypeError:
                return False
        return is_fund

    def __generate_fund_task(self, record):

        try:
            task = self.extract_funding_from_contents(**record)
        except TypeError:
            task = {}
        task['news_id'] = str(record['_id'])
        task['news_date'] = record['date']
        task['createTime'] = datetime.utcnow()
        task['processStatus'] = int(0)
        task['type'] = 'fund'
        task['categories'] = [578349]
        task['section'] = 'step1'
        task['subtype'] = self.classify_fund_subtype(task)
        return task

    def __generate_news_task(self, record):

        # no need to have
        if record.get('type', 60008) == 60008:
            return False
        # from weixin, needed by topic
        if self.news_tagger.label_11800_record(record, record['_id']) \
                or self.news_tagger.label_11810_record(record, record['_id']):
            return {'news_id': str(record['_id']),
                    'news_date': record['date'],
                    'type': 'important',
                    'createTime': datetime.utcnow(),
                    'processStatus': int(0),
                    'section': 'step1'}

        # check source
        if record.get('source') in self.important_sources:
            news_important = True
        else:
            news_important = False
        # extract companies from news
        companies = map(lambda y: y[0],
                        sorted(dict(self.company_linker.find_from_record(record)).items(), key=lambda x: -x[1]))[:3]
        cids = map(lambda x: int(x), chain(*[dbutil.get_id_from_name(self.db, name) for name in companies]))
        trusted_cid = record.get('companyId', False)
        if trusted_cid and trusted_cid not in cids:
            cids.append(trusted_cid)

        if not (cids or news_important):
            return False

        task_type = 'important' if news_important else 'check'
        task = {'news_id': str(record['_id']),
                'news_date': record['date'],
                'type': task_type,
                'companyIds': cids,
                'createTime': datetime.utcnow(),
                'processStatus': int(0),
                'section': 'step1'}
        return task

    def classify_category(self, record, prejudgement):

        results = prejudgement
        # 汇总类新闻
        if u'日报' in record['title'] or u'周报' in record['title']:
                return [578358]

        for cate_id, category in self.categories.items():
            if len(category) == 1:
                if category[0] in (set(record.get('categoryNames', [])) | set(record.get('original_tags', []) or [])):
                    results.append(int(cate_id))
            else:
                if set(self.news_feeder.feed(record)) & set(category):
                    results.append(int(cate_id))
        if len(results) > 0:
            result = [results[0]]
        return list(set(int(result) for result in results)) if results else [578359]

    def classify_tags(self, record):

        news_content = ' '.join([c.get('content', '') for c in record.get('contents')])
        for tag, tid in self.tags.items():
            if news_content.count(tag) > 5 or (float(news_content.count(tag)) / len(news_content) > 0.005):
                yield tid

    def classify_sector_tags(self, record, categories):

        desc = ' '.join(self.news_feeder.feed(record))
        if desc and len(desc) > 20:
            classifier_vips = {int(tag.replace(u'__label__', '')): weight for (tag, weight) in
                               self.viptag_clf.predict_proba([desc], 2)[0]}
            if max(classifier_vips.values()) < 0.25:
                sectors = [(999, 0)]
            elif max(classifier_vips.values()) - min(classifier_vips.values()) < 0.15:
                sectors = [(dbutil.get_sector_from_tag(self.db, tid), confidence)
                           for (tid, confidence) in sorted(classifier_vips.iteritems(), key=lambda x: -x[1])]
            else:
                sectors = [(dbutil.get_sector_from_tag(self.db, tid), confidence)
                           for (tid, confidence) in sorted(classifier_vips.iteritems(), key=lambda x: -x[1])]
                sectors = [sectors[0]]
        else:
            sectors = [(999, 0)]
        sids = [sid for (sid, _) in sectors]
        if 7 in sids and u'区块链' in desc and 20006 not in sids:
            sids.remove(7)
            sids.append(20006)
            confidences = []
        else:
            confidences = [confidence for (_, confidence) in sectors]
        tags = [dbutil.get_tag_from_sector(self.db, sid) for sid in sids]
        tags = [t for t in tags if t]
        if {128, 578353, 578349, 578351, 578356, 578351} & set(categories):
            self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'sectors': sids,
                                                                             'features': tags,
                                                                             'sector_confidence': confidences}})
        return tags

    def extract_funding_from_contents(self, **kwargs):

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
        try:
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
        except Exception, e:
            pass
        if self.__is_event_title(data.get('title', '')):
            results.setdefault('items', []).append({'brief': data.get('title'),
                                                    'sort': 1})

        # organize
        if results:
            results['companyIds'] = [int(cid) for cid in set(chain(*[dbutil.get_id_from_name(self.db, name)
                                                                     for name in set(results.get('companyIds', []))
                                                                     if name.strip()]))]
            results['items'] = sorted(results.get('items'),
                                      key=lambda x: x.get('sort', 0), reverse=True)[:self.brief_size]

        return results

    def classify_fund_subtype(self, task):

        company_candidates = task.get('companyIds', [])
        if set(company_candidates) & set(self.latest_funding_companies):
            subtype = 'duplicate'
        elif self.mongo.task.news.find({'companyIds': {'$in': company_candidates}, 'processStatus': 1, 'type': 'fund',
                                        'news_date': {'$gt': self.date_3_days_ago}}).count() > 0:
            subtype = 'duplicate'
        else:
            subtype = 'major'
        return subtype

    def __is_event_sentence(self, sentence):

        for fund_tip in self.fund_tips:
            if fund_tip in sentence:
                return True
        for round_tip in self.round_tips:
            if round_tip in sentence:
                return True
        return False

    def __is_event_title(self, sentence):

        for fund_keyword in self.fund_keywords:
            if fund_keyword in sentence:
                return True
        return False


if __name__ == '__main__':

    print __file__

    logger_tn.info('News Task Model Initing')
    nt = NewsTask()
    logger_tn.info('News Task Model Inited')
    nt.process_all()
    # fe.process_piece(ObjectId('57ce684d4877af20e02b12a6'))
