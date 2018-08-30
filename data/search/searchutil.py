# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

import json
import itertools
from datetime import datetime

import db as dbcon
from nlp.common import dbutil, dicts
from common import dbutil
from nlp.common.zhtools.segment import Segmenter
from nlp.common.zhtools import word_filter


class Identifier(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.tpfj = set([u'清华', u'北大', u'北京大学', u'复旦', u'上海交通大学'])
        self.u985 = set([x.termName.strip()
                         for x in self.db.query('select termName from thesaurus where termType=42010;')])
        self.u211 = set([x.termName.strip()
                         for x in self.db.query('select termName from thesaurus where termType=42020;')]) | self.u985

        self.bat = set([x.termName.strip()
                        for x in self.db.query('select termName from thesaurus where termType=43010;')])
        self.tmt = set([x.termName.strip()
                        for x in self.db.query('select termName from thesaurus where termType=43020;')]) | self.bat
        self.top500 = set(dicts.get_company_top500())

    def identify_education(self, intro):

        for u in self.u985:
            if u in intro:
                yield 42010
                break
        for u in self.u211:
            if u in intro:
                yield 42020
                break
        for u in self.tpfj:
            if u in intro:
                yield 42030
                break

    def identify_work(self, intro):

        for c in self.bat:
            if c in intro:
                yield 43010
                break
        for c in self.tmt:
            if c in intro:
                yield 43020
                break
        for c in self.top500:
            if c in intro:
                yield 43030
                break

    def identify(self, cid):

        """
        member and work info
        :param cid:
        :return:
        """
        members = self.db.query('select member.education, member.work from member, company_member_rel '
                                'where company_member_rel.companyId=%s and company_member_rel.memberId=member.id;', cid)
        if not members or len(members) == 0:
            return []

        educations, works = [member.education for member in members], [member.work for member in members]
        educations = [self.identify_education(education) for education in educations if education and education.strip()]
        educations = set(itertools.chain(*[list(education) for education in educations if education]))
        works = [self.identify_work(work) for work in works if work and work.strip()]
        works = set(itertools.chain(*[list(work) for work in works if work]))
        results = educations | works
        return list(results)


class NameSegmenter(object):

    def __init__(self):

        self.seg = Segmenter()
        self.wfilter = word_filter.get_search_name_filter()

    def segment(self, name):

        name = name.replace(u'\(', '').replace(u'\)', '').replace(u'（', '').replace(u'）', '')
        if len(name) > 4:
            return ' '.join(self.wfilter(list(self.seg.cut(name))))
        return


def generate_sector_filters():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    for tag in dbutil.get_tags_by_type(db, [11054]):
        cids = dbutil.get_company_from_tag(db, tag.id)
        if not cids:
            continue
        sectors = dbutil.get_companies_sector_tag(db, cids, [1], 'novelty')
        mongo.keywords.sector_filters.update({'source': tag.name, 'filter_type': 'tag'},
                                             {'$set': {'sectors': sectors, 'modifyTime': datetime.utcnow()}}, True)
    for idid, _ in dbutil.get_industries(db):
        cids = [c.companyId for c in dbutil.get_industry_companies(db, idid)]
        if not cids:
            continue
        sectors = dbutil.get_companies_sector_tag(db, cids, [1], 'novelty')
        mongo.keywords.sector_filters.update({'source': idid, 'filter_type': 'industry'},
                                             {'$set': {'sectors': sectors, 'modifyTime': datetime.utcnow()}}, True)
    for tpid in dbutil.get_all_topics(db):
        cids = [c.companyId for c in dbutil.get_topic_companies(db, tpid)]
        if not cids:
            continue
        sectors = dbutil.get_companies_sector_tag(db, cids, [1], 'novelty')
        mongo.keywords.sector_filters.update({'source': tpid, 'filter_type': 'topic'},
                                             {'$set': {'sectors': sectors, 'modifyTime': datetime.utcnow()}}, True)
    for iid, name in dbutil.get_all_investor(db):
        sectors = dbutil.filter_sector_tags(db, json.loads(dbutil.get_investor_tags(db, iid, 0)).keys())
        mongo.keywords.sector_filters.update({'source': name, 'filter_type': 'investor'},
                                             {'$set': {'sectors': sectors, 'modifyTime': datetime.utcnow()}}, True)
    db.close()


def delete_from_collection(colid, ccode):

    db = dbcon.connect_torndb()
    cid = dbutil.get_id_from_code(db, ccode)
    dbutil.rm_collection_company(db, colid, cid)
    db.close()


def add2collection(colid, ccode):

    db = dbcon.connect_torndb()
    cid = dbutil.get_id_from_code(db, ccode)
    dbutil.update_collection(db, colid, cid)
    db.close()


def get_online_investors():

    db = dbcon.connect_torndb()
    return set(dbutil.get_investor_alias(db, *dbutil.get_online_investors(db))) | \
           set([dbutil.get_investor_name(db, iid) for iid in dbutil.get_online_investors(db)])


if __name__ == '__main__':

    print __file__

    # ns = NameSegmenter()
    # print ns.segment(u'上海汇翼科技有限公司')
    if sys.argv[1] == 'rmcollectioncompany' or sys.argv[1] == 'rmcolcid':
        delete_from_collection(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'addcollectioncompany' or sys.argv[1] == 'addcolcid':
        add2collection(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'filters':
        generate_sector_filters()
