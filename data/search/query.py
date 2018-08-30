# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

from datetime import datetime, timedelta
from itertools import chain

import db as dbcon
import templates
from searchutil import NameSegmenter
from nlp.common import dbutil
from nlp.common.functions import is_engish_word
from nlp.common.zhtools.segment import Segmenter
from nlp.common.zhtools.postagger import Tagger
from nlp.common import dicts
from nlp.common.zhtools import stopword

# config
collection_ranking_threshold = 0.25


class Query(object):

    tagger = Tagger(tags=True)
    yellows = dicts.get_yellow_tags_name()

    def __init__(self, query):

        self.query = query
        self.intent = None
        db = dbcon.connect_torndb()
        self.en_tags = [t.name for t in dbutil.get_tags_by_type(db) if is_engish_word(t.name)]
        db.close()

    def __intent_classify(self):

        if not self.query.strip():
            self.intent = 'empty'
            return self.query

        if self.query in self.yellows:
            self.intent = 'yellow'
            return self.query

        # 英文直接处理
        if self.query.replace(' ', '').replace('+', '').replace('-', '').encode('utf-8').isalnum():
            if self.query in self.en_tags:
                self.intent = 'tag'
                return [self.query.lower().replace(' ', '')]
            postags = [item[1] for item in self.tagger.tag(self.query) if item[0].strip()]
            if len(postags) == 1 and postags[0] == 'tag':
                self.intent = 'tag'
                return [self.query.lower().replace(' ', '')]
            else:
                self.intent = 'general'
                self.query = self.query.lower().replace(' ', '')
                return self.query

        query = [item for item in self.tagger.tag(self.query) if item[0].strip()]
        postags = [x[1] for x in query]
        tagratio = float(postags.count('tag') + postags.count('itag'))/len(query)
        if tagratio > 0.6 or (len(self.query) > 5 and tagratio > 0.5):
            self.intent = 'tag'
            return [x[0].lower() for x in query]
        else:
            self.intent = 'general'
            self.query = self.query.lower().replace(' ', '')
            return self.query

    def extend_query(self, es_query):

        query = self.__intent_classify()
        print 'intent', self.intent
        print 'query', query

        if self.intent == 'yellow':
            es_query.setdefault('bool', {}).setdefault('should', []).append(templates.get_term('tags', query, boost=5))
            return es_query
        elif self.intent == 'tag':
            # es_query.setdefault('bool', {}).setdefault('should', []).append(templates.get_term('name', ''.join(query),
            #                                                                                    boost=50))
            es_query.setdefault('bool', {}).setdefault('should', []).append(templates.get_keyword_template(*query))
            # es_query["bool"]["should"].append(templates.get_fuzzy('name', ''.join(query), boost=10))
            es_query["bool"]["minimum_number_should_match"] = 1
            # for tag in query:
            #     es_query.setdefault('bool', {}).setdefault('should', []).append(
            #         templates.get_term('description', tag, 0.5))
            # print es_query
            return es_query
        elif self.intent == 'general':
            es_query["bool"]["should"].append(templates.get_fuzzy('name', query, boost=50))
            es_query["bool"]["should"].append(templates.get_fuzzy('alias', query))
            es_query["bool"]["should"].append(templates.get_term('description', query))
            es_query["bool"]["should"].append(templates.get_term('tags', query, boost=5))
            es_query["bool"]["minimum_number_should_match"] = 1
            # print es_query
            return es_query
        elif self.intent == 'empty':
            return es_query


class UniversalQuery(object):

    db = dbcon.connect_torndb()
    reload_control = 0
    en_tags = set([t.name.lower() for t in dbutil.get_tags_by_type(db) if is_engish_word(t.name)])
    tags = set([t.lower() for t in dbutil.get_searchable_tags(db)])
    db.close()

    def __init__(self, input, filters, nested=None):

        self.input = input if isinstance(input, dict) else input.lower().strip()
        self.filters = filters
        self.nested = nested

        self.intent = None
        self.query = None

        self.reload_tags()

    def __intent_classify(self):

        # 空搜索
        if not self.input.strip():
            self.intent = 'empty'
            return
        # 英文直接处理
        if self.input.replace(' ', '').replace('+', '').replace('-', '').encode('utf-8').isalnum():
            if self.input.lower() in self.en_tags:
                self.intent = 'tag'
                self.query = self.query = {'or': [self.input.strip().lower().replace(' ', '')]}
                return
            else:
                self.intent = 'general'
                self.input = self.input.strip().lower()
                self.query = self.input
            return
        words = self.input.split(' ')
        if [w.lower().strip() in self.tags for w in words].count(False) == 0:
            self.intent = 'tag'
            self.query = {'or': [word.strip().lower() for word in words]}
        else:
            self.intent = 'general'
            self.query = self.input.strip().lower()
            return

    def generate_query(self):

        self.__intent_classify()
        query = {}
        if self.intent == 'tag':
            for tag in self.query.get('and', []):
                query.setdefault('bool', {}).setdefault('must', []).append(templates.get_terms('tags', [tag.lower()]))
                # query.setdefault('bool', {}).setdefault('must', []).append(templates.get_tag_template(tag))
            for tag in self.query.get('or', []):
                query.setdefault('bool', {}).setdefault('should',
                                                        []).extend(templates.get_fast_tag_template(tag.lower()))
            if self.query.get('or'):
                query['bool']['minimum_number_should_match'] = 1
            for tag in self.query.get('not', []):
                query.setdefault('bool', {}).setdefault('must_not', []).append(templates.get_tag_template(tag.lower()))
        if self.intent == 'general':
            name = self.query
            query.setdefault('bool', {}).setdefault('should', []).append(templates.get_name_template(name))
            query.setdefault('bool', {}).setdefault('should', []).append(templates.get_fuzzy('name', name, 5))
            query.setdefault('bool', {}).setdefault('should', []).append(templates.get_fuzzy('alias', name))
            query.setdefault('bool', {}).setdefault('should', []).append(templates.get_term('members', name))
            query.setdefault('bool', {})['minimum_number_should_match'] = 1
        if self.filters:
            query.setdefault('bool', {}).setdefault('must', []).extend(self.__generate_filter(self.filters))
        if self.nested:
            query.setdefault('bool', {}).setdefault('must', []).extend(self.__generate_filter(self.nested))
        return query

    def __generate_filter(self, kv):

        global collection_ranking_threshold
        pending = []
        if kv.get('round'):
            pending.append(templates.get_terms('round', kv.get('round', [])))
        if kv.get('date'):
            pending.append(templates.get_terms('established', self.__extend_date(kv.get('date'))))
        if kv.get('location'):
            pending.append(templates.get_terms('location', kv.get('location')))
        if kv.get('domestic', None) is not None:
            pending.append(self.__generate_domestic_filter(kv.get('domestic')))
        if kv.get('team'):
            pending.append(templates.get_terms('team', kv.get('team')))
        if kv.get('threshold'):
            pending.append(templates.get_range('ranking_score', 1, collection_ranking_threshold))
        if kv.get('yellow'):
            pending.append(templates.get_terms('yellows', kv.get('yellow')))
        if kv.get('status'):
            pending.append(templates.get_terms('status', kv.get('status')))
        if kv.get('tag'):
            if kv.get('operator', 'and') == 'or':
                pending.append(templates.get_terms('tags', [t.lower() for t in kv.get('tag')]))
            else:
                for t in kv.get('tag', []):
                    pending.append(templates.get_term('tags', t.lower().strip()))
        if kv.get('category'):
            pending.append(templates.get_terms('category', kv.get('category')))
        if kv.get('industry'):
            pending.append(templates.get_nested_term('nested_tag.id', 'industry', kv.get('industry')))
        if kv.get('topic'):
            pending.append(templates.get_nested_term('nested_tag.id', 'topic', kv.get('topic')))
        if kv.get('funding_date'):
            today = datetime.today().date()
            for fd in kv.get('funding_date'):
                if fd == 'latest7':
                    start, end = today - timedelta(days=7), today
                    pending.append(templates.get_range('last_funding_date', end, start))
                elif fd == 'latest30':
                    start, end = today - timedelta(days=30), today
                    pending.append(templates.get_range('last_funding_date', end, start))
                elif fd == 'latest90':
                    start, end = today - timedelta(days=90), today
                    pending.append(templates.get_range('last_funding_date', end, start))
                elif fd.isalnum():
                    start = datetime.strptime('%s-01-01' % fd, '%Y-%m-%d')
                    end = datetime.strptime('%s-12-31' % fd, '%Y-%m-%d')
                    pending.append(templates.get_range('last_funding_date', end, start))
        return pending

    def __generate_domestic_filter(self, domestic):

        if domestic:
            return {'range': {
                'location': {
                    'gt': 0,
                    'lte': 370
                }}}
        else:
            return {'bool': {
                'should': [
                    {'range': {
                        'location': {
                            'gt': 370
                        }
                    }},
                    {'term': {
                        'location': 0
                    }},
                ],
                'minimum_number_should_match': 1}}

    def __extend_date(self, dates):

        dates = list(dates)
        if 2013 in dates:
            dates.extend(xrange(1990, 2013))
        extends = []
        for date in dates:
            for month in xrange(1, 13):
                if month > 9:
                    extends.append(int('%s%s' % (date, month)))
                else:
                    extends.append(int('%s0%s' % (date, month)))
        return extends

    def get_intent(self):

        return self.intent

    def reload_tags(self):

        if datetime.now().hour == self.reload_control:
            return
        self.reload_control = datetime.now().hour
        db = dbcon.connect_torndb()
        self.en_tags = set([t.name.lower() for t in dbutil.get_tags_by_type(db) if is_engish_word(t.name)])
        self.tags = set([t.lower() for t in dbutil.get_searchable_tags(db)])
        db.close()


class GeneralQuery(object):

    # tagger = Tagger(tags=True)
    seg = Segmenter(tags=True)
    yellows = dicts.get_yellow_tags_name()
    name_parser = NameSegmenter()

    db = dbcon.connect_torndb()
    en_tags = set([t.name.lower() for t in dbutil.get_tags_by_type(db) if is_engish_word(t.name)])
    tags = set([t.name.lower() for t in dbutil.get_tags_by_type(db)])
    db.close()

    def __init__(self, input, filters):

        self.input = input if isinstance(input, dict) else input.lower().strip()
        self.filters = filters

        self.intent = None
        self.query = None

    def __intent_classify(self, logger):

        # logger.info('Start to classify intent')
        if isinstance(self.input, dict):
            self.intent = 'tag'
            self.query = self.input
            return
        else:
            # 空搜索
            if not self.input.strip():
                self.intent = 'empty'
                return
            # 英文直接处理
            if self.input.replace(' ', '').replace('+', '').replace('-', '').encode('utf-8').isalnum():
                if self.input.lower() in self.en_tags:
                    self.intent = 'tag'
                    self.query = self.query = {'or': [self.input.strip().lower().replace(' ', '')]}
                    return
                else:
                    self.intent = 'general'
                    self.input = self.input.strip().lower()
                    self.query = self.input
                return
            # any query that contains yellow tag
            if set(self.input.split(' ')).intersection(set(self.yellows)):
                self.intent = 'tag'
                self.query = {}
                for tag in self.input.split(' '):
                    if tag in self.yellows:
                        self.filters.setdefault('yellow', []).append(tag)
                    else:
                        self.query.setdefault('or', []).append(tag)
                return
            # default query analyze
            query = set([word for word in self.seg.cut(self.input)])
            # logger.info('POS Tag Done')
            tagratio = float(len(self.tags & query)) / len(query)
            if tagratio > 0.8 or (len(self.input) > 5 and tagratio > 0.5):
                # 判断是tag搜索
                self.intent = 'tag'
                self.query = {'or': [word.strip().lower() for word in query]}
                return
            else:
                self.intent = 'general'
                self.query = self.input.strip().lower()
                return

    def generate_query(self, logger=None):

        self.__intent_classify(logger)
        # logger.info('End to classify intent')
        query = {}
        if isinstance(self.input, str) or isinstance(self.input, unicode):
            query.setdefault('bool', {}).setdefault('should', []).append(templates.get_term('name', self.input, 10))
        if self.intent == 'tag':
            for tag in self.query.get('and', []):
                query.setdefault('bool', {}).setdefault('must', []).append(templates.get_terms('tags', [tag.lower()]))
                # query.setdefault('bool', {}).setdefault('must', []).append(templates.get_tag_template(tag))
            for tag in self.query.get('or', []):
                query.setdefault('bool', {}).setdefault('should',
                                                        []).extend(templates.get_fast_tag_template(tag.lower()))
            if self.query.get('or'):
                query['bool']['minimum_number_should_match'] = 1
            for tag in self.query.get('not', []):
                query.setdefault('bool', {}).setdefault('must_not', []).append(templates.get_tag_template(tag.lower()))
        if self.intent == 'general':
            name = self.query
            # parsed_names = self.name_parser.segment(name)
            # query.setdefault('bool', {}).setdefault('should', []).append(templates.get_term('alias', name, 100))
            query.setdefault('bool', {}).setdefault('should', []).append(templates.get_name_template(name))
            query.setdefault('bool', {}).setdefault('should', []).append(templates.get_fuzzy('name', name, 5))
            query.setdefault('bool', {}).setdefault('should', []).append(templates.get_fuzzy('alias', name))
            query.setdefault('bool', {}).setdefault('should', []).append(templates.get_term('members', name))
            # fuzzy name
            # if parsed_names:
            #     for parsed_name in parsed_names.split():
            #         query.setdefault('bool', {}).setdefault('should', []).append(
            #             templates.get_term('alias', parsed_name))
            query.setdefault('bool', {})['minimum_number_should_match'] = 1

        if self.filters:
            if logger:
                logger.info('Filter', self.filters)
            query.setdefault('bool', {}).setdefault('must', []).extend(self.__generate_filter(self.filters))
        return query

    def __generate_filter(self, kv):

        global collection_ranking_threshold
        pending = []
        if kv.get('round'):
            pending.append(templates.get_round(kv.get('round')))
        if kv.get('date'):
            pending.append(templates.get_terms('established', self.__extend_date(kv.get('date'))))
        if kv.get('location'):
            pending.append(templates.get_terms('location', kv.get('location')))
        if kv.get('domestic', None) is not None:
            pending.append(self.__generate_domestic_filter(kv.get('domestic')))
        if kv.get('team'):
            pending.append(templates.get_terms('team', kv.get('team')))
        if kv.get('threshold'):
            pending.append(templates.get_range('ranking_score', 1, collection_ranking_threshold))
        if kv.get('yellow'):
            pending.append(templates.get_terms('yellows', [yellow.lower().strip() for yellow in kv.get('yellow')]))
        if kv.get('tag'):
            pending.append(templates.get_terms('tags', kv.get('tag')))
        if kv.get('category'):
            pending.append(templates.get_terms('category', kv.get('category')))
        return pending

    def __generate_domestic_filter(self, domestic):

        if domestic:
            return {'range': {
                'location': {
                    'gt': 0,
                    'lte': 370
                }}}
        else:
            return {'bool': {
                'should': [
                    {'range': {
                        'location': {
                            'gt': 370
                        }
                    }},
                    {'term': {
                        'location': 0
                    }},
                ],
                'minimum_number_should_match': 1}}

    def __extend_date(self, dates):

        dates = list(dates)
        if 2013 in dates:
            dates.extend(xrange(1990, 2013))
        extends = []
        for date in dates:
            for month in xrange(1, 13):
                if month > 9:
                    extends.append(int('%s%s' % (date, month)))
                else:
                    extends.append(int('%s0%s' % (date, month)))
        return extends

    def get_intent(self):

        return self.intent


class EventQuery(object):

    def __init__(self, filters):

        self.filters = filters

    def generate_query(self):

        query = {}
        if self.filters:
            query.setdefault('bool', {}).setdefault('must', []).extend(self.__generate_filter(self.filters))
        return query

    def __generate_filter(self, kv):

        pending = []
        if kv.get('round'):
            pending.append(templates.get_round(kv.get('round')))
        if kv.get('location'):
            pending.append(templates.get_terms('location', kv.get('location')))
        if kv.get('domestic', None) is not None:
            pending.append(self.__generate_domestic_filter(kv.get('domestic')))
        if kv.get('public', None) is not None:
            pending.append(self.__generate_public_filter(kv.get('public')))
        if kv.get('tag'):
            if kv.get('operator', 'or') == 'and':
                for t in kv.get('tag', []):
                    pending.append(templates.get_term('tags', t.lower().strip()))
            else:
                pending.append(templates.get_terms('tags', [t.lower() for t in kv.get('tag')]))
        if kv.get('investor'):
            for iv in kv.get('investor'):
                pending.append(templates.get_fuzzy('investor', iv))
        if kv.get('investorId'):
            pending.append(templates.get_terms('investorId', kv.get('investorId')))
        if kv.get('previous_investor'):
            for iv in kv.get('previous_investor'):
                pending.append(templates.get_fuzzy('previous_investor', iv))
        if kv.get('date'):
            pending.append(templates.get_terms('funding_year', kv.get('date')))
        if kv.get('funding_date'):
            today = datetime.today().date()
            for fd in kv.get('funding_date'):
                if fd == 'latest7':
                    start, end = today - timedelta(days=7), today + timedelta(days=1)
                    pending.append(templates.get_range('last_funding_date', end, start))
                elif fd == 'latest30':
                    start, end = today - timedelta(days=30), today + timedelta(days=1)
                    pending.append(templates.get_range('last_funding_date', end, start))
                elif fd == 'latest90':
                    start, end = today - timedelta(days=90), today + timedelta(days=1)
                    pending.append(templates.get_range('last_funding_date', end, start))
                elif fd.isalnum():
                    pending.append(templates.get_term('funding_year', int(fd)))
        if kv.get('source'):
            pending.append(templates.get_terms('source', kv.get('source')))
        return pending

    def __generate_domestic_filter(self, domestic):

        if domestic:
            return {'range': {
                'location': {
                    'gt': 0,
                    'lte': 370
                }}}
        else:
            return {'bool': {
                'should': [
                    {'range': {
                        'location': {
                            'gt': 370
                        }
                    }},
                    {'term': {
                        'location': 0
                    }},
                ],
                'minimum_number_should_match': 1}}

    def __generate_public_filter(self, public):

        if public:
            return templates.get_terms('source', [0, 69001, 69003, 69999])
        else:
            return templates.get_terms('source', [69002])


class InvestorQuery(object):

    db = dbcon.connect_torndb()
    en_tags = set([t.name.lower() for t in dbutil.get_tags_by_type(db) if is_engish_word(t.name)])
    tags = set([t.lower() for t in dbutil.get_searchable_tags(db)])
    reload_control = 0
    db.close()

    def __init__(self, inputs, filters, online=True):

        self.input = inputs.strip().lower()
        self.filters = filters
        self.online = online

        self.reload_tags()

    def __intent_classify(self):

        # 空搜索
        if not self.input.strip():
            self.intent = 'empty'
            return
        # 英文直接处理
        if self.input.replace(' ', '').replace('+', '').replace('-', '').encode('utf-8').isalnum():
            if self.input.lower() in self.en_tags:
                self.intent = 'tag'
                self.query = [self.input.strip().lower().replace(' ', '')]
                return
            else:
                self.intent = 'general'
                self.input = self.input.strip().lower()
                self.query = self.input
            return
        words = self.input.split(' ')
        if [w.lower().strip() in self.tags for w in words].count(False) == 0:
            self.intent = 'tag'
            self.query = [word.strip().lower() for word in words]
        else:
            self.intent = 'general'
            self.query = self.input.strip().lower()
            return

    def generate_query(self):

        query = {}
        self.__intent_classify()
        if self.intent == 'tag':
            query_piece = templates.get_nested_template('investor_tag', 'investor_tag.tag', self.query)
            query.setdefault('bool', {}).setdefault('must', []).append(query_piece)
        elif self.intent == 'general':
            query.setdefault('bool', {})['should'] = templates.get_investor_name_completion(self.query)
            query['bool']['minimum_number_should_match'] = 1
        if self.online:
            query.setdefault('bool', {}).setdefault('must', []).append(templates.get_term('online', True))
        if self.filters:
            query.setdefault('bool', {}).setdefault('must', []).extend(self.__generate_filter(self.filters))
        return query

    def __generate_filter(self, kv):

        pending = []
        if kv.get('round'):
            pending.append(templates.get_round(kv.get('round')))
        if kv.get('location'):
            pending.append(templates.get_terms('location', kv.get('location')))
        if kv.get('tag'):
            for t in kv.get('tag'):
                pending.append(templates.get_nested_template('investor_tag', 'investor_tag.tag', [t.lower().strip()]))
        if kv.get('domestic', None) is not None:
            pending.append(self.__generate_domestic_filter(kv.get('domestic')))
        return pending

    def get_intent(self):

        return self.intent

    def get_tag(self):

        tags = self.filters.get('tag', [])
        return tags[0] if tags else self.query[0]

    def __generate_domestic_filter(self, domestic):

        if domestic:
            return {'range': {
                'location': {
                    'gt': 0,
                    'lte': 370
                }}}
        else:
            return {'bool': {
                'should': [
                    {'range': {
                        'location': {
                            'gt': 370
                        }
                    }},
                    {'term': {
                        'location': 0
                    }},
                ],
                'minimum_number_should_match': 1}}

    def reload_tags(self):

        if datetime.now().hour == self.reload_control:
            return
        self.reload_control = datetime.now().hour
        db = dbcon.connect_torndb()
        self.en_tags = set([t.name.lower() for t in dbutil.get_tags_by_type(db) if is_engish_word(t.name)])
        self.tags = set([t.lower() for t in dbutil.get_searchable_tags(db)])
        db.close()


class DealQuery(object):

    def __init__(self, input, filters, org):

        self.input = input.lower()
        self.filters = filters
        self.org = org

        self.query = None

    def generate_query(self):

        query = dict()
        query.setdefault('bool', {}).setdefault('should', []).append(templates.get_fuzzy('name', self.input, 5))
        query.setdefault('bool', {}).setdefault('should', []).append(templates.get_fuzzy('alias', self.input))
        query.setdefault('bool', {}).setdefault('should', []).append(templates.get_tag_template(self.input))
        query['bool']['minimum_number_should_match'] = 1
        query.setdefault('bool', {}).setdefault('must', []).extend(self.__generate_filter(self.filters))

        return query

    def __generate_filter(self, kv):

        pending = [templates.get_term('oid', self.org)]
        if kv.get('status'):
            pending.append(templates.get_terms('status', kv.get('status')))
        if kv.get('location'):
            pending.append(templates.get_terms('location', kv.get('location')))
        if kv.get('assignee'):
            pending.append(templates.get_terms('assignee', kv.get('assignee')))
        if kv.get('sponsor'):
            sponsor = [s for s in kv.get('sponsor') if s]
            pending.append(templates.get_terms('sponsor', sponsor))
        if kv.get('portfolioStatus'):
            pending.append(templates.get_terms('portfolioStatus', kv.get('portfolioStatus')))
        if kv.get('stage'):
            pending.append(templates.get_terms('stage', kv.get('stage')))
        if kv.get('portfolioStage'):
            pending.append(templates.get_terms('portfolioStage', kv.get('portfolioStage')))
        return pending


class NewsQuery(object):

    seg = Segmenter()
    tag_max_len = 5
    stopwords = stopword.get_standard_stopwords()
    db = dbcon.connect_torndb()
    news_tags = {t.name: t.id for t in dbutil.get_tags_by_type(db, [11500, 11801])}
    db.close()

    def __init__(self, query_input, filters):

        self.input = query_input.lower().replace(' ', '').replace('/', '')
        # self.input = input.split()
        self.filters = filters
        self.len = len(self.input)

    # field is search target field, can be 'content' or 'title'
    def generate_query(self, field, extend=False):

        query = dict()
        if self.input:
            if self.input.strip() in self.news_tags:
                query = templates.get_term('features', self.news_tags.get(self.input.strip()))
            elif extend:
                if self.len <= self.tag_max_len:
                    key = filter(lambda x: (x not in self.stopwords) and len(x) > 1, self.seg.cut4search(self.input))
                    query.setdefault('bool', {}).setdefault('must', []).append(
                        templates.get_string_template(field, ' '.join(key),  '100%'))
            else:
                if isinstance(self.input, str) or isinstance(self.input, unicode):
                    key = filter(lambda x: (x not in self.stopwords) and len(x) > 1, self.seg.cut4search(self.input))
                    if self.len <= self.tag_max_len:
                        query.setdefault('bool', {}).setdefault('must', []).append(
                            templates.get_term(field, self.input))
                    elif self.len <= 20:
                        query.setdefault('bool', {}).setdefault('must', []).append(
                            templates.get_string_template(field, ' '.join(key), '100%'))
                    else:
                        query.setdefault('bool', {}).setdefault('must', []).append(
                            templates.get_string_template(field, ' '.join(key), '95%'))
        if self.filters:
            for key in self.filters.keys():
                if self.filters.get(key):
                    query.setdefault('bool', {}).setdefault('must', []).append(
                        templates.get_terms(key, self.filters.get(key)))
        if not extend and (not query):
            return {"match_all": {}}

        return query


if __name__ == '__main__':

    print __file__
    inp = u'熊猫优选'
    query = GeneralQuery(input=inp, filters={})
    print query.generate_query()
