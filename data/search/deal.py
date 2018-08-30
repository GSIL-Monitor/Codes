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
from datetime import datetime
from kafka import KafkaConsumer

import db as dbcon
import config as tsbconfig
import templates
from query import DealQuery
from common import dbutil
# from search import SearchClient
from indice import IndexCreator
from elasticsearch import Elasticsearch

# logging
logging.getLogger('search').handlers = []
logger_search = logging.getLogger('search')
logger_search.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_search.addHandler(stream_handler)

# kalfka
consumer_deal = None


class DealSearchClient(IndexCreator):

    def __init__(self, es=None, full_feature=True):

        if full_feature:
            IndexCreator.__init__(self, es)
        global logger_search
        self.logger = logger_search
        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es

    def create_indice(self):

        global logger_search
        self.logger = logger_search
        db = dbcon.connect_torndb()
        for did in [deal.id for deal in db.query('select distinct id from deal where status not in (0, 19000);')]:
            try:
                self.create_single(db, did)
                self.logger.info('%s index created' % did)
            except Exception, e:
                self.logger.exception('%s failed, %s' % (did, e))
        db.close()

    def create_single(self, db, did):

        dinfo = dbutil.get_deal_info(db, did)
        name = dinfo.name.lower().replace(' ', '')
        if dinfo.status and (dinfo.status == 19000 or dinfo.status == 0):
            return
        deal = dict()
        oid = dinfo.organizationId
        deal['oid'] = oid
        deal['did'] = did
        completion = {
            'id': did,
            'did': did,
            'oid': oid,
            '_name': name
        }

        # Name
        alias = set()
        alias.add(name)
        # Full name
        full = dinfo.fullName
        if full and full.strip():
            alias.add(full.lower())
        # Artifact
        aresults = dbutil.get_artifact_idname_from_did(db, did)
        if aresults:
            alias.update([self.valid_name(aname) for _, aname in aresults if self.valid_name(aname)])
        # Alias
        aliass = dbutil.get_alias_idname(db, dinfo.companyId)
        if aliass and len(aliass) < 20:
            alias.update([self.valid_name(aname) for _, aname in aliass if self.valid_name(aname)])

        # create indice names
        completion['completionName'] = list(alias)
        # for item in alias.values():
        #     self.create_index(item, 'deal_completion', item.get('id'))
        deal['name'] = name.lower()
        deal['alias'] = self.analyze_names(alias)

        # create descrption
        desc = dinfo.description
        if desc and desc.strip():
            desc = filter(lambda x: (x not in self.stopwords) and len(x) > 1, list(self.seg.cut4search(desc)))
            deal['description'] = (' '.join(desc)).lower()

        # create tag
        deal['tags'] = dbutil.get_deal_tags(db, did)

        # create filter info
        deal['location'] = dinfo.locationId
        deal['status'] = 18020 if (dinfo.declineStatus and dinfo.declineStatus == 18020) else dinfo.status
        deal['assignee'] = dbutil.get_deal_assignee(db, did)
        deal['sponsor'] = dbutil.get_deal_sponsor(db, did)
        deal['portfolioStatus'] = dinfo.portfolioStatus
        deal['stage'] = dinfo.stageId
        deal['portfolioStage'] = dinfo.portfolioStageId

        # create sort
        deal['round'] = dinfo.currentRound
        deal['investment'] = dinfo.investment
        deal['postMoney'] = dinfo.postMoney
        # deal['lastNoteTime'] = datetime.utcfromtimestamp(dinfo.lastNoteTime) if dinfo.lastNoteTime else None
        deal['lastNoteTime'] = dinfo.lastNoteTime

        self.create_index(completion, 'dealCompletion', did)
        self.create_index(deal, 'deal', did)

    def search(self, type, **kwargs):

        self.logger.info('Query: %s' % (str(kwargs)))
        return {
            'deal': self.__search_deal,
            'deal_completion': self.__search_deal_completion
        }[type](**kwargs)

    def __search_deal(self, **kwargs):

        query = dict(kwargs)
        start = query.get('start', 0)
        size = query.get('size', 10)
        sort = query.get('sort', 'lastNoteTime')
        order = query.get('order', 'default')
        es_query = DealQuery(query.get('input'), query.get('filter', {}), query.get('orgId')).generate_query()
        self.logger.info('ES Query Generated')
        self.logger.info(es_query)

        hits = self.es.search(index='xiniudata', doc_type='deal',
                              body={"query": es_query, "sort": self.__generate_sort_search(sort, order),
                                    "from": start, "size": size})
        self.logger.info('ES Results Fetched')

        count = hits['hits'].get('total', 0)
        hits = [item['_source'] for item in hits['hits']['hits']]
        return {"count": count, "data": [result['did'] for result in hits]}

    def __search_deal_completion(self, **kwargs):

        kv = dict(**kwargs)
        key, org = kv.get('key'), kv.get('org')
        query = templates.get_org_completion(key, org)
        # print query
        hits = self.es.search(index="xiniudata", doc_type="dealCompletion", body={"query": query, "size": 200})
        # print hits

        # result success check
        if ('error' in hits) or hits.get('time_out'):
            return []
            # return {'status': 'failed'}
        hits = [item['_source'] for item in hits['hits']['hits']]
        if len(hits) == 0 or (not hits):
            return []
            # return {'status': 'empty'}
        results, dids = [], set()
        for hit in hits[:10]:
            if hit['did'] in dids:
                continue
            results.append({'id': hit['did'], 'name': hit['_name']})
            dids.add(hit['did'])
        return results

    def __generate_sort_search(self, sort='lastNoteTime', order='default'):

        if sort == 'round':
            if order == 'asc':
                return [{"round": {"order": "asc", "missing": "_last"}}]
            return [{"round": {"order": "desc", "missing": "_last"}}]
        elif sort == 'investment':
            if order == 'desc' or order == 'default':
                return [{"investment": {"order": "desc", "missing": "_last"}}]
            return [{"investment": {"order": "asc", "missing": "_last"}}]
        elif sort == 'postMoney':
            if order == 'asc':
                return [{"postMoney": {"order": "asc", "missing": "_last"}}]
            return [{"postMoney": {"order": "desc", "missing": "_last"}}]
        elif sort == 'lastNoteTime':
            if order == 'desc' or order == 'default':
                return [{"lastNoteTime": {"order": "desc", "missing": "_last"}}]
            return [{"lastNoteTime": {"order": "asc", "missing": "_last"}}]
        else:
            return {}


def init_kafka(index):

    global consumer_deal

    url = tsbconfig.get_kafka_config()
    consumer_deal = KafkaConsumer("track", group_id="deal search%s index" % index,
                                  bootstrap_servers=[url], auto_offset_reset='smallest')


def create_full():

    client = DealSearchClient()
    client.create_indice()


def create_incremental(index):

    global consumer_deal, logger_search
    if int(index) == 1:
        host, port = tsbconfig.get_es_config_1()
        client = DealSearchClient(Elasticsearch([{'host': host, 'port': port}]))
    elif int(index) == 2:
        host, port = tsbconfig.get_es_config_2()
        client = DealSearchClient(Elasticsearch([{'host': host, 'port': port}]))
    else:
        client = DealSearchClient()
    init_kafka(index)
    db = dbcon.connect_torndb()
    logger_search.info('Search client inited')
    while True:
        logger_search.info('Incremental create search%s index starts' % index)
        for message in consumer_deal:
            try:
                logger_search.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                                  message.offset, message.key,
                                                                  message.value))
                did = json.loads(message.value).get('dealId')
                client.create_single(db, int(did))
                logger_search.info('incremental deal %s created' % did)
                consumer_deal.commit()
            except Exception, e:
                logger_search.info(e)


if __name__ == '__main__':

    print __file__
    if sys.argv[1] == 'full' or sys.argv[1] == 'all':
        create_full()
    elif sys.argv[1] == 'incr' or sys.argv[1] == 'incremental':
        create_incremental(sys.argv[2])
