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

import json
from math import log
from copy import copy
from pypinyin import lazy_pinyin
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

# logger
loghelper.init_logger("completion", stream=True)
logger_completion = loghelper.get_logger("completion")


class CompletionIndexCreator(object):

    def __init__(self, es=None):

        global logger_completion
        self.db = dbcon.connect_torndb()
        self.logger = logger_completion
        if not es:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])
        else:
            self.es = es
        self.searchable_tag_types = [11011, 11012, 11013, 11100, 11110, 11111, 11050, 11051, 11052, 11053, 11054]
        if not self.es.indices.exists(["xiniudata2"]):
            self.logger.info('Creating index xiniudata2')
            self.es.indices.create("xiniudata2")
            self.logger.info('Created')
        self.es.indices.put_mapping("completion", mappings.get_completion_mapping(), "xiniudata2")
        self.logger.info('Completion Client inited')

    def create_indice_completion_locations(self):

        location_score = 1
        for lid, lname in dbutil.get_all_locations(self.db):
            if len(lname) < 1:
                self.logger.exception('%s location has no name' % lid)
                continue
            item = {
                'id': 'l%s' % lid,
                '_name': lname,
                'completionName': [lname.lower(), ''.join(lazy_pinyin(lname))],
                '_prompt': 'location',
                'ranking_score': location_score * round((1.0/len(lname)), 2),
                'active': "Y",
                'online': True
            }
            self.es.index(index="xiniudata2", doc_type="completion", id='l%s' % lid, body=item)

    def create_indice_completion_keywords(self, update=False):

        if not update:
            for x in dbutil.get_all_tag(self.db, self.searchable_tag_types):
                tid, tname = x.id, x.name
                item = {
                    'id': 'k%s' % tid,
                    '_name': tname,
                    'completionName': [tname.lower(), ''.join(lazy_pinyin(tname))],
                    '_prompt': 'keyword',
                    'ranking_score': round((1.0/(len(tname)+1)), 2),
                    'active': "Y",
                    'online': True
                }
                self.es.index(index="xiniudata2", doc_type="completion", id='k%s' % tid, body=item)
        else:
            for x in dbutil.get_all_tag(self.db, self.searchable_tag_types, True):
                tid, tname = x.id, x.name
                item = {
                    'id': 'k%s' % tid,
                    '_name': tname,
                    'completionName': [tname.lower(), ''.join(lazy_pinyin(tname))],
                    '_prompt': 'keyword',
                    'ranking_score': round((1.0/(len(tname)+1)), 2),
                    'active': "Y",
                    'online': True
                }
                self.es.index(index="xiniudata2", doc_type="completion", id='k%s' % tid, body=item)

    def delete_useless_indice_completion_keywords(self):

        for x in dbutil.get_all_tag(self.db, [11001]):
            tid = x.id
            self.delete_index('completion', "k{}".format(tid))

    def create_indice_completion_industries(self):

        for idid, _ in dbutil.get_industries(self.db):
            industry = dbutil.get_industry_info(self.db, idid)
            active = dbutil.get_industry_info(self.db, idid).active
            active = active if active else 'Y'
            item = {
                'id': 'industry%s' % idid,
                '_code': industry.code,
                '_name': industry.name,
                'completionName': [industry.name.lower(), ''.join(lazy_pinyin(industry.name))],
                '_prompt': 'industry',
                'active': active,
                'online': True if active == 'Y' else False,
                'ranking_score': round((1.0/(len(industry.name)+1)), 2)
            }
            self.es.index(index="xiniudata2", doc_type="completion", id='industry%s' % idid, body=item)

    def create_single_investor(self, iid):

        iname = dbutil.get_investor_name(self.db, iid)
        code = dbutil.get_investor_info(self.db, iid).code
        if len(iname) < 1:
            self.logger.exception('%s investor has no name' % iid)
            return
        alias = set()
        alias.add(iname.strip().lower())
        other_names = [item for item in dbutil.get_investor_alias(self.db, iid) if item.strip()]
        alias.update(set(other_names))
        alias = [name.decode('utf-8').strip() for name in alias]
        alias.extend([''.join(lazy_pinyin(name, errors='ignore')) for name in alias])
        for alia in copy(alias):
            alias.append(alia.replace(u'投资', u'').replace(u'基金', u'').replace(u'创投', u'').replace(u'资本', u''))
        alias.extend([name.lower() for name in alias])
        alias = list(set(alias))
        # tags_scores = {k: round(v, 2) for k, v in sorted(json.loads(dbutil.get_investor_tags(self.db, iid, 0)).items(),
        #                                                  key=lambda x: -x[1])[:30]}
        # tags = [tag.lower() for tag, _ in tags_scores.items()]
        item = {
            'id': 'i%s' % iid,
            '_code': code,
            '_name': iname,
            'completionName': alias,
            '_prompt': 'investor',
            'ranking_score': round(log(dbutil.get_investor_info(self.db, iid).get('fundingCntFrom2017') or 1, 2), 2),
            'online': True if dbutil.get_investor_info(self.db, iid).online == 'Y' else False,
            'active': dbutil.get_investor_info(self.db, iid).active
            # 'features': tags,
            # 'feature_scores': json.dumps(tags_scores)
        }
        self.es.index(index="xiniudata2", doc_type="completion", id='i%s' % iid, body=item)

    def create_single_company(self, cid):

        alias = set()
        name = dbutil.get_company_name(self.db, cid).lower().replace(' ', '')
        code = dbutil.get_company_code(self.db, cid)
        alias.add(name.lower())
        alias.add(''.join(lazy_pinyin(name.lower())))
        # full name
        full = dbutil.get_company_corporate_name(self.db, cid, False)
        if full and full.strip():
            alias.add(full.lower())
            alias.add(full.lower().replace(u'北京', '').replace(u'上海', '').replace(u'深圳', ''))
        # alias
        aliass = dbutil.get_alias_idname(self.db, cid)
        if aliass and len(aliass) < 20:
            alias.update([self.valid_name(aname) for _, aname in aliass if self.valid_name(aname)])
        # corporate name
        corporate = dbutil.get_company_corporate_name(self.db, cid)
        if corporate and corporate.strip():
            alias.add(corporate.lower())
        # corporate alias
        corporate_alias = dbutil.get_corporate_alias(self.db, cid)
        if corporate_alias and len(corporate_alias) < 20:
            alias.update([self.valid_name(aname) for aname in corporate_alias if self.valid_name(aname)])
        # check if there is a relevant digital coin
        dt = dbutil.get_company_digital_coin_info(self.db, cid)
        if dt:
            alias.add(dt.symbol.lower())
            # short name
            if dt.name:
                alias.add(dt.name.lower().replace(' ', ''))
            # english name
            if dt.enname:
                alias.add(dt.enname.lower())
        active = dbutil.get_company_active(self.db, cid)
        # create indice names
        completion = {
            'id': 'c%s' % cid,
            '_code': code,
            '_name': name,
            'completionName': list(set(alias)),
            '_prompt': 'name',
            'online': True if active == 'Y' else False,
            'active': active
        }
        self.es.index(index="xiniudata2", doc_type='completion', id='c%s' % cid, body=completion)

    def valid_name(self, name):

        name = name.replace(u'・', u'-').replace(u'－', u'-').split(u'-')[0]
        if len(name) < 20:
            return name.lower()
        return False

    def delete_index(self, doc_type, id):

        try:
            self.es.delete('xiniudata2', doc_type, id)
        except NotFoundError, efe:
            pass

    def create_indice_completion_companies(self):

        dbbk = dbcon.connect_torndb()
        for cid in dbutil.get_all_company_id_withna(dbbk):
            try:
                self.create_single_company(cid)
            except Exception, e:
                self.logger.exception('Fail to process %s' % cid)
        dbbk.close()

    def create_indice_completion_investors(self):

        dbbk = dbcon.connect_torndb()
        for iid in dbutil.get_all_investor_withna(dbbk):
            self.create_single_investor(iid)
        dbbk.close()


if __name__ == '__main__':

    cic = CompletionIndexCreator()
    if sys.argv[1] == 'company':
        if sys.argv[2] == 'full':
            cic.create_indice_completion_companies()
    if sys.argv[1] == 'investor':
        if sys.argv[2] == 'full':
            cic.create_indice_completion_investors()
    if sys.argv[1] == 'location':
        cic.create_indice_completion_locations()
    if sys.argv[1] == 'industry':
        cic.create_indice_completion_industries()
    if sys.argv[1] == 'keyword':
        cic.create_indice_completion_keywords()
    if sys.argv[1] == 'full':
        logger_completion.info('Creating index of keyword')
        cic.create_indice_completion_keywords()
        logger_completion.info('Creating index of location')
        cic.create_indice_completion_locations()
        logger_completion.info('Creating index of industry')
        cic.create_indice_completion_industries()
        logger_completion.info('Creating index of investor')
        cic.create_indice_completion_investors()
        logger_completion.info('Creating index of company')
        cic.create_indice_completion_companies()
