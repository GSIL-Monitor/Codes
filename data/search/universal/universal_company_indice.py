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
from searchutil import NameSegmenter
from common import dbutil
from common.zhtools.segment import Segmenter
from common.zhtools import stopword

import logging
import json

from datetime import datetime, timedelta
from pypinyin import lazy_pinyin
from kafka import KafkaClient, SimpleProducer, KafkaConsumer
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError


loghelper.init_logger('universal', stream=True)
logger_universal_index = loghelper.get_logger('universal')


class UniversalIndexCreator(object):

    stopwords = stopword.get_standard_stopwords()
    seg = Segmenter()
    nameseg = NameSegmenter()

    def __init__(self, es=None):

        global logger_universal_index
        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es
        self.topic_tags = {}
        logger_universal_index.info('Universal Index Creator inited')

    def __check(self):

        global logger_universal_index
        if not self.es.indices.exists(["xiniudata2"]):
            logger_universal_index.info('Creating index xiniudata2')
            self.es.indices.create("xiniudata2")
            logger_universal_index.info('Created')
        self.es.indices.put_mapping("universal", mappings.get_universal_company_mapping(), "xiniudata2")
        logger_universal_index.info('Universal Company mapping created')

    def create_indice(self):

        global logger_universal_index
        self.__check()
        db = dbcon.connect_torndb()
        self.topic_tags = dbutil.get_topic_corresponding_tags(db)
        logger_universal_index.info('Start to create indice')
        logger_universal_index.info(str(self.es.info()))
        logger_universal_index.info('ES Config %s' % str(tsbconfig.get_es_config()))
        for cid in dbutil.get_all_company_id(db):
            try:
                self.create_single(db, cid)
                logger_universal_index.info('%s index created, %s' % (cid, dbutil.get_company_name(db, cid)))
            except Exception, e:
                logger_universal_index.exception('%s failed # %s' % (cid, e))
        db.close()

    def create_single(self, db, cid):

        global logger_universal_index
        # check whether to index this cid
        if not dbutil.get_company_index_type(db, cid):
            logger_universal_index.info('should not index %s' % cid)
            return

        company = {}
        alias, artifacts = set(), set()
        company['ranking_score'] = dbutil.get_company_score(db, cid, 37020)

        name = dbutil.get_company_name(db, cid).lower().replace(' ', '')
        code = dbutil.get_company_code(db, cid)
        company['id'] = code

        # short name
        alias.add(name.lower())
        alias.add(''.join(lazy_pinyin(name.lower())))
        # full name
        full = dbutil.get_company_corporate_name(db, cid, False)
        if full and full.strip():
            alias.add(full.lower())
            alias.add(full.lower().replace(u'北京', '').replace(u'上海', '').replace(u'深圳', '').replace(u'成都', ''))
        # artifact name
        aresults = dbutil.get_artifact_idname_from_cid(db, cid, True)
        if aresults:
            alias.update([self.valid_name(aname) for _, aname in aresults if self.valid_name(aname)])
        # alias
        aliass = dbutil.get_alias_idname(db, cid)
        if aliass and len(aliass) < 20:
            alias.update([self.valid_name(aname) for _, aname in aliass if self.valid_name(aname)])
        # corporate name
        corporate = dbutil.get_company_corporate_name(db, cid)
        if corporate and corporate.strip():
            alias.add(corporate.lower())
        # corporate full name
        corporate_full = dbutil.get_company_corporate_name(db, cid, False)
        if corporate_full and corporate_full.strip():
            alias.add(corporate_full.lower())
        # corporate alias
        corporate_alias = dbutil.get_corporate_alias(db, cid)
        if corporate_alias and len(corporate_alias) < 20:
            alias.update([self.valid_name(aname) for aname in corporate_alias if self.valid_name(aname)])
        # check if there is a relevant digital coin
        dt = dbutil.get_company_digital_coin_info(db, cid)
        if dt:
            alias.add(dt.symbol.lower())
            # short name
            if dt.name:
                alias.add(dt.name.lower().replace(' ', ''))
            # english name
            if dt.enname:
                alias.add(dt.enname.lower())

        # create indice names
        company['name'] = name.lower()
        company['alias'] = self.analyze_names(alias)

        # tag
        tags_info = dbutil.get_company_tags_idname(db, cid, tag_out_type=(11000, 11001, 11002))
        if tags_info:
            for tid, tname, weight in tags_info:
                company.setdefault('tags', []).append(tname.lower())
                company.setdefault('features', []).append(tid)
        company['nested_tag'] = []
        for industry in dbutil.get_company_industries(db, cid):
            company.setdefault('nested_tag', []).append({'id': industry.industryId,
                                                         'published': industry.publishTime,
                                                         "category": "industry"})
        for topic in dbutil.get_company_topics(db, cid):
            msg_publish = dbutil.get_topic_message_company_publish(db, topic)
            company.setdefault('nested_tag', []).append({'id': topic.topicId,
                                                         'published': msg_publish,
                                                         "category": "topic"})
            topic_tag = self.topic_tags.get(topic.topicId)
            if topic_tag:
                company.setdefault('tags', []).append(topic_tag.lower())
        sectors = dbutil.get_company_sector_tag(db, cid)
        company['sector'] = sectors

        # description
        desc = dbutil.get_company_solid_description(db, cid)
        if desc and desc.strip():
            desc = filter(lambda x: (x not in self.stopwords) and len(x) > 1, list(self.seg.cut4search(desc)))
            company['description'] = (' '.join(desc)).lower()

        # round and investors and members
        round = dbutil.get_company_round(db, cid)
        company['round'] = 1000 if round == 0 else round
        company['sort_round'] = dbutil.get_round_sort(db, company.get('round'))
        status = dbutil.get_company_status(db, cid)
        if status in {2020, 2025}:
            company['status'] = status
        elif dbutil.get_company_ipo_status(db, cid):
            company['status'] = -1
        else:
            company['status'] = -2
        company['investors'] = dbutil.get_company_investor_names(db, cid)
        company['investorId'] = dbutil.get_company_investors(db, cid)
        company['members'] = [name for _, name in dbutil.get_member_idname(db, cid)]

        # location
        lid, lname = dbutil.get_company_location(db, cid)
        company['location'] = lid

        # establish date, create date, count of company message
        establish_date = dbutil.get_company_establish_date(db, cid)
        try:
            company['established'] = int(establish_date.strftime('%Y%m'))
        except Exception, e:
            pass
        company['created'] = dbutil.get_company_create_date(db, cid)
        lfd = dbutil.get_corporate_latest_funding(db, dbutil.get_company_corporate_id(db, cid))
        if lfd:
            if lfd.fundingDate:
                company['last_funding_date'] = lfd.fundingDate
            if lfd.investment:
                company['last_funding_amount'] = (lfd.investment * {'Y': 1, 'N': 5}.get(lfd.precise, 1)) / 10000
        company['fa_date'] = dbutil.get_company_latest_fa_date(db, cid)
        company['num_cm'] = len(list(dbutil.get_company_messages(db, cid, "Y")))

        # sort value
        company['sort_sector'] = dbutil.get_tag_novelty(db, sectors[0]) if len(sectors) > 0 else None
        company['sort_location'] = dbutil.get_company_location(db, cid, True)[1]

        # create index
        # print company
        self.create_index(company, 'universal', code)

    def create_index(self, item, doc, iid=None):

        iid = iid if iid else item.get('id')
        if iid:
            self.es.index(index="xiniudata2", doc_type=doc, id=iid, body=item)

    def valid_name(self, name):

        name = name.replace(u'・', u'-').replace(u'－', u'-').split(u'-')[0]
        if len(name) < 20:
            return name.lower()
        return False

    def analyze_names(self, alias):

        analyzed = []
        for name in alias:
            analyzed.append(name)
            seged = self.nameseg.segment(name)
            if seged:
                analyzed.append(seged)
        return list(set(name for name in analyzed if name.strip()))

    def delete_index(self, doc_type, id):

        try:
            self.es.delete('xiniudata2', doc_type, id)
        except NotFoundError, efe:
            pass

    def delete_dead_company(self):

        global logger_universal_index
        db = dbcon.connect_torndb()
        for c in dbutil.get_no_index_company(db):
            logger_universal_index.info('Delete dead %s Processing' % c.id)
            if not c.code:
                continue
            # delete company index
            try:
                self.delete_index('universal', c.code)
            except NotFoundError, efe:
                pass
            except Exception, e:
                logger_universal_index.exception('Failed to delete company %s, %s' % (c.code, e))
            # delete completion
            try:
                self.delete_index('completion', c.id)
            except NotFoundError, efe:
                pass
            except Exception, e:
                logger_universal_index.exception('Failed to delete completion %s, %s' % (c.id, e))
        db.close()


def create_index_all():

    client = UniversalIndexCreator()
    client.create_indice()


def create_index_topic26():

    client = UniversalIndexCreator()
    db = dbcon.connect_torndb()
    dbfyesterday = datetime.now() - timedelta(days=2)
    for tc in dbutil.get_topic_companies(db, 26, dbfyesterday):
        client.create_single(db, tc.companyId)
    db.close()


def init_kafka():

    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    consumer_search = KafkaConsumer("keyword_v2", group_id="create search index new1",
                                    bootstrap_servers=[url], auto_offset_reset='smallest')
    return consumer_search


def create_incremental(index=None):

    global logger_universal_index
    if not index:
        client = UniversalIndexCreator()
    elif int(index) == 1:
        host, port = tsbconfig.get_es_config_1()
        client = UniversalIndexCreator(Elasticsearch([{'host': host, 'port': port}]))
    elif int(index) == 2:
        host, port = tsbconfig.get_es_config_2()
        client = UniversalIndexCreator(Elasticsearch([{'host': host, 'port': port}]))
    else:
        client = UniversalIndexCreator()
    db = dbcon.connect_torndb()
    consumer_search = init_kafka()
    while True:
        logger_universal_index.info('Incremental create search1 index starts')
        try:
            for message in consumer_search:
                try:
                    logger_universal_index.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                                               message.offset, message.key,
                                                                               message.value))
                    action = json.loads(message.value).get('action', 'create')
                    cid = json.loads(message.value).get('id') or json.loads(message.value).get('_id')
                    if action == 'create':
                        client.create_single(db, cid)
                        logger_universal_index.info('incremental %s index created' % cid)
                    elif action == 'delete':
                        if json.loads(message.value).get('aliasId', False):
                            client.create_single(db, cid)
                            logger_universal_index.info('incremental %s alias deleted' % cid)
                        elif json.loads(message.value).get('artifactId', False):
                            client.create_single(db, cid)
                            logger_universal_index.info('incremental %s artifact deleted' % cid)
                        else:
                            client.delete_index('universal', dbutil.get_company_code(db, cid))
                            logger_universal_index.info('incremental %s index deleted' % cid)
                    consumer_search.commit()
                except Exception, e:
                    logger_universal_index.exception('Incr exception# %s \n # %s' % (message, e))
        except Exception, e:
            logger_universal_index.exception('Incr outside exception # %s' % e)


if __name__ == '__main__':

    if sys.argv[1] == 'full':
        create_index_all()
    elif sys.argv[1] == 'incremental' or sys.argv[1] == 'incr':
        if len(sys.argv) > 2:
            create_incremental(sys.argv[2])
        else:
            create_incremental()
    elif sys.argv[1] == 'topic26':
        create_index_topic26()
    elif sys.argv[1] == 'delete':
        client = UniversalIndexCreator()
        client.delete_index('universal', sys.argv[2])
    elif sys.argv[1] == 'dead':
        client = UniversalIndexCreator()
        client.delete_dead_company()
