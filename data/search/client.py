# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

import time
import json
import logging
from itertools import chain

from pypinyin import lazy_pinyin
from elasticsearch import Elasticsearch

import db as dbcon
import templates
import searchutil
import config as tsbconfig
from results import ResultAnalyzer
from query import Query, GeneralQuery
from nlp.embedding.words import WordExtender
from nlp.common import dbutil
from nlp.common.dsutil import SortedFixLenList, FrozenLenList, FixLenDictCach


class MilisecondFormatter(logging.Formatter):

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            if "%F" in datefmt:
                msec = "%03d" % record.msecs
                datefmt = datefmt.replace("%F", msec)
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            s = "%s,%03d" % (t, record.msecs)
        return s


# logging
logging.getLogger('cs').handlers = []
logger_cs = logging.getLogger('cs')
logger_cs.setLevel(logging.INFO)
formatter = MilisecondFormatter(fmt='%(name)-6s %(asctime)s-%(levelname)4s- %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S.%F')
# formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%H:%M:%S.%F')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger_cs.addHandler(stream_handler)

# config
collection_size = 10000
collection_ranking_threshold = 0.25


class SearchClient(object):

    search_portion_size = 1000

    global logger_cs

    # tagextend = WordExtender()
    # tagextender = WordExtender(3)
    resulter = ResultAnalyzer()
    prompt_tags_cach = FixLenDictCach(20)

    investor_lists = searchutil.get_online_investors()
    cycle = 0

    def __init__(self, es=None):

        global logger_cs
        self.logger = logger_cs
        if not es:
            # host, port, user, pswd = tsbconfig.get_es_config()
            # self.es = Elasticsearch([{'host': host, 'port': port}], http_auth=(user, pswd))
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es
        # self.logger.info('General Search client inited')

    def search(self, type, **kwargs):

        # self.logger.info('Query: %s' % (str(kwargs)))
        global logger_cs
        logger_cs.info('Query: %s' % (str(kwargs)))
        return {
            'completion': self.__search_completion,
            'general': self.__search_general,
            'collection': self.__search_collection,
            'topic': self.__search_topic,
            'blockchain': self.__search_blockchain,
        }[type](**kwargs)

    def __search_blockchain(self, **kwargs):

        query = dict(kwargs)
        start = query.get('start', 0)
        size = query.get('size', 10)
        highlight = query.get('highlight', False)

        # query preparation
        general_query = GeneralQuery(query.get('input'), query.get('filter'))
        es_query = general_query.generate_query(self.logger)
        intent = general_query.get_intent()
        self.logger.info('ES Query Generated, intent %s' % intent)

        # empty search
        if (isinstance(query.get('input'), str) or
            isinstance(query.get('input'), unicode)) and (not query.get('input').strip()):
            return {"company": {"count": 0, "data": []}, "filter": {"tag": []}, "relate": [],
                    'collection_preservable': False}

        # search
        default_sort = 6 if intent == 'tag' else 1
        # sort = default_sort if query.get('sort', 1) == 1 else query.get('sort')
        sort = query.get('sort', 1)
        order = query.get('order', 'default')
        portion_size = max(self.search_portion_size, size)
        portion, start = start / portion_size, start % portion_size
        # self.logger.info('Sort by %s, default %s' % (sort, default_sort))
        # self.logger.info('ES Query Final, from %s to %s' % (portion_size*portion, portion_size))
        self.logger.info('Query, %s' % es_query)
        hits = self.es.search(index='xiniudata', doc_type='company',
                              body={"query": es_query, "sort": self.__generate_sort_search(sort, order),
                                    "from": portion_size * portion, "size": portion_size,
                                    "highlight": self.__generate_highlight_search()})
        self.logger.info('ES Results Fetched')

        # get count, and review if applicable
        count = hits['hits'].get('total', 0)
        if count == 0:
            flag, review = self.__review(query)
            if flag:
                hits = review
                count = hits['hits'].get('total', 0)

        # preservable for collection
        preservable = True if intent == 'tag' else False

        # format results
        rank_sort = 6 if (default_sort == 6 and sort in (1, 6)) else 0
        hits = self.__re_rank_company(hits, start, size, rank_sort, highlight)
        self.logger.info('Result ready')
        # return {"company": {"count": count, "data": hits}, "filter": {"tag": prompt_tags}, "relate": related_tags,
        #         "collection_preservable": preservable}
        return {"company": {"count": count, "data": hits}, "filter": {"tag": []},
                "collection_preservable": preservable}

    def __search_general(self, **kwargs):

        query = dict(kwargs)
        if query.get('field', 'default') == 'investor':
            results = self.__search_general_investor(**kwargs)
            results['default'] = 'investor'
            return results
        if query.get('field', 'default') == 'company':
            results = self.__search_general_company(**kwargs)
            results['default'] = 'company'
            return results
        if query.get('field', 'default') == 'default':
            results = self.__search_general_company(**kwargs)
            results.update(self.__search_general_investor(**kwargs))
            results['default'] = self.__classify_general_intent(query.get('input'))
            return results

    def __search_general_investor(self, **kwargs):

        kv = dict(**kwargs)
        key = kv.get('input')

        if isinstance(key, dict) or not key.strip():
            return {"investor": {"count": 0, "data": []}}
        else:
            key = key.lower()

        if u' ' in key and not key.replace(u' ', u'').encode('utf-8').isalnum():
            query = templates.get_investor_completion(key.split(), True)
            keys = key.split()
        else:
            query = templates.get_investor_completion(key)
            keys = [key]
        start = kv.get('start', 0)
        size = kv.get('size', 10)
        hits = self.es.search(index="xiniudata", doc_type="completion",
                              body={"query": query, "from": 0, "size": 300})

        # result success check
        count = hits['hits'].get('total', 0)
        if ('error' in hits) or hits.get('time_out'):
            return {"investor": {"count": 0, "data": []}}
        hits = hits['hits']['hits']
        if len(hits) == 0 or (not hits):
            return {"investor": {"count": 0, "data": []}}

        # results ranking and format
        sort_func = lambda x: sum([json.loads(x['_source'].get('feature_scores', u'{}')).get(term, x.get('_score'))
                                   for term in keys])
        hits = sorted(hits, key=sort_func, reverse=True)[start: start+size]
        hits = map(lambda x: x['_source'], filter(lambda item: '_source' in item, hits))
        hits = map(lambda x: {'name': x.get('_name'), 'id': int(x.get('id')[1:])}, hits)
        return {"investor": {"count": count, "data": hits}}

    def __search_general_company(self, **kwargs):

        query = dict(kwargs)
        start = query.get('start', 0)
        size = query.get('size', 10)
        highlight = query.get('highlight', False)

        # query preparation
        general_query = GeneralQuery(query.get('input'), query.get('filter'))
        es_query = general_query.generate_query(self.logger)
        intent = general_query.get_intent()
        self.logger.info('ES Query Generated, intent %s' % intent)

        # fast hint
        fast_hint = self.__fast_hint(query, highlight, intent)
        if fast_hint:
            self.logger.info('Fast hint')
            return fast_hint

        # empty search
        if (isinstance(query.get('input'), str) or
                isinstance(query.get('input'), unicode)) and (not query.get('input').strip()):
            return {"company": {"count": 0, "data": []}, "filter": {"tag": []}, "relate": [],
                    'collection_preservable': False}

        # process relate tag, dismissed
        if isinstance(query.get('input'), dict):
            processing_tags = list(chain(query.get('input').get('and', []), query.get('input').get('or', [])))
        else:
            processing_tags = [query.get('input')]
        # related_tags = self.tagextender.extend4tag(*processing_tags)

        # search
        default_sort = 6 if intent == 'tag' else 1
        # sort = default_sort if query.get('sort', 1) == 1 else query.get('sort')
        sort = query.get('sort', 1)
        order = query.get('order', 'default')
        portion_size = max(self.search_portion_size, size)
        portion, start = start/portion_size, start % portion_size
        # self.logger.info('Sort by %s, default %s' % (sort, default_sort))
        # self.logger.info('ES Query Final, from %s to %s' % (portion_size*portion, portion_size))
        hits = self.es.search(index='xiniudata', doc_type='company',
                              body={"query": es_query, "sort": self.__generate_sort_search(sort, order),
                                    "from": portion_size*portion, "size": portion_size,
                                    "highlight": self.__generate_highlight_search()})
        self.logger.info('Query, %s' % es_query)
        self.logger.info('ES Results Fetched')

        # get prompt filters
        if isinstance(query.get('input'), str) or isinstance(query.get('input'), unicode):
            query_string = query.get('input')
            # print query_string
            if self.prompt_tags_cach.get(query_string):
                prompt_tags = self.prompt_tags_cach.get(query_string)
                self.logger.info('Query in cach, dunt generate prompt %s' % query_string)
            else:
                prompt_tags = self.resulter.prompt_filter(hits)
                prompt_tags = [tag for tag in prompt_tags if tag not in processing_tags]
                self.prompt_tags_cach.append((query_string, prompt_tags))
                # self.logger.info('Hits, %s' % str(hits))
                self.logger.info('Generate new prompt for %s, is %s' % (query_string, str(prompt_tags)))
            self.logger.info('Filter prompted')
        else:
            prompt_tags = []
            self.logger.info('Complex search, nothing prompted')

        # get count, and review if applicable
        count = hits['hits'].get('total', 0)
        if count == 0:
            flag, review = self.__review(query)
            if flag:
                hits = review
                count = hits['hits'].get('total', 0)

        # preservable for collection
        preservable = True if intent == 'tag' else False

        # format results
        rank_sort = 6 if (default_sort == 6 and sort in (1, 6)) else 0
        hits = self.__re_rank_company(hits, start, size, rank_sort, highlight)
        self.logger.info('Result ready')
        # return {"company": {"count": count, "data": hits}, "filter": {"tag": prompt_tags}, "relate": related_tags,
        #         "collection_preservable": preservable}
        return {"company": {"count": count, "data": hits}, "filter": {"tag": prompt_tags},
                "collection_preservable": preservable}

    def __search_completion(self, **kwargs):

        kv = dict(**kwargs)
        key, field = kv.get('key'), kv.get('field')

        # ranking benchmark
        rank_key = lambda x: x.get('ranking_score', 0.01)

        # query, diff with field
        if field:
            if field == 'industry':
                query = templates.get_industry_completion(key)
            elif field == 'investor':
                if kv.get('strict'):
                    query = templates.get_investor_strict_completion(key)
                else:
                    query = templates.get_investor_completion(key, online=kv.get('online', [True, False]))
            else:
                query = templates.get_field_completion(key, field)
            hits = self.es.search(index="xiniudata", doc_type="completion", body={"query": query, "size": 20})
            results = {
                field: FrozenLenList(10)
            }
        else:
            query = templates.get_completion(key)
            # self.logger.info(query)
            hits = self.es.search(index="xiniudata", doc_type="completion", body={"query": query, "size": 100})
            results = {
                'name': FrozenLenList(8),
                'keyword': SortedFixLenList(3, rank_key),
                'location': FrozenLenList(1),
                'investor': SortedFixLenList(2, rank_key),
                'industry': FrozenLenList(1)
            }

        # result success check
        if ('error' in hits) or hits.get('time_out'):
            return {'status': 'failed'}
        hits = hits['hits']['hits']
        if len(hits) == 0 or (not hits):
            return {'status': 'empty'}

        # results ranking and format
        hits = map(lambda x: x['_source'], filter(lambda item: '_source' in item, hits))
        for hit in hits:
            # self.logger.info(hit)
            prompt = hit.get('_prompt') or 'name'
            results[prompt].append(hit)
        return results

    def __search_collection(self, **kwargs):

        global collection_size

        query = dict(kwargs)
        es_query = GeneralQuery(query.get('input'), query.get('filter'))
        es_query = es_query.generate_query()

        hits = self.es.search(index='xiniudata', doc_type='company',
                              body={"query": es_query, "from": 0, "size": collection_size})
        hits = self.__re_rank_company(hits, start=0, size=collection_size)
        return {"company": {"data": hits}}

    def __search_topic(self, **kwargs):

        global collection_size
        query = dict(kwargs).get('query')
        hits = self.es.search(index='xiniudata', doc_type='company',
                              body={"query": query, "from": 0, "size": collection_size})
        hits = self.__re_rank_company(hits, start=0, size=collection_size)
        return {"company": {"data": hits}}

    def __re_arrange(self, hits, start, size):

        if ('error' in hits) or hits.get('time_out'):
            return {'status': 'failed'}
        if len(hits['hits']['hits']) == 0 or (not hits['hits']['hits']):
            return {}
        hits = hits['hits']['hits']

        return [{"id": result['_id'], "highlight": self.__highlight_sort(result['highlight'].keys())}
                for result in hits][start:(start+size)]

    def __highlight_sort(self, highlights):

        if not highlights:
            return 'name'
        if 'name' in highlights:
            return 'name'
        if 'tags' in highlights:
            return 'tags'
        if 'yellows' in highlights:
            return 'tags'
        if 'investors' in highlights:
            return 'investors'
        if 'members' in highlights:
            return 'members'
        if 'alias' in highlights:
            return 'alias'
        if 'description' in highlights:
            return 'description'
        return highlights[0]

    def __generate_sort_search(self, sort=0, order='default'):

        if sort == 2:
            if order == 'default' or order == 'asc':
                return [{"round": {"order": "asc", "missing": "_last"}}]
            return [{"round": {"order": "desc", "missing": "_last"}}]
        elif sort == 3:
            if order == 'desc' or order == 'default':
                return [{"established": {"order": "desc", "missing": "_last"}}]
            return [{"established": {"order": "asc", "missing": "_last"}}]
        elif sort == 4:
            return [{"created": {"order": "desc", "missing": "_last"}}]
        elif sort == 5:
            return [{"fa_date": {"order": "desc", "missing": "_last"}}]
        elif sort == 6:
            return [{"ranking_score": {"order": "desc", "missing": "_last"}}]
        elif sort == 7:
            if order == 'desc' or order == 'default':
                return [{"num_cm": {"order": "desc", "missing": "_last"}}]
            return [{"num_cm": {"order": "asc", "missing": "_last"}}]
        else:
            return {}

    def __generate_highlight_search(self):

        return {
            "fields": {
                "name": {},
                "alias": {},
                "tags": {},
                "yellows": {},
                "investors": {},
                "members": {},
                "description": {}
            }
        }

    def __re_rank_company(self, hits, start=0, size=10, sort=None, highlight=False):

        """
        re-calculate the score, normalize es score, multiple by ranking_score
        the final score is the product of two parts:
        1. the relevance score of the query and the result
        2. the quality score of the result itself
        """
        if ('error' in hits) or hits.get('time_out'):
            return {'status': 'failed'}
        if len(hits['hits']['hits']) == 0 or (not hits['hits']['hits']):
            return {}
        hits = hits['hits']['hits']
        if sort == 6:
            hits = sorted(hits,
                          key=lambda x: (x['_source'].get('ranking_score', 0) + 0.01) * x.get('_score'), reverse=True)
        # self.logger.info('Orignal, %s' % ','.join([str(result['_score']) for result in hits][start:(start+size)]))
        if highlight:
            return [{"id": result['_id'], "highlight": self.__highlight_sort(result.get('highlight', {}).keys())}
                    for result in hits][start:(start+size)]
        else:
            return [result['_id'] for result in hits][start:(start+size)]

    def __fast_hint(self, query, highlight=False, intent='default'):

        if self.__exist_filter(query.get('filter', {})):
            return False
        if isinstance(query.get('input'), str) or isinstance(query.get('input'), unicode):
            key = query.get('input').strip().lower()
            if intent == 'tag':
                return False
            # 有限公司
            if u'有限公司' in key:
                codes = self.__search_completion(key=key, field='name')
                if codes and codes.get('name', False) and 0 < len(codes.get('name')) < 5:
                    if highlight:
                        highlight_field = lambda x: 'name' if x else 'alias'
                        codes = [{'id': item.get('_code'), 'highlight': highlight_field(key == item.get('_name'))}
                                 for item in codes.get('name')]
                    else:
                        codes = list(set([item.get('_code') for item in codes.get('name')]))
                    return {"company": {"count": len(codes), "data": codes}, "filter": {"tag": []}, "relate": []}
            # complete result count equal to 1 or 2
            else:
                completion = self.__search_completion(key=key, field='name')
                self.logger.info(completion)
                if 0 < len(completion.get('name', [])) < 3:
                    if highlight:
                        highlight_field = lambda x: 'name' if x else 'alias'
                        codes = [{'id': item.get('_code'), 'highlight': highlight_field(key == item.get('_name'))}
                                 for item in completion.get('name')]
                    else:
                        codes = list(set([item.get('_code') for item in completion.get('name')]))
                    return {"company": {"count": len(codes), "data": codes},
                            "filter": {"tag": []}, "relate": [], 'collection_preservable': False}
        return False

    def __review(self, query):

        if self.__exist_filter(query.get('filter')) or query.get('start') > 0:
            return False, None
        if isinstance(query.get('input'), str) or isinstance(query.get('input'), unicode):
            name = query.get('input').replace(' ', '').replace('+', '').replace('-', '')
            es_query = {}
            if len(name) < 5:
                es_query.setdefault('bool', {}).setdefault('should', []).append(
                    templates.get_string_template('name', ' '.join(name), '100%')
                )
            es_query.setdefault('bool', {}).setdefault('should', []).append(
                templates.get_string_template('alias', ''.join(lazy_pinyin(name, errors='ignore')), '100%')
            )
            sort = query.get('sort', 1)
            order = query.get('order', 'default')
            hits = self.es.search(index='xiniudata', doc_type='company',
                                  body={"query": es_query, "sort": self.__generate_sort_search(sort, order),
                                        "from": 0, "size": 10})
            # print es_query
            return True, hits
        return False, None

    def __classify_general_intent(self, input):

        if self.cycle >= 100:
            self.cycle = 0
            self.investor_lists = searchutil.get_online_investors()
        self.cycle += 1

        if (isinstance(input, str) or isinstance(input, unicode)) and input in self.investor_lists:
            return 'investor'
        else:
            return 'company'

    def __exist_filter(self, f):

        for k, v in f.items():
            if v:
                return True
        return False