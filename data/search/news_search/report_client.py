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
from elasticsearch import Elasticsearch

import config as tsbconfig
from query import NewsQuery
from nlp.common.zhtools import stopword
import db as dbcon


# logging
logging.basicConfig(level=logging.INFO, format='%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
logger_ns = logging.getLogger('news search')


class ReportSearchClient(object):

    global logger_ns
    logger = logger_ns
    stopwords = stopword.get_standard_stopwords()

    def __init__(self, es=None):

        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es

    # report search input targets for 'title'
    def search(self, **kwargs):

        self.logger.info('Query: %s' % (str(kwargs)))
        query = dict(kwargs)
        report_query = NewsQuery(query.get('input'), query.get('filter'))
        es_query = report_query.generate_query('title')
        self.logger.info('ES Query, %s' % es_query)

        hits = self.es.search(index='xiniudata2', doc_type='report',
                              body={'query': es_query, 'sort': self.__generate_sort_search(),
                                    'from': query.get('start', 0), 'size': query.get('size', 10)})
        self.logger.info('ES Results Fetched')
        count = hits['hits'].get('total', 0)
        # no results, query extended
        if count == 0 and query.get('start', 0) == 0 and len(query.get('input')) <= 5:
            report_query = NewsQuery(query.get('input'), query.get('filter'))
            es_query = report_query.generate_query('title', extend=True)
            self.logger.info('Extended ES Query, %s' % es_query)
            hits = self.es.search(index='xiniudata2', doc_type='report',
                                  body={'query': es_query, 'sort': self.__generate_sort_search(),
                                        'from': query.get('start', 0), "size": query.get('size', 10)})
            self.logger.info('ES Extended Results Fetched')
            count = min(query.get('size', 10), hits['hits'].get('total', 0))
        # organize results
        hits = hits['hits']['hits']
        hits = [result['_id'] for result in hits]
        self.logger.info('Result ready')
        return {'report': {'count': count, 'data': hits}}

    def __generate_sort_search(self):

        return [{'date': {'order': 'desc', 'missing': '_last'}}]


if __name__ == '__main__':
    rsc = ReportSearchClient()
    key, start, size = sys.argv[1] if len(sys.argv) > 1 else '', int(sys.argv[2]) if len(sys.argv) > 2 else 0, int(sys.argv[3]) if len(sys.argv) > 3 else 10
    # result = rsc.search(input="", start=start, size=size, filter={'reportType': [78002]})['report']
    result = rsc.search(input=u"%s" % key, start=start, size=size)['report']
    mongo = dbcon.connect_mongo()
    logger_ns.info('%s\n' % result['count'])
    ids = map(ObjectId, result['data'])
    logger_ns.info(ids)

    for record in (mongo.article.report.find({'_id': {'$in': ids}})).sort([('pdfCreationDate', -1)]):
        logger_ns.info(record['_id'])
        logger_ns.info(record['pdfCreationDate'])
        logger_ns.info('title: %s' % record['title'])
        logger_ns.info('type: %s' % record['type'])
        logger_ns.info('pages: %s' % record['pages'])
        size = record['size'] / 1024
        logger_ns.info('size: %s KB\n' % size) if size < 1024 else logger_ns.info('size: %.2f MB\n' % (size / 1024.))