# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import logging
from bson.objectid import ObjectId
from itertools import chain

from pypinyin import lazy_pinyin
from elasticsearch import Elasticsearch

import config as tsbconfig
from query import NewsQuery
from nlp.common.zhtools import stopword
import db as dbcon


# logging
logging.basicConfig(level=logging.INFO, format='%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
logger_ns = logging.getLogger('news search')


class NewsSearchClient(object):

    global logger_ns
    logger = logger_ns
    stopwords = stopword.get_standard_stopwords()

    def __init__(self, es=None):

        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es

    def __search(self, field, **kwargs):

        """
        field is search target field, can be 'content' or 'title'
        """

        self.logger.info('Query: %s' % (str(kwargs)))
        query = dict(kwargs)
        news_query = NewsQuery(query.get('input'), query.get('filter'))
        es_query = news_query.generate_query(field)
        self.logger.info('ES Query, %s' % es_query)

        hits = self.es.search(index='xiniudata2', doc_type='news',
                              body={'query': es_query, 'sort': self.__generate_sort_search(),
                                    'from': query.get('start', 0), 'size': query.get('size', 10)})
        self.logger.info('ES Results Fetched')
        count = hits['hits'].get('total', 0)
        # no results, query extended
        if count == 0 and query.get('start', 0) == 0 and len(query.get('input')) <= 10:
            news_query = NewsQuery(query.get('input'), query.get('filter'))
            es_query = news_query.generate_query(field, extend=True)
            hits = self.es.search(index='xiniudata2', doc_type='news',
                                  body={'query': es_query, 'sort': self.__generate_sort_search(),
                                        'from': query.get('start', 0), "size": query.get('size', 10)})
            self.logger.info('ES Extended Results Fetched')
            count = hits['hits'].get('total', 0)
        # organize results
        hits = hits['hits']['hits']
        hits = [result['_id'] for result in hits]
        self.logger.info('Result ready')
        return {'news': {'count': count, 'data': hits}}

    def search_content(self, **kwargs):
        return self.__search('content', **kwargs)

    def search_title(self, **kwargs):
        return self.__search('title', **kwargs)

    def search(self, type, **kwargs):

        return {
            'title': self.search_title,
            'content': self.search_content
        }[type](**kwargs)

    def __generate_sort_search(self):

        return [{'date': {'order': 'desc', 'missing': '_last'}}]


if __name__ == '__main__':

    nsc = NewsSearchClient()
    # result = nsc.search_title(input=sys.argv[1] if len(sys.argv) > 1 else '', filter={})['news']
    result = nsc.search_title(input='', filter={})['news']
    logger_ns.info(result['count'])
    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    logger_ns.info(result['count'])
    ids = map(ObjectId, result['data'])
    for id in ids:
        for record in (mongo.article.news.find({'_id': id})):
            logger_ns.info(record['_id'])
            logger_ns.info(record['date'])
            tags = {}
            if 'sectors' in record:
                tags = set(record['sectors'])
            if 'features' in record:
                tags.update(set(record['features']))
            logger_ns.info('news tags %s' % list(tags)) if tags else logger_ns.info('news has no tags')
            logger_ns.info('news type %s' % record['type']) if 'type' in record else logger_ns.info('news has no type')
            logger_ns.info('title: %s\n' % record['title'])
