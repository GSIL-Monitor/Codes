# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import loghelper
import config as tsbconfig
import templates
from common import dbutil

from elasticsearch import Elasticsearch


# logger
loghelper.init_logger("coin", stream=True)
logger_coin = loghelper.get_logger("coin")


class DigitalTokenSearchClient(object):

    global logger_coin
    logger = logger_coin

    def __init__(self, es=None):

        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es

    def search(self, key, actives=None, start=0, size=10, sort=1, order='desc'):

        if not actives:
            actives = ['Y']
        query = templates.get_coin_completion(key, actives)
        self.logger.info(query)
        hits = self.es.search(index="xiniudata", doc_type="digital_token",
                              body={"query": query, "from": start, "size": size,
                                    "sort": self.__generate_sort_search(sort, order)})

        # result success check
        count = hits['hits'].get('total', 0)
        if ('error' in hits) or hits.get('time_out'):
            return {}
        hits = hits['hits']['hits']
        if len(hits) == 0 or (not hits):
            return {'ids': list(hits), 'count': count}

        hits = map(lambda x: x['_source']['id'], filter(lambda item: '_source' in item, hits))
        return {'ids': list(hits), 'count': count}

    def __generate_sort_search(self, sort=4, order='desc'):

        if sort == 1:
            if order == 'desc':
                return [{"price": {"order": "desc", "missing": "_last"}}]
            return [{"price": {"order": "asc", "missing": "_last"}}]
        elif sort == 2:
            if order == 'desc':
                return [{"increase24h": {"order": "desc", "missing": "_last"}}]
            return [{"increase24h": {"order": "asc", "missing": "_last"}}]
        elif sort == 3:
            if order == 'desc':
                return [{"turnover24h": {"order": "desc", "missing": "_last"}}]
            return [{"turnover24h": {"order": "asc", "missing": "_last"}}]
        elif sort == 4:
            if order == 'desc':
                return [{"circulationMarketValue": {"order": "desc", "missing": "_last"}}]
            return [{"circulationMarketValue": {"order": "asc", "missing": "_last"}}]
        elif sort == 5:
            if order == 'desc':
                return [{"circulationQuantity": {"order": "desc", "missing": "_last"}}]
            return [{"circulationQuantity": {"order": "asc", "missing": "_last"}}]
        elif sort == 6:
            if order == 'desc':
                return [{"flowRate": {"order": "desc", "missing": "_last"}}]
            return [{"flowRate": {"order": "asc", "missing": "_last"}}]
        elif sort == 7:
            if order == 'desc':
                return [{"totalCirculation": {"order": "desc", "missing": "_last"}}]
            return [{"totalCirculation": {"order": "asc", "missing": "_last"}}]
        else:
            return {}

