# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../nlp'))

import loghelper
import db as dbcon
import config as tsbconfig
import templates
from common import dbutil
from common.dsutil import SortedFixLenList, FrozenLenList, FixLenDictCach
from query import UniversalQuery, EventQuery, InvestorQuery
from client import SearchClient

import json
from elasticsearch import Elasticsearch


# logger
loghelper.init_logger("universal", stream=True)
logger_universal = loghelper.get_logger("universal")


class UniversalSearchClient(object):

    global logger_universal
    logger = logger_universal

    general_client = SearchClient()
    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()

    def __init__(self, es=None):

        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es
        self.max_result_size = 1000

    def search(self, type, **kwargs):

        self.logger.info('Query: %s' % (str(kwargs)))
        return {
            'general': self.__search_universal,
            'combined': self.__search_combined,
            'investor': self.__search_investor,
            'industry': self.__search_industry,
            'topic': self.__search_topic,
            'ranklist': self.__search_ranklist,
            'event': self.__search_event,
            'completion': self.__search_completion
        }[type](**kwargs)

    def __search_completion(self, **kwargs):

        kv = dict(**kwargs)
        key, field = kv.get('key'), kv.get('field')

        # ranking benchmark
        rank_key = lambda x: x.get('ranking_score', 0.01)

        # query, diff with field
        if field:
            query = templates.get_field_completion(key, field)
            hits = self.es.search(index="xiniudata2", doc_type="completion", body={"query": query, "size": 20})
            results = {
                field: FrozenLenList(10)
            }
        else:
            query = templates.get_completion(key)
            # self.logger.info(query)
            hits = self.es.search(index="xiniudata2", doc_type="completion", body={"query": query, "size": 100})
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

    def __search_combined(self, **kwargs):

        query = dict(kwargs)
        results = {'relevant': []}
        companies = self.__search_universal(**query)
        results['company'] = companies.get('company', {})
        results['investor'] = self.__search_investor(**query).get('investor', {})
        industris = self.general_client.search('completion', key=query.get('input', ''),
                                               field='industry').get('industry', [])
        industris = map(lambda x: {'name': x.get('_name'), 'code': x.get('_code'), 'id': x.get('id')[8:]}, industris)
        for ind in companies.get('industry', []):
            if ind.get('id') in [industry.get('id') for industry in industris]:
                continue
            else:
                industris.append(ind)
        results['industry'] = industris
        return results

    def __search_universal(self, **kwargs):

        query = dict(kwargs)
        start = query.get('start', 0)
        size = min(query.get('size', 10), self.max_result_size)
        highlight = query.get('highlight', False)
        sort = query.get('sort', 76001)
        order = query.get('order', 'default')

        # query preparation
        general_query = UniversalQuery(query.get('input'), query.get('filter'))
        es_query = general_query.generate_query()
        intent = general_query.get_intent()
        self.logger.info('ES Query Generated, intent %s' % intent)

        # fast hint
        if not intent == 'tag':
            fast_hint = self.__fast_hint(query, highlight, intent)
            if fast_hint:
                self.logger.info('Fast hint')
                return fast_hint
        # rethink sort function
        if sort == 76001 and intent == 'general':
            sort = 0
            order = 'desc'

        # logger_universal.info('sort %s, order %s' % (sort, order))
        hits = self.es.search(index='xiniudata2', doc_type='universal',
                              body={"query": es_query, "sort": self.__generate_sort_search(sort, order),
                                    "from": start, "size": size, "highlight": self.__generate_highlight_search()})
        count = hits['hits'].get('total', 0)
        hits = self.__organize(hits, highlight)
        self.logger.info('Result ready')
        return {"company": {"count": count, "data": hits}}

    def __search_investor(self, **kwargs):

        global max_size
        query = dict(kwargs)
        start = query.get('start', 0)
        size = min(query.get('size', 10), self.max_result_size)
        sort = query.get('sort', 76001)
        order = query.get('order', 'default')

        investor_query = InvestorQuery(query.get('input'), query.get('filter'))
        es_query = investor_query.generate_query()
        if sort == 76001 and (investor_query.get_intent() == 'tag' or query.get('filter', {}).get('tag')):
            sort = 76008
        nested_tag = investor_query.get_tag() if sort == 76008 else None
        self.logger.info('ES, %s' % es_query)
        self.logger.info('Sort, %s' % self.__generate_sort_search(sort, order, nested_tag))
        hits = self.es.search(index='xiniudata2', doc_type='investor',
                              body={"query": es_query, "sort": self.__generate_sort_search(sort, order, nested_tag),
                                    "from": start, "size": size})
        count = hits['hits'].get('total', 0)
        hits = self.__organize(hits)
        self.logger.info('Result ready, %s' % str(hits))
        return {"investor": {"count": count, "data": hits}}

    def __search_industry(self, **kwargs):

        query = dict(kwargs)
        start = query.get('start', 0)
        size = min(query.get('size', 10), self.max_result_size)
        sort = query.get('sort', 1)
        order = query.get('order', 'default')
        idid = query.get('industry', 0)

        general_query = UniversalQuery(query.get('input'), query.get('filter'), {'industry': query.get('industry')})
        es_query = general_query.generate_query()
        logger_universal.info('ES %s, industry %s' % (es_query, idid))
        hits = self.es.search(index='xiniudata2', doc_type='universal',
                              body={"query": es_query, "sort": self.__generate_sort_search(sort, order, idid),
                                    "from": start, "size": size})
        count = hits['hits'].get('total', 0)
        hits = self.__organize(hits)
        self.logger.info('Result ready')
        sector_filters = self.__get_sector_filter(idid, 'industry')
        return {"company": {"count": count, "data": hits, 'sectors': sector_filters}}

    def __search_topic(self, **kwargs):

        query = dict(kwargs)
        start = query.get('start', 0)
        size = min(query.get('size', 10), self.max_result_size)
        sort = query.get('sort', 76001)
        order = query.get('order', 'default')
        tpid = query.get('topic', 0)
        if sort == 76001:
            sort = 76020

        general_query = UniversalQuery(query.get('input'), query.get('filter'), {'topic': query.get('topic')})
        es_query = general_query.generate_query()
        logger_universal.info('ES %s, topic %s' % (es_query, tpid))
        hits = self.es.search(index='xiniudata2', doc_type='universal',
                              body={"query": es_query, "sort": self.__generate_sort_search(sort, order, tpid),
                                    "from": start, "size": size})
        count = hits['hits'].get('total', 0)
        hits = self.__organize(hits)
        self.logger.info('Result ready')
        sector_filters = self.__get_sector_filter(tpid, 'topic')
        return {"company": {"count": count, "data": hits, 'sectors': sector_filters}}

    def __search_ranklist(self, **kwargs):

        query = dict(kwargs)
        start = query.get('start', 0)
        size = min(query.get('size', 10), self.max_result_size)
        sort = query.get('sort', 76001)
        order = query.get('order', 'default')
        tag = query.get('filter', {}).get('tag')
        if not tag:
            return {"company": {"count": 0, "data": [], 'sectors': []}}
        tag = tag[0]
        tid = dbutil.get_tag_id(self.db, tag)[0]

        general_query = UniversalQuery(query.get('input'), query.get('filter'))
        es_query = general_query.generate_query()
        logger_universal.info('ES %s, topic %s' % (es_query, tag))
        hits = self.es.search(index='xiniudata2', doc_type='universal',
                              body={"query": es_query, "sort": self.__generate_sort_search(sort, order, tid),
                                    "from": start, "size": size})
        count = hits['hits'].get('total', 0)
        hits = self.__organize(hits)
        self.logger.info('Result ready')
        sector_filters = self.__get_sector_filter(tag, 'tag')
        return {"company": {"count": count, "data": hits, 'sectors': sector_filters}}

    def __search_event(self, **kwargs):

        query = dict(kwargs)
        start = query.get('start', 0)
        size = min(query.get('size', 10), self.max_result_size)
        sort = query.get('sort', 1)
        order = query.get('order', 'default')

        # sector filter needed
        if query.get('filter', {}).get('investor'):
            investor = query.get('filter', {}).get('investor')
            if investor:
                investor = investor[0]
                sector_filters = self.__get_sector_filter(investor, 'investor')
            else:
                sector_filters = []
        else:
            sector_filters = []

        event_query = EventQuery(query.get('filter'))
        es_query = event_query.generate_query()
        self.logger.info('ES, %s' % es_query)
        hits = self.es.search(index='xiniudata2', doc_type='event',
                              body={"query": es_query, "sort": self.__generate_sort_search(sort, order),
                                    "from": start, "size": size})
        count = hits['hits'].get('total', 0)
        hits = self.__organize(hits)
        self.logger.info('Result ready, %s' % str(hits))
        return {"funding": {"count": count, "data": hits, "sectors": sector_filters}}

    def __get_sector_filter(self, source, ftype):

        sector_filters = self.mongo.keywords.sector_filters.find_one({'source': source, 'filter_type': ftype})
        sector_filters = sector_filters.get('sectors', []) if sector_filters else []
        sector_filters = [dbutil.get_tag_name(self.db, tid) for tid in sector_filters]
        return sector_filters

    def __fast_hint(self, query, highlight=False, intent='default'):

        if self.__exist_filter(query.get('filter', {})):
            return False
        if isinstance(query.get('input'), str) or isinstance(query.get('input'), unicode):
            key = query.get('input').strip().lower()
            if intent == 'tag':
                return False
            # 有限公司
            if u'有限公司' in key:
                codes = self.general_client.search('completion', key=key, field='name')
                if codes and codes.get('name', False) and 0 < len(codes.get('name')) < 5:
                    if highlight:
                        highlight_field = lambda x: 'name' if x else 'alias'
                        codes = [{'id': item.get('_code'), 'highlight': highlight_field(key == item.get('_name'))}
                                 for item in codes.get('name')]
                    else:
                        codes = list(set([item.get('_code') for item in codes.get('name')]))
                    industries = self.__find_industry(codes)
                    return {"company": {"count": len(codes), "data": codes}, "filter": {"tag": []}, "relate": [],
                            "industry": industries}
            # complete result count equal to 1 or 2
            else:
                completion = self.general_client.search('completion', key=key, field='name')
                if 0 < len(completion.get('name', [])) < 3:
                    if highlight:
                        highlight_field = lambda x: 'name' if x else 'alias'
                        codes = [{'id': item.get('_code'), 'highlight': highlight_field(key == item.get('_name'))}
                                 for item in completion.get('name')]
                    else:
                        codes = list(set([item.get('_code') for item in completion.get('name')]))
                    industries = self.__find_industry(codes)
                    return {"company": {"count": len(codes), "data": codes},
                            "filter": {"tag": []}, "relate": [], 'collection_preservable': False,
                            "industry": industries}
        return False

    def __find_industry(self, codes):

        cids = [dbutil.get_id_from_code(self.db, code) for code in codes]
        idids = [ind.industryId for ind in dbutil.get_company_industries(self.db, cids, True)]
        inds = [dbutil.get_industry_info(self.db, idid) for idid in idids]
        return [{"id": ind.id, "code": ind.code, "name": ind.name} for ind in inds
                if (ind.active is None or ind.active == 'Y')]

    def __organize(self, hits, highlight=False):

        if ('error' in hits) or hits.get('time_out'):
            return {'status': 'failed'}
        if len(hits['hits']['hits']) == 0 or (not hits['hits']['hits']):
            return []
        hits = hits['hits']['hits']
        if highlight:
            return [{"id": result['_id'], "highlight": self.__highlight_sort(result.get('highlight', {}).keys())}
                    for result in hits]
        else:
            return [result['_id'] for result in hits]

    def __generate_sort_search(self, sort=0, order='default', nested_value=None):

        if sort == 76001:
            if order == 'default' or order == 'desc':
                return [{"ranking_score": {"order": "desc", "missing": "_last"}}]
            return [{"ranking_score": {"order": "asc", "missing": "_last"}}]
        elif sort == 76002:
            if order == 'default' or order == 'desc':
                return [{"sort_sector": {"order": "desc", "missing": "_last"}}]
            return [{"sort_sector": {"order": "asc", "missing": "_last"}}]
        elif sort == 76003:
            if order == 'default' or order == 'desc':
                return [{"sort_location": {"order": "desc", "missing": "_last"}}]
            return [{"sort_location": {"order": "asc", "missing": "_last"}}]
        elif sort == 76004:
            if order == 'default' or order == 'desc':
                return [{"last_funding_date": {"order": "desc", "missing": "_last"}}]
            return [{"last_funding_date": {"order": "asc", "missing": "_last"}}]
        elif sort == 76005:
            if order == 'asc' or order == 'default':
                return [{"sort_round": {"order": "asc", "missing": "_last"}}]
            return [{"sort_round": {"order": "desc", "missing": "_last"}}]
        elif sort == 76006:
            if order == 'default' or order == 'desc':
                return [{"last_funding_amount": {"order": "desc", "missing": "_last"}}]
            return [{"last_funding_amount": {"order": "asc", "missing": "_last"}}]
        elif sort == 76007:
            if order == 'default' or order == 'desc':
                return [{"established": {"order": "desc", "missing": "_last"}}]
            return [{"established": {"order": "asc", "missing": "_last"}}]
        elif sort == 76008:
            if order == 'default' or order == 'desc':
                return [{'investor_tag.confidence': {"order": "desc",
                                                     "missing": "_last",
                                                     "nested_path": "investor_tag",
                                                     "nested_filter": {
                                                         "term": {"investor_tag.tag": nested_value}
                                                     }}}]
            return [{'investor_tag.confidence': {"order": "asc",
                                                 "missing": "_last",
                                                 "nested_path": "investor_tag",
                                                 "nested_filter": {
                                                     "term": {"investor_tag.tag": nested_value}
                                                 }}}]
        elif sort == 76009:
            if order == 'default' or order == 'desc':
                return [{"portfolio_number_annual": {"order": "desc", "missing": "_last"}}]
            return [{"portfolio_number_annual": {"order": "asc", "missing": "_last"}}]
        elif sort == 76010:
            if order == 'default' or order == 'desc':
                return [{"portfolio_number": {"order": "desc", "missing": "_last"}}]
            return [{"portfolio_number": {"order": "asc", "missing": "_last"}}]
        elif sort == 76020:
            if order == 'default' or order == 'desc':
                return [{'nested_tag.published': {"order": "desc",
                                                  "missing": "_last",
                                                  "nested_path": "nested_tag",
                                                  "nested_filter": {
                                                      "term": {"nested_tag.id": nested_value}
                                                  }}}]
            return [{'nested_tag.published': {"order": "asc",
                                              "missing": "_last",
                                              "nested_path": "nested_tag",
                                              "nested_filter": {
                                                  "term": {"nested_tag.id": nested_value}
                                              }}}]
        else:
            return []

    def __generate_highlight_search(self):

        return {
            "fields": {
                "name": {},
                "alias": {},
                "tags": {},
                "investors": {},
                "members": {},
                "description": {}
            }
        }

    def __exist_filter(self, f):

        for k, v in f.items():
            if v:
                return True
        return False

    def __highlight_sort(self, highlights):

        if not highlights:
            return 'name'
        if 'name' in highlights:
            return 'name'
        if 'tags' in highlights:
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


def test():

    client = UniversalSearchClient()
    search = []
    for i in xrange(15):
        search.extend(client.search('event', filter={'investorId': [217]},
                                    start=i*20, size=20).get('funding', {}).get('data'))
    db = dbcon.connect_torndb()
    dbs = db.query('select distinct funding.id fid from company, funding, funding_investor_rel rel, corporate cp where rel.investorId=217  and funding.corporateId = company.corporateId and (company.active is null or company.active="Y") and company.corporateId=cp.id and (cp.active is null or cp.active="Y") and rel.fundingId=funding.id and (funding.active is null or funding.active="Y") and (rel.active is null or rel.active="Y");')
    search = map(lambda x: int(x), search)
    dbs = [f.fid for f in dbs]
    print len(search), len(set(search))
    print [fid for fid in search if fid not in dbs]


if __name__ == '__main__':

    test()
