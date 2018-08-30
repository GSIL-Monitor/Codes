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


# logger
loghelper.init_logger("coin", stream=True)
logger_coin = loghelper.get_logger("coin")


class CoinIndexCreator(object):

    def __init__(self, es=None):

        global logger_coin
        self.db = dbcon.connect_torndb()
        self.logger = logger_coin
        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es
        self.logger.info('Coin Client inited')

    def create_indice(self):

        db = dbcon.connect_torndb()
        self.logger.info('Start to create indice')
        self.logger.info(str(self.es.info()))
        self.logger.info('ES Config %s' % str(tsbconfig.get_es_config()))

        self.es.indices.put_mapping("digital_token", mappings.get_digital_token_mapping(), "xiniudata")
        self.logger.info('Digital token mapping created')

        for dtid in dbutil.get_all_digital_token(db):
            try:
                self.create_index(dtid)
                self.logger.info('%s index created' % dtid)
            except Exception, e:
                self.logger.exception('%s failed # %s' % (dtid, e))
        db.close()

    def create_index(self, dtid):

        dt = dbutil.get_digital_token_info(self.db, dtid)
        active = 'Y' if dt.active is None else dt.active
        token = {
            'id': dtid,
            'symbol': dt.symbol.lower(),
            'active': active
        }
        # name
        alias = set()
        alias.add(dt.symbol.lower())
        # short name
        if dt.name:
            alias.add(dt.name.lower().replace(' ', ''))
        # english name
        if dt.enname:
            alias.add(dt.enname.lower())
        # company name
        if dt.companyId:
            full = dbutil.get_company_corporate_name(self.db, dt.companyId, False)
            if full and full.strip():
                alias.add(full.strip().lower())
            cname = dbutil.get_company_name(self.db, dt.companyId)
            if cname and cname.strip():
                alias.add(cname.strip().lower())
        token['dt_alias'] = [name for name in alias if name and name.strip()]

        # sort info
        dtm = dbutil.get_digital_token_market_info(self.db, dtid)
        if dtm:
            token['price'] = dtm.price
            token['increase24h'] = dtm.increase24h
            token['turnover24h'] = dtm.turnover24h
            token['circulationMarketValue'] = dtm.circulationMarketValue
            token['circulationQuantity'] = dtm.circulationQuantity
            token['flowRate'] = dtm.flowRate
            token['totalCirculation'] = dtm.totalCirculation

        self.es.index(index="xiniudata", doc_type='digital_token', id=dtid, body=token)


if __name__ == '__main__':

    bci = CoinIndexCreator()
    bci.create_indice()
