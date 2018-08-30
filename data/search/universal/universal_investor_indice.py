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

import json
import hashlib
from datetime import timedelta, datetime
from copy import copy

from pypinyin import lazy_pinyin
from kafka import KafkaClient, SimpleProducer, KafkaConsumer
from elasticsearch import Elasticsearch

loghelper.init_logger('universal-i', stream=True)
logger_universali_index = loghelper.get_logger('universal-i')


class UniversalInvestorIndexCreator(object):

    def __init__(self, es=None):

        global logger_universali_index
        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es
            logger_universali_index.info('Universal Index Creator inited')

    def __check(self):

        global logger_universali_index
        if not self.es.indices.exists(["xiniudata2"]):
            logger_universali_index.info('Creating index xiniudata2')
            self.es.indices.create("xiniudata2")
            logger_universali_index.info('Created')
        self.es.indices.put_mapping("investor", mappings.get_universal_investor_mapping(), "xiniudata2")
        logger_universali_index.info('Universal investor mapping created')

    def create_indice(self):

        global logger_universali_index

        self.__check()
        today = datetime.today().date()
        year2018 = datetime.strptime('2018-01-01', '%Y-%M-%d')
        db = dbcon.connect_torndb()
        logger_universali_index.info('Start to create indice')
        logger_universali_index.info(str(self.es.info()))
        logger_universali_index.info('ES Config %s' % str(tsbconfig.get_es_config()))
        for investor in dbutil.get_all_investor_info(db, False):
            try:
                self.create_single(db, investor, (year2018, today))
                logger_universali_index.info('%s index created' % investor.id)
            except Exception, e:
                logger_universali_index.exception('%s failed # %s' % (investor.id, e))
        db.close()

    def create_single(self, db, i, period):

        if not i.code:
            data = "%s%s%s" % (i.id, i.name, datetime.now())
            code = hashlib.md5(data).hexdigest()
            dbutil.update_investor_code(db, i.id, code)
            return
        investor = {
            'iid': i.code,
            'name': i.name.strip().lower(),
            'location': i.locationId,
            'online': True if i.online == 'Y' else False,
            'active': i.active
        }
        alias = set()
        alias.add(i.name.strip().lower())
        other_names = [item for item in dbutil.get_investor_alias(db, i.id) if item.strip()]
        alias.update(set(other_names))
        alias = [name.decode('utf-8').strip() for name in alias]
        alias.extend([''.join(lazy_pinyin(name, errors='ignore')) for name in alias])
        for alia in copy(alias):
            alias.append(alia.replace(u'投资', u'').replace(u'基金', u'').replace(u'创投', u'').replace(u'资本', u''))
        alias.extend([name.lower() for name in alias])
        alias = list(set(alias))
        investor['alias'] = alias
        candidates = [name for (_, name) in dbutil.get_investor_alias_candidates(db, i.id)]
        investor['candidate'] = candidates
        for tag, weight in json.loads(dbutil.get_investor_tags(db, i.id, 0)).items():
            investor.setdefault('investor_tag', []).append({'tag': tag.strip().lower(), 'confidence': weight})
        investor['portfolio_number'] = len(list(dbutil.get_investor_portfilio(db, i.id)))
        investor['portfolio_number_annual'] = len(list(dbutil.get_investor_portfilio(db, i.id, period)))
        self.es.index(index="xiniudata2", doc_type='investor', id=i.code, body=investor)


if __name__ == '__main__':

    if len(sys.argv) > 1:
        if int(sys.argv[1]) == 1:
            host, port = tsbconfig.get_es_config_1()
            uic = UniversalInvestorIndexCreator(Elasticsearch([{'host': host, 'port': port}]))
        elif int(sys.argv[1]) == 2:
            host, port = tsbconfig.get_es_config_2()
            uic = UniversalInvestorIndexCreator(Elasticsearch([{'host': host, 'port': port}]))
        else:
            uic = UniversalInvestorIndexCreator()
    else:
        uic = UniversalInvestorIndexCreator()
    uic.create_indice()
