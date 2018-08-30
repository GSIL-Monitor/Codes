# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../nlp'))

import loghelper
import db as dbcon
import config as tsbconfig
import mappings
from common import dbutil

from elasticsearch import Elasticsearch
from pymongo import ASCENDING


# logger
loghelper.init_logger("amac", stream=True)
logger_amac = loghelper.get_logger("amac")


class AMACIndexCreator(object):

    def __init__(self, es=None):

        global logger_amac
        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        self.logger = logger_amac
        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es
        self.logger.info('Coin Client inited')

    def create_indice(self):

        if not self.es.indices.exists(["xiniudata2"]):
            self.logger.info('Creating index xiniudata')
            self.es.indices.create("xiniudata2")
            self.logger.info('Created')
        self.logger.info('Start to create indice of amac')
        self.logger.info(str(self.es.info()))
        self.logger.info('ES Config %s' % str(tsbconfig.get_es_config()))
        self.es.indices.put_mapping("amac", mappings.get_amac_mapping(), "xiniudata2")

        mongo_back = dbcon.connect_mongo()
        coordinate = mongo_back.amac.fund.find().sort('_id', ASCENDING).limit(1)[0]
        self.create_single(coordinate)
        self.logger.info('Coordinate prepared')
        coordinate = coordinate.get('_id')
        end_flag = False
        while not end_flag:
            end_flag = True
            for fund in mongo_back.amac.fund.find({'_id': {'$gt': coordinate}}).sort('_id', ASCENDING).limit(5000):
                coordinate = fund['_id']
                end_flag = False
                try:
                    self.create_single(fund)
                    self.logger.info('%s index created' % fund['_id'])
                except Exception, e:
                    self.logger.exception('Fail to index %s, due to %s' % (coordinate, e))

    def create_single(self, amac_fund):

        amac = {'amacid': str(amac_fund['_id'])}
        alias = set()
        amac['name'] = amac_fund['fundName']
        alias.add(amac_fund['fundName'])
        amac['fundCode'] = amac_fund['fundCode']
        amac['manager'] = amac_fund['managerName']
        alias.add(amac_fund['managerName'])
        # manager
        manager = self.mongo.amac.manager.find_one({'managerName': amac_fund['managerName']})
        if manager:
            amac['managerId'] = str(manager['_id'])
            amac['regCode'] = manager.get('regCode')
        names = [n for n in [amac_fund['managerName'], amac_fund['fundName']] if n and n.strip()]
        iid = dbutil.locate_investor_alias(self.db, names)
        if iid:
            amac['gp'] = iid
            alias.update(dbutil.get_investor_short_alias(self.db, iid))
        amac['amac_alias'] = list(alias)
        self.es.index(index="xiniudata2", doc_type='amac', id=amac_fund['_id'], body=amac)


if __name__ == '__main__':

    amac = AMACIndexCreator()
    amac.create_indice()
