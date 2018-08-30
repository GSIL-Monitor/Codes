# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
from common import dbutil
from score.completeness import ScorerCompleteness
from classifier.context_type import ContextClassifier

import json
import re

english_space = re.compile(r'([a-zA-Z])\s+([a-zA-Z])')
multi_period = re.compile(u'。+')

MAX_PARAGRAGH_LEN = 250
MED_PARAGRAGH_LEN = 50


class Context(object):

    def __init__(self, cid, db=None, type='company'):

        self.db = db if db else dbcon.connect_torndb()
        self.cid = cid
        self.idtype = type

    def cut(self):

        global MAX_PARAGRAGH_LEN
        count = 0  # count of empty line
        for scid, content in self.__get_context():
            for i, paragraph in enumerate(content.split('\n')):
                if paragraph.strip() and len(paragraph.strip()) < MAX_PARAGRAGH_LEN:
                    yield scid, {'position': i, 'emptyline': count}, paragraph
                    count = 0
                elif paragraph.strip() and len(paragraph.strip()) >= MAX_PARAGRAGH_LEN:
                    for si, piece in enumerate(self.__process_complex_paragraph(paragraph.strip())):
                        yield scid, {'position': i, 'subposition': si, 'emptyline': count}, piece
                else:
                    count += 1

    def record(self, confidence=1, type=30000):

        dbutil.rm_old_context(self.db, self.cid)
        for scid, info, content in self.cut():
            dbutil.update_company_context(self.db, scid, content, json.dumps(info), confidence, type)

    def __get_context(self):

        if self.idtype == 'company':
            for scid, content in dbutil.get_source_company_description_from_cid(self.db, self.cid):
                yield scid, content
            for scid, brief in dbutil.get_source_company_brief_from_cid(self.db, self.cid):
                yield scid, brief
        elif self.idtype == 'source_company':
            scid, content = dbutil.get_source_company_description(self.db, self.cid)
            if content.strip():
                yield scid, content
            scid, brief = dbutil.get_source_company_brief(self.db, self.cid)
            if brief.strip():
                yield scid, brief
            scid, product_description = dbutil.get_source_company_productDesc(self.db, self.cid)
            if product_description and product_description.strip():
                yield scid, brief

    def __process_complex_paragraph(self, p):

        global MAX_PARAGRAGH_LEN
        lg = self.__lagou_paragraph(p)
        if lg:
            return lg
        return list(self.__general_paragraph(p))

    def __lagou_paragraph(self, pg):

        global english_space, MED_PARAGRAGH_LEN
        pgl = english_space.sub(r'\1#es\2', pg)
        pgs = pgl.split()
        if 1 < len(pgs) < len(pg)/MED_PARAGRAGH_LEN:
            return pgs
        return []

    def __general_paragraph(self, pg):

        global multi_period, MED_PARAGRAGH_LEN
        pgg = multi_period.sub(u'。', pg)
        pgs = pgg.split(u'。')
        candidate = ''
        for sentence in pgs:
            candidate += sentence
            if len(candidate) > MED_PARAGRAGH_LEN:
                yield candidate
                candidate = ''
        if candidate.strip():
            yield candidate


def annotate(query=None):

    dbc = dbcon.connect_torndb()
    scorer = ScorerCompleteness()
    b = False
    annotated = set([
        x.companyId for x in dbc.query('select source_company.companyId from source_company, source_context '
                                       'where source_context.type!=30000 and '
                                       'source_context.sourceCompanyId=source_company.id;')
    ])

    if not query:
        query = 'select company.* from company, source_company where source_company.companyId=company.id and ' \
                'source_company.source=13050 order by length(source_company.description) desc;'
    elif query.isdigit():
        query = 'select * from company where id=%s;' % query

    for item in dbc.query(query):
        if item.id in annotated:
            continue
        if b:
            break
        if scorer.score(dbc, item.id) < 0.3:
            continue
        print 'processing', item.id, item.name
        context = Context(item.id, db=dbc)
        for scid, feature, content in context.cut():
            print scid, content
            inp = raw_input('Assign:')
            if inp == 'exit' or inp == 'q':
                b = True
                inp = raw_input('Assign:')
            ctype = int(inp) + 30000
            dbutil.update_company_context(dbc, scid, content, json.dumps(feature), 1, ctype)

    dbc.close()


def classify_noise():

    db = dbcon.connect_torndb()
    classifier = ContextClassifier()
    for item in db.query('select distinct id from company;'):
        try:
            context = Context(item.id, db)
            __process_pieces(context, db, classifier)
        except Exception, e:
            print item.id, e
    db.close()


def classify_noise_incr(scid, cf=None):

    db = dbcon.connect_torndb()
    classifier = cf if cf else ContextClassifier()
    context = Context(scid, db, 'source_company')
    try:
        __process_pieces(context, db, classifier)
    except Exception, e:
        print scid, e
    db.close()


def classify_noise_makeup():

    db = dbcon.connect_torndb()
    classifier = ContextClassifier()
    exists = set(item.scid for item in db.query('select distinct sourceCompanyId as scid from source_context;'))
    for item in db.iter('select distinct id from source_company'):
        if item.id in exists:
            continue
        print 'processing scid', item.id
        classify_noise_incr(item.id, classifier)
    db.close()


def __process_pieces(context, db, classifier):

    pieces = list(context.cut())
    if len(pieces) < 1:
        return
    scids = [x[0] for x in pieces]
    features = [x[1] for x in pieces]
    contents = [x[2] for x in pieces]
    for scid in set(scids):
        dbutil.rm_old_context_source(db, scid)
    confidences = [x[1] for x in classifier.classify_noise_prob(contents)]
    for i in xrange(len(scids)):
        dbutil.update_company_context(db, scids[i], contents[i], json.dumps(features[i]),
                                      *infer_type(confidences[i]))


def infer_type(confidence):

    if confidence > 0.7:
        return round(confidence, 2), 30010
    elif confidence < 0.4:
        return round((1-confidence), 2), 30020
    return 0.5, 30000


if __name__ == '__main__':

    if sys.argv[1] == 'test':
        annotate(sys.argv[2])
    elif sys.argv[1] == 'noise':
        classify_noise()
    elif sys.argv[1] == 'makeup':
        classify_noise_makeup()
    else:
        annotate()