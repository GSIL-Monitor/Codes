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
loghelper.init_logger("amac", stream=True)
logger_amac = loghelper.get_logger("amac")


class AMACClient(object):

    def __init__(self, es=None):

        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es

    def search(self, type, key, start=0, size=10):

        return {
            'general': self.__search_general,
            'fund': self.__search_fund,
            'manager': self.__search_manager
        }[type](key, start, size)

    def __search_general(self, key, start, size):

        global logger_amac
        query = templates.get_amac_distinct_completion(key, 'gp')
        logger_amac.info(query)
        hits = self.es.search(index="xiniudata2", doc_type="amac", body=query)

        # result success check
        if ('error' in hits) or hits.get('time_out'):
            return {}
        hits = hits['aggregations']['distinctId']
        count = hits.get('count', {}).get('value', 0)
        if count == 0 or (not hits):
            return {'code': [], 'count': 0}

        hits = [b.get('key') for b in hits.get('data', {}).get('buckets')[start:start + size]]
        return {'code': list(hits), 'count': count}

    def __search_fund(self, key, start, size):

        global logger_amac
        query = templates.get_amac_completion(key)
        logger_amac.info(query)
        hits = self.es.search(index="xiniudata2", doc_type="amac",
                              body={"query": query, "from": start, "size": size})

        # result success check
        count = hits['hits'].get('total', 0)
        if ('error' in hits) or hits.get('time_out'):
            return {}
        hits = hits['hits']['hits']
        if len(hits) == 0 or (not hits):
            return {'code': list(hits), 'count': count}

        hits = map(lambda x: x['_source']['amacid'], filter(lambda item: '_source' in item, hits))
        return {'code': list(hits), 'count': count}

    def __search_manager(self, key, start, size):

        global logger_amac
        query = templates.get_amac_distinct_completion(key, 'managerId')
        logger_amac.info(query)
        hits = self.es.search(index="xiniudata2", doc_type="amac", body=query)

        # result success check
        if ('error' in hits) or hits.get('time_out'):
            return {}
        hits = hits['aggregations']['distinctId']
        count = hits.get('count', {}).get('value', 0)
        if count == 0 or (not hits):
            return {'code': [], 'count': 0}

        hits = [b.get('key') for b in hits.get('data', {}).get('buckets')[start:start+size]]
        return {'code': list(hits), 'count': count}


if __name__ == '__main__':

    amac = AMACClient()
    print amac.search('general', u'SCX007')
