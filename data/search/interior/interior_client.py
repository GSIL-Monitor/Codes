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
loghelper.init_logger("interior", stream=True)
logger_is = loghelper.get_logger("interior")


class InteriorSearchClient(object):

    global logger_is
    logger = logger_is

    def __init__(self, es=None):

        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es

    def search(self, key, actives=None, start=0, size=10):

        if not actives:
            actives = ['Y', 'A', 'P']
        query = templates.get_new_completion(key, actives)
        hits = self.es.search(index="xiniudata", doc_type="interior",
                              body={"query": query, "from": start, "size": size})

        # result success check
        count = hits['hits'].get('total', 0)
        if ('error' in hits) or hits.get('time_out'):
            return {'name': list(hits), 'count': count, 'status': 'failed'}
        hits = hits['hits']['hits']
        if len(hits) == 0 or (not hits):
            return {'name': list(hits), 'count': count}

        hits = map(lambda x: {'code': x['_source']['code'], 'name': x['_source']['name'],
                              'active': x['_source']['active']},
                   filter(lambda item: '_source' in item, hits))
        return {'name': list(hits), 'count': count}