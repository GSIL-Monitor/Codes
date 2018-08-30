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
from searchutil import NameSegmenter
from common import dbutil

from copy import copy
from pypinyin import lazy_pinyin
from elasticsearch import Elasticsearch


# logger
loghelper.init_logger("interior", stream=True)
logger_iid = loghelper.get_logger("interior")


class InteriorIndexCreator(object):

    def __init__(self, es=None):

        global logger_iid
        self.db = dbcon.connect_torndb()
        self.logger = logger_iid
        self.domestic_locations = [lname for lid, lname in dbutil.get_all_locations(self.db) if lid < 371]
        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es
        self.logger.info('Interior Client inited')

    def create_indice(self):

        db = dbcon.connect_torndb()
        self.logger.info('Start to create indice')
        self.logger.info(str(self.es.info()))
        self.logger.info('ES Config %s' % str(tsbconfig.get_es_config()))

        for cid in dbutil.get_all_company_id_withna(db):
            try:
                self.create_index(db, cid)
                self.logger.info('%s index created, %s' % (cid, dbutil.get_company_name(db, cid)))
            except Exception, e:
                self.logger.exception('%s failed # %s' % (cid, e))
        db.close()

    def create_index(self, db, cid):

        name = db.get('select name from company where id=%s', cid).name.lower().replace(' ', '')
        code = db.get('select code from company where id=%s', cid).code
        if not code:
            return
        company = {
            'id': cid,
            'name': name,
            'code': code,
            'active': dbutil.get_company_active(self.db, cid)
        }

        # name
        alias = set()
        # short name
        alias.add(name.lower())
        alias.add(''.join(lazy_pinyin(name.lower(), errors='ignore')))
        # full name
        full = dbutil.get_company_corporate_name(self.db, cid, False)
        if full and full.strip():
            alias.add(full.lower())
            short_full = copy(full)
            for location in self.domestic_locations:
                short_full = short_full.replace(location, '')
            alias.add(short_full.lower())
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

        company['i_alias'] = [name for name in alias if name and name.strip()]
        self.es.index(index="xiniudata", doc_type='interior', id=code, body=company)

    def valid_name(self, name):

        name = name.replace(u'・', u'-').replace(u'－', u'-').split(u'-')[0]
        if len(name) < 20:
            return name.lower()
        return False


if __name__ == '__main__':

    iic = InteriorIndexCreator()
    iic.create_indice()
