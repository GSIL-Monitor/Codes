# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../nlp'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

import logging
import json
from math import log
from copy import copy
from kafka import KafkaClient, SimpleProducer, KafkaConsumer
from elasticsearch import Elasticsearch
from pypinyin import lazy_pinyin

import config as tsbconfig
import db as dbcon
from common import dbutil

# logging
logging.getLogger('searchi').handlers = []
logger_searchi = logging.getLogger('searchi')
logger_searchi.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_searchi.addHandler(stream_handler)


# kalfka
consumer_search = None
producer_search = None


def init_kafka(index):

    global producer_search, consumer_search

    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    producer_search = SimpleProducer(kafka)
    consumer_search = KafkaConsumer("search_investor", group_id="create search%s index" % index,
                                    bootstrap_servers=[url], auto_offset_reset='smallest')


class InvestorSearchClient(object):

    def __init__(self, es):

        global logger_searchi
        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es
        self.db = dbcon.connect_torndb()

    def delete_index(self, iid):

        self.es.delete('xiniudata', 'completion', 'i%s' % iid)

    def create_index(self, iid):

        global logger_searchi
        alias = set()
        iname = dbutil.get_investor_name(self.db, iid)
        code = dbutil.get_investor_info(self.db, iid).code
        if len(iname) < 1:
            logger_searchi.exception('%s investor has no name' % iid)
            return
        alias.add(iname.strip())
        other_names = [item for item in dbutil.get_investor_alias(self.db, iid) if item.strip()]
        alias.update(set(other_names))
        alias = [name.decode('utf-8').strip() for name in alias]
        alias.extend([''.join(lazy_pinyin(name, errors='ignore')) for name in alias])
        for alia in copy(alias):
            alias.append(alia.replace(u'投资', u'').replace(u'基金', u'').replace(u'创投', u'').replace(u'资本', u''))
        alias.extend([name.lower() for name in alias])
        alias = list(set(alias))
        tags_scores = {k: round(v, 2) for k, v in sorted(json.loads(dbutil.get_investor_tags(self.db, iid, 0)).items(),
                                                         key=lambda x: -x[1])[:30]}
        tags = [tag.lower() for tag, _ in tags_scores.items()]
        active = dbutil.get_investor_info(self.db, iid).active
        item = {
            'id': 'i%s' % iid,
            '_code': code,
            '_name': iname.lower(),
            'completionName': alias,
            '_prompt': 'investor',
            'ranking_score': round(log(dbutil.get_investor_info(self.db, iid).get('fundingCntFrom2017') or 1, 2), 2),
            'online': True if dbutil.get_investor_info(self.db, iid).online == 'Y' else False,
            'active': 'Y' if (active is None or active == 'Y') else active,
            'features': tags,
            'feature_scores': json.dumps(tags_scores)
        }
        self.__create_index(item)

    def __create_index(self, item):

        iid = item.get('id')
        if iid:
            self.es.index(index="xiniudata", doc_type="completion", id=iid, body=item)


def incremental_process_investor_index(index):

    global logger_searchi, consumer_search, producer_search

    if int(index) == 1:
        host, port = tsbconfig.get_es_config_1()
        client = InvestorSearchClient(Elasticsearch([{'host': host, 'port': port}]))
    elif int(index) == 2:
        host, port = tsbconfig.get_es_config_2()
        client = InvestorSearchClient(Elasticsearch([{'host': host, 'port': port}]))
    else:
        host, port = tsbconfig.get_es_config()
        client = InvestorSearchClient(Elasticsearch([{'host': host, 'port': port}]))
        logger_searchi.error('Not legal elasticsearch config %s' % index)

    init_kafka(index)

    while True:
        logger_searchi.info('Incremental create search%s index starts' % index)
        try:
            for message in consumer_search:
                try:
                    logger_searchi.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                                       message.offset, message.key,
                                                                       message.value))
                    iid = json.loads(message.value).get('id') or json.loads(message.value).get('_id')
                    action = json.loads(message.value).get('action', 'create')
                    if action == 'create':
                        client.create_index(iid)
                        logger_searchi.info('incremental %s index created' % iid)
                    elif action == 'delete':
                        client.delete_index(iid)
                        logger_searchi.info('incremental %s index deleted' % iid)
                    consumer_search.commit()
                except Exception, e:
                    logger_searchi.exception('Incr exception# %s \n # %s' % (message, e))
        except Exception, e:
            logger_searchi.exception('Incr outside exception # %s' % e)


def process_investor_indice(index):

    global logger_searchi
    if int(index) == 1:
        host, port = tsbconfig.get_es_config_1()
        client = InvestorSearchClient(Elasticsearch([{'host': host, 'port': port}]))
    elif int(index) == 2:
        host, port = tsbconfig.get_es_config_2()
        client = InvestorSearchClient(Elasticsearch([{'host': host, 'port': port}]))
    elif int(index) == 0:
        host, port = tsbconfig.get_es_config()
        client = InvestorSearchClient(Elasticsearch([{'host': host, 'port': port}]))
        logger_searchi.info('Using default client, %s, %s' % (host, client))
    else:
        logger_searchi.error('Not legal elasticsearch config %s' % index)
        return

    logger_searchi.info('Start to create index')
    db = dbcon.connect_torndb()
    for iid, _ in dbutil.get_all_investor(db):
        try:
            client.create_index(iid)
            logger_searchi.info('%s created' % iid)
        except Exception, e:
            logger_searchi.exception('%s failed' % iid)
    db.close()


def test():

    global logger_searchi
    host, port = tsbconfig.get_es_config()
    client = InvestorSearchClient(Elasticsearch([{'host': host, 'port': port}]))
    client.create_index(122)


if __name__ == '__main__':

    print __file__

    if sys.argv[1] == 'incr' or sys.argv[1] == 'incremental':
        incremental_process_investor_index(sys.argv[2])
    elif sys.argv[1] == 'full' or sys.argv[1] == 'all':
        process_investor_indice(sys.argv[2])
    elif sys.argv[1] == 'test':
        test()
