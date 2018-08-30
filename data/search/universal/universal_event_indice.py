# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../nlp'))

import config as tsbconfig
import db as dbcon
import loghelper
import mappings
from common import dbutil

from itertools import chain
from pypinyin import lazy_pinyin
from kafka import KafkaClient, SimpleProducer, KafkaConsumer
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

loghelper.init_logger('universal-e', stream=True)
logger_universale_index = loghelper.get_logger('universal-e')


class UniversalEventIndexCreator(object):

    def __init__(self, es=None):

        global logger_universale_index
        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es
            logger_universale_index.info('Universal Index Creator inited')

    def __check(self):

        global logger_universale_index
        if not self.es.indices.exists(["xiniudata2"]):
            logger_universale_index.info('Creating index xiniudata2')
            self.es.indices.create("xiniudata2")
            logger_universale_index.info('Created')
        self.es.indices.put_mapping("event", mappings.get_universal_event_mapping(), "xiniudata2")
        logger_universale_index.info('Universal Event mapping created')

    def delete_dead_event(self):

        global logger_universale_index
        db = dbcon.connect_torndb()
        dbback = dbcon.connect_torndb()
        logger_universale_index.info('Start to delete dead funding')
        for funding in dbutil.get_itered_funding(dbback):
            if not dbutil.get_funding_index_type(db, funding.id):
                logger_universale_index.info('Deleting funding %s' % funding.id)
                self.delete_index('event', funding.id)
        db.close()

    def delete_index(self, doc_type, id):

        try:
            self.es.delete('xiniudata2', doc_type, id)
        except NotFoundError, efe:
            pass

    def create_indice(self):

        global logger_universale_index

        self.__check()
        db = dbcon.connect_torndb()
        logger_universale_index.info('Start to create indice')
        logger_universale_index.info(str(self.es.info()))
        logger_universale_index.info('ES Config %s' % str(tsbconfig.get_es_config()))
        for funding in dbutil.get_funding_by_date(db):
            try:
                self.create_single(db, funding)
                logger_universale_index.info('%s index created' % funding.id)
            except Exception, e:
                logger_universale_index.exception('%s failed # %s' % (funding.id, e))
        db.close()

    def create_recent_indice(self):

        global logger_universale_index

        db = dbcon.connect_torndb()
        logger_universale_index.info('Start to create recent funding indice')
        logger_universale_index.info(str(self.es.info()))
        logger_universale_index.info('ES Config %s' % str(tsbconfig.get_es_config()))
        self.__check()
        for funding in dbutil.get_makeup_funding(db):
            try:
                self.create_single(db, funding)
                logger_universale_index.info('%s index created' % funding.id)
            except Exception, e:
                logger_universale_index.exception('%s failed # %s' % (funding.id, e))
        db.close()

    def create_single(self, db, funding):

        global logger_universale_index

        # funding that is not active
        if not dbutil.get_funding_index_type(db, funding.id):
            return

        event = {'fid': funding.id}
        event['investorId'] = dbutil.get_funding_investor_ids(db, funding.id)
        event['investor'] = [dbutil.get_investor_name(db, iid) for iid in event.get('investorId', [])]
        # previous investors
        if funding.fundingDate:
            previous_fundings = [f.id for f in dbutil.get_company_funding(db, funding.companyId)
                                 if f.fundingDate and f.fundingDate < funding.fundingDate]
            previous_iids = set(chain(*[dbutil.get_funding_investor_ids(db, fid) for fid in previous_fundings]))
            event['previous_investor'] = [dbutil.get_investor_name(db, iid) for iid in previous_iids if iid]
        event['location'] = dbutil.get_company_location(db, funding.companyId)[0]
        sectors = dbutil.get_company_sector_tag(db, funding.companyId)
        event['sector'] = sectors[0] if len(sectors) > 0 else 0
        tags_info = dbutil.get_company_tags_idname(db, funding.companyId, tag_out_type=(11000, 11001, 11002))
        if tags_info:
            for tid, tname, weight in tags_info:
                event.setdefault('tags', []).append(tname.lower())
        event['round'] = funding.round
        event['sort_round'] = dbutil.get_round_sort(db, funding.round)
        if funding.investment:
            precise = {'Y': 1, 'N': 5}.get(funding.precise, 1)
            investment = funding.investment * precise * dbutil.get_currency_rate(db, funding.currency) / 10000
            event['last_funding_amount'] = investment
        else:
            event['last_funding_amount'] = None
        event['last_funding_date'] = funding.fundingDate
        event['funding_year'] = funding.fundingDate.year if funding.fundingDate else None
        event['publish_date'] = funding.publishDate
        event['source'] = funding.source if funding.source else 0
        event['sort_sector'] = dbutil.get_tag_novelty(db, sectors[0]) if len(sectors) > 0 else None
        event['sort_location'] = dbutil.get_company_location(db, funding.companyId, True)[1]
        self.es.index(index="xiniudata2", doc_type='event', id=funding.id, body=event)


if __name__ == '__main__':

    if len(sys.argv) > 2:
        if not sys.argv[2]:
            uei = UniversalEventIndexCreator()
        elif int(sys.argv[2]) == 1:
            host, port = tsbconfig.get_es_config_1()
            uei = UniversalEventIndexCreator(Elasticsearch([{'host': host, 'port': port}]))
        elif int(sys.argv[2]) == 2:
            host, port = tsbconfig.get_es_config_2()
            uei = UniversalEventIndexCreator(Elasticsearch([{'host': host, 'port': port}]))
        else:
            uei = UniversalEventIndexCreator()
    else:
        uei = UniversalEventIndexCreator()

    if sys.argv[1] == 'full':
        uei.create_indice()
    elif sys.argv[1] == 'recent':
        uei.create_recent_indice()
    elif sys.argv[1] == 'dead':
        uei.delete_dead_event()
