# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

import config as tsbconfig
import db as dbcon
import mappings
import deleter
from searchutil import Identifier, NameSegmenter
from interior.interior_indice import InteriorIndexCreator
from common import dbutil
from nlp.score.end import RankScorer
from nlp.common.zhtools.segment import Segmenter
from nlp.common.zhtools import stopword

import logging
import json

from pypinyin import lazy_pinyin
from kafka import KafkaClient, SimpleProducer, KafkaConsumer
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
# from elasticsearch5 import Elasticsearch
# from elasticsearch5.exceptions import NotFoundError


# logging
logging.getLogger('index').handlers = []
logger_index = logging.getLogger('index')
logger_index.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                              '%d %b %Y %H:%M:%S')
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_index.addHandler(stream_handler)


class IndexCreator(object):

    nameseg = NameSegmenter()
    identifier = Identifier()
    stopwords = stopword.get_standard_stopwords()
    seg = Segmenter()

    def __init__(self, es=None):

        global logger_index
        self.logger = logger_index
        if not es:
            host, port = tsbconfig.get_es_config()
            self.logger.info(','.join([host, port]))
            self.es = Elasticsearch([{'host': host, 'port': port}])
            # host, port, user, pswd = tsbconfig.get_es_config()
            # self.logger.info(','.join([host, port, user, pswd]))
            # self.es = Elasticsearch([{'host': host, 'port': port}], http_auth=(user, pswd))
        else:
            self.es = es
        self.logger.info(self.es)
        self.logger.info('Index Creator inited')

    def __check(self):

        if not self.es.indices.exists(["xiniudata"]):
            self.logger.info('Creating index xiniudata')
            self.es.indices.create("xiniudata")
            self.logger.info('Created')
        self.es.indices.put_mapping("company", mappings.get_company_mapping(), "xiniudata")
        self.logger.info('Company mapping created')
        self.es.indices.put_mapping("completion", mappings.get_completion_mapping(), "xiniudata")
        self.logger.info('Completion mapping created')
        self.es.indices.put_mapping("dealCompletion", mappings.get_deal_completion_mapping(), "xiniudata")
        self.logger.info('Deal Completion mapping created')
        self.es.indices.put_mapping("deal", mappings.get_deal_mapping(), "xiniudata")
        self.logger.info('Deal mapping created')
        self.es.indices.put_mapping("interior", mappings.get_company_interior_mapping(), "xiniudata")
        self.logger.info('Interior mapping created')
        self.es.indices.put_mapping("digital_token", mappings.get_digital_token_mapping(), "xiniudata")
        self.logger.info('Token mapping created')

    def delete_index(self, doc_type, id):

        try:
            self.es.delete('xiniudata', doc_type, id)
        except NotFoundError, efe:
            pass

    def delete_dead_company(self):

        db = dbcon.connect_torndb()
        for c in dbutil.get_no_index_company(db):
            self.logger.info('Delete dead %s Processing' % c.id)
            if not c.code:
                continue
            # delete company index
            try:
                self.delete_index('company', c.code)
            except NotFoundError, efe:
                pass
            except Exception, e:
                self.logger.exception('Failed to delete company %s, %s' % (c.code, e))
            # delete completion
            try:
                self.delete_index('completion', c.id)
            except NotFoundError, efe:
                pass
            except Exception, e:
                self.logger.exception('Failed to delete completion %s, %s' % (c.id, e))
        db.close()

    def create_indice(self):

        self.__check()

        db = dbcon.connect_torndb()
        self.logger.info('Start to create indice')
        self.logger.info(str(self.es.info()))
        self.logger.info('ES Config %s' % str(tsbconfig.get_es_config()))
        try:
            self.logger.info('Start to create location & tag indice')
            self.create_indice_completion_locations(db)
            self.create_indice_completion_keywords(db)
        except Exception, e:
            self.logger.exception('location indice & tag failed')
            self.logger.exception(e)

        for cid in dbutil.get_all_company_id(db):
            try:
                self.create_single(db, cid)
                self.logger.info('%s index created, %s' % (cid, dbutil.get_company_name(db, cid)))
            except Exception, e:
                self.logger.exception('%s failed # %s' % (cid, e))
        db.close()

    def create_single(self, db, cid):

        """
        create a single index for a particular company,
        completion id consists of its type and original id, including
            cxxxx, fxxx, axxxx, pxxxx, nxxxx, standing for company, full, artifact, product, nick
            kxxxx, keyword
        """

        # check whether to index this cid
        if not dbutil.get_company_index_type(db, cid):
            self.logger.info('should not index %s' % cid)
            return

        company = {}
        alias = set()
        company_score = dbutil.get_company_score(db, cid, 37020)
        company['ranking_score'] = company_score

        name = dbutil.get_company_name(db, cid).lower().replace(' ', '')
        code = dbutil.get_company_code(db, cid)
        company['cid'] = code
        completion = {
            'id': cid,
            '_name': name,
            '_code': code,
            '_prompt': 'name',
        }

        # First, Names
        # short name
        alias.add(name.lower())
        alias.add(''.join(lazy_pinyin(name.lower())))
        # full name
        full = dbutil.get_company_corporate_name(db, cid, False)
        if full and full.strip():
            alias.add(full.lower())
            # TODO temp solution
            alias.add(full.lower().replace(u'北京', '').replace(u'上海', '').replace(u'深圳', ''))
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
        completion['completionName'] = list(alias)
        company['name'] = name.lower()
        company['alias'] = self.analyze_names(alias)

        # Second, team identify, investor identify
        team = self.identifier.identify(cid)
        if team and len(team) > 0:
            company['team'] = team
        if dbutil.exist_company_tag(db, cid, 309129):
            company['investor'] = 44010

        # Third, keywords
        # regular tag
        tags_info = dbutil.get_company_tags_idname(db, cid, tag_out_type=(11000, 11001, 11002))
        if tags_info:
            for tid, tname, weight in tags_info:
                company.setdefault('tags', []).append(tname.lower())
        # yellows, --> forget y take this out
        yellows = dbutil.get_company_tags_yellow(db, cid)
        if yellows:
            company['yellows'] = [yellow.lower() for yellow in yellows]

        # Forth, description
        desc = dbutil.get_company_solid_description(db, cid)
        if desc and desc.strip():
            desc = filter(lambda x: (x not in self.stopwords) and len(x) > 1, list(self.seg.cut4search(desc)))
            company['description'] = (' '.join(desc)).lower()

        # Fifth, round and investors and members
        company['round'] = dbutil.get_company_round(db, cid)
        company['investors'] = dbutil.get_company_investor_names(db, cid)
        company['members'] = [name for _, name in dbutil.get_member_idname(db, cid)]

        # Sixth, location
        lid, lname = dbutil.get_company_location(db, cid)
        company['location'] = lid

        # Seventh, establish date, create date, count of company message
        establish_date = dbutil.get_company_establish_date(db, cid)
        try:
            company['established'] = int(establish_date.strftime('%Y%m'))
        except Exception, e:
            pass
        company['created'] = dbutil.get_company_create_date(db, cid)
        company['num_cm'] = len(list(dbutil.get_company_messages(db, cid, "Y")))

        # Eighth, fa date
        company['fa_date'] = dbutil.get_company_latest_fa_date(db, cid)

        # Ninth, sector with level 1, duplicated
        company['sector_l1'] = dbutil.get_company_sector(db, cid, 1)

        # create index
        self.create_index(company, 'company', code)
        self.create_index(completion, 'completion', cid)

        # print completion, company
        # close db
        db.close()

    def create_index(self, item, doc, iid=None):

        iid = iid if iid else item.get('id')
        if iid:
            self.es.index(index="xiniudata", doc_type=doc, id=iid, body=item)

    def analyze_names(self, alias):

        analyzed = []
        for name in alias:
            analyzed.append(name)
            seged = self.nameseg.segment(name)
            if seged:
                analyzed.append(seged)
        return list(set(name for name in analyzed if name.strip()))

    def valid_name(self, name):

        name = name.replace(u'・', u'-').replace(u'－', u'-').split(u'-')[0]
        if len(name) < 20:
            return name.lower()
        return False

    def create_indice_completion_locations(self, db):

        location_score = 1
        for lid, lname in dbutil.get_all_locations(db):
            if len(lname) < 1:
                self.logger.exception('%s location has no name' % lid)
                continue
            en_name = dbutil.get_location_en_name(db, lid)
            item = {
                'id': 'l%s' % lid,
                '_name': lname,
                'en_name': en_name,
                'completionName': [lname.lower(), ''.join(lazy_pinyin(lname)), en_name.lower()],
                '_prompt': 'location',
                'ranking_score': location_score * round((1.0/len(lname)), 2)
            }
            self.create_index(item, 'completion')

    def create_indice_completion_keywords(self, db, update=False):

        searchable_tag_types = [11011, 11012, 11013, 11100, 11110, 11111, 11050, 11051, 11052, 11053, 11054]
        no_searchable_tag_types = [11010, 11000, 11001]
        if not update:
            for x in dbutil.get_all_tag(db, searchable_tag_types):
                tid, tname = x.id, x.name
                item = {
                    'id': 'k%s' % tid,
                    '_name': tname,
                    'completionName': [tname.lower(), ''.join(lazy_pinyin(tname))],
                    '_prompt': 'keyword',
                    'ranking_score': round((1.0/(len(tname)+1)), 2)
                }
                self.create_index(item, 'completion')
        else:
            for x in dbutil.get_all_tag(db, searchable_tag_types, True):
                tid, tname = x.id, x.name
                item = {
                    'id': 'k%s' % tid,
                    '_name': tname,
                    'completionName': [tname.lower(), ''.join(lazy_pinyin(tname))],
                    '_prompt': 'keyword',
                    'ranking_score': round((1.0/(len(tname)+1)), 2)
                }
                self.create_index(item, 'completion')
        for x in dbutil.get_all_tag(db, no_searchable_tag_types, True):
            tid = 'k%s' % x.id
            try:
                self.delete_index('completion', tid)
            except Exception, e:
                pass

    def create_indice_completion_industry(self, db):

        for idid, _ in dbutil.get_industries(db):
            industry = dbutil.get_industry_info(db, idid)
            active = dbutil.get_industry_info(db, idid).active
            item = {
                'id': 'industry%s' % idid,
                '_code': industry.code,
                '_name': industry.name,
                'completionName': [industry.name.lower(), ''.join(lazy_pinyin(industry.name))],
                '_prompt': 'industry',
                'active': active if active else 'Y',
                'ranking_score': round((1.0/(len(industry.name)+1)), 2)
            }
            self.create_index(item, 'completion')

    def delete_useless_indice_completion_keywords(self, db):

        for x in dbutil.get_all_tag(db, [11001]):
            tid = x.id
            self.delete_index('completion', "k{}".format(tid))


def init_kafka(index):

    global producer_search, consumer_search

    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    producer_search = SimpleProducer(kafka)
    consumer_search = KafkaConsumer("keyword_v2", group_id="create search%s index" % index,
                                    bootstrap_servers=[url], auto_offset_reset='smallest')


def create_index_all():

    client = IndexCreator()
    client.create_indice()
    i_client = InteriorIndexCreator()
    i_client.create_indice()
    client.delete_dead_company()


def create_indice_location():

    db = dbcon.connect_torndb()
    client = IndexCreator()
    client.create_indice_completion_locations(db)
    db.close()


def create_indice_keyword():

    db = dbcon.connect_torndb()
    client = IndexCreator()
    client.create_indice_completion_keywords(db)
    db.close()


def create_indice_industry():

    db = dbcon.connect_torndb()
    client = IndexCreator()
    client.create_indice_completion_industry(db)
    db.close()


def create_indice_makeup(index):

    global consumer_search, producer_search

    logging.getLogger('makeup').handlers = []
    logger_makeup = logging.getLogger('makeup')
    logger_makeup.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    logger_makeup.addHandler(stream_handler)

    if int(index) == 1:
        host, port = tsbconfig.get_es_config_1()
        client = IndexCreator(Elasticsearch([{'host': host, 'port': port}]))
    elif int(index) == 2:
        host, port = tsbconfig.get_es_config_2()
        client = IndexCreator(Elasticsearch([{'host': host, 'port': port}]))
    else:
        logger_makeup.error('Not legal elasticsearch config %s' % index)
        return

    db = dbcon.connect_torndb()
    for cid in dbutil.get_company_ids_by_modify(db):
        client.create_single(db, cid)
        logger_makeup.info('makeup %s index created' % cid)
    db.close()


def create_incremental(index):

    global logger_index, consumer_search, producer_search

    if int(index) == 1:
        host, port = tsbconfig.get_es_config_1()
    elif int(index) == 2:
        host, port = tsbconfig.get_es_config_2()
        # client = IndexCreator(Elasticsearch([{'host': host, 'port': port}]))
    else:
        host, port = tsbconfig.get_es_config()
        # client = IndexCreator(Elasticsearch([{'host': host, 'port': port}]))
        logger_index.error('Not legal elasticsearch config %s, using default' % index)
    client = IndexCreator(Elasticsearch([{'host': host, 'port': port}]))
    i_client = InteriorIndexCreator(Elasticsearch([{'host': host, 'port': port}]))

    db = dbcon.connect_torndb()
    init_kafka(index)

    while True:
        logger_index.info('Incremental create search%s index starts' % index)
        try:
            for message in consumer_search:
                try:
                    logger_index.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                                     message.offset, message.key,
                                                                     message.value))
                    action = json.loads(message.value).get('action', 'create')
                    # sb create a new tag
                    if action == 'keyword':
                        client.create_indice_completion_keywords(db, update=True)
                        # consumer_search.commit()
                        logger_index.info('Update keyword')
                        continue
                    cid = json.loads(message.value).get('id') or json.loads(message.value).get('_id')
                    if action == 'create':
                        client.create_single(db, cid)
                        i_client.create_index(db, cid)
                        logger_index.info('incremental %s index created' % cid)
                    elif action == 'delete':
                        if json.loads(message.value).get('aliasId', False):
                            client.create_single(db, cid)
                            i_client.create_index(db, cid)
                            logger_index.info('incremental %s alias deleted' % cid)
                        elif json.loads(message.value).get('artifactId', False):
                            client.create_single(db, cid)
                            i_client.create_index(db, cid)
                            logger_index.info('incremental %s artifact deleted' % cid)
                        else:
                            client.delete_index('company', dbutil.get_company_code(db, cid))
                            client.delete_index('completion', cid)
                            i_client.create_index(db, cid)
                            logger_index.info('incremental %s index deleted' % cid)
                    consumer_search.commit()
                except Exception, e:
                    logger_index.exception('Incr exception# %s \n # %s' % (message, e))
        except Exception, e:
            logger_index.exception('Incr outside exception # %s' % e)


def create_list():

    client = IndexCreator()
    db = dbcon.connect_torndb()
    for c in db.query('select distinct companyId from company_tag_rel where tagid=175747 '
                      'and (active="Y" or active is null);'):
        client.create_single(db, c.companyId)
    db.close()


def clear_msg(index):

    global consumer_search
    init_kafka(index)
    for message in consumer_search:
        action = json.loads(message.value).get('action', 'create')
        if action == 'create':
            consumer_search.commit()
            print message


if __name__ == "__main__":

    print __file__

    if sys.argv[1] == 'full':
        create_index_all()
    elif sys.argv[1] == 'location':
        create_indice_location()
    elif sys.argv[1] == 'keyword' or sys.argv[1] == 'tag':
        create_indice_keyword()
    elif sys.argv[1] == 'industry':
        create_indice_industry()
    elif sys.argv[1] == 'makeup':
        create_indice_makeup(sys.argv[2])
    elif sys.argv[1] == 'clearmsg':
        clear_msg(sys.argv[2])
    elif sys.argv[1] == 'delete':
        client = IndexCreator()
        db = dbcon.connect_torndb()
        client.delete_index('company', sys.argv[2])
        db.close()
    elif sys.argv[1] == 'deletedead':
        client = IndexCreator()
        client.delete_dead_company()
    elif sys.argv[1] == 'single':
        db = dbcon.connect_torndb()
        client = IndexCreator()
        i_client = InteriorIndexCreator()
        client.create_single(db, sys.argv[2])
        i_client.create_index(db, sys.argv[2])
        db.close()
    elif sys.argv[1] == 'pack':
        pack = [int(line.strip()) for line in open('files/pack')]
        db = dbcon.connect_torndb()
        client = IndexCreator()
        i_client = InteriorIndexCreator()
        for cid in pack:
            client.create_single(db, cid)
            i_client.create_index(db, cid)
        db.close()
    elif sys.argv[1] == 'list':
        create_list()
    elif sys.argv[1] == 'incremental' or sys.argv[1] == 'incr':
        create_incremental(sys.argv[2])
