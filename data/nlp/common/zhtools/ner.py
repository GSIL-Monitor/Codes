# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
from common import dicts, dbutil
from score.completeness import ScorerCompleteness

import time
import jieba
jieba.load_userdict(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict.txt'))
from jieba import posseg
import logging

# logging
logging.getLogger('ner').handlers = []
logger_ner = logging.getLogger('ner')
logger_ner.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_ner.addHandler(stream_handler)


class SimpleNER(object):

    min_complete_score = 0.15
    default_freq = 30

    def __init__(self):

        global logger_ner
        self.db = dbcon.connect_torndb()
        self.scorer = ScorerCompleteness()
        self.logger = logger_ner

    def train(self):

        backup_db = dbcon.connect_torndb()
        for result in self.db.iter('select id, name, fullName from company;'):
            cid, name, fname = result.id, result.name, result.fullName
            # self.logger.info('Processing %s' % cid)
            if self.scorer.score(backup_db, cid) < self.min_complete_score:
                continue
            if name and 1 < len(name) < 8:
                jieba.add_word(name, freq=self.default_freq, tag='cn')
            if fname and 1 < len(fname) < 8:
                jieba.add_word(fname, tag='cn')
        self.logger.info('Company name processed')
        backup_db.close()
        # for result in self.db.iter('select companyId, name from artifact;'):
        #     if self.scorer.score(backup_db, result.companyId) < self.min_complete_score:
        #         continue
        #     if result.name and 1 < len(result.name) < 8:
        #         jieba.add_word(result.name, freq=self.default_freq, tag='cn')
        # self.logger.info('Names loaded for SimpleNER')

    def chunk(self, seq):

        return posseg.cut(seq)


class CompanyNER(SimpleNER):

    def __init__(self):

        SimpleNER.__init__(self)
        self.common_names = set(dicts.get_common_cname())
        self.train()

    def train(self):

        db2 = dbcon.connect_torndb()
        for result in self.db.iter('select company.name as name from company, funding '
                                   'where companyId=company.id and (company.active is null or company.active="Y") and '
                                   '(funding.active is null or funding.active="Y");'):
            self.__add_name(result.name)
        for result in self.db.iter('select c.id id, c.name name from company c, corporate cp '
                                   'where cp.establishDate>"2009-12-31" and c.corporateId=cp.id '
                                   'and (c.active is null or c.active="Y") and c.name is not null;'):
            cscore = dbutil.get_company_score(db2, result.id)
            if cscore < 0.2:
                continue
            if dbutil.get_company_score(db2, result.id, 37030) == 0 and cscore < 0.75:
                continue
            self.__add_name(result.name)
        self.logger.info('Company name processed')

    def __add_name(self, name):

        # self.logger.info('Processing %s' % cid)

        if not name.strip():
            return
        if name.isdigit():
            return
        if name in self.common_names:
            return
        if name and 1 < len(name) < 8:
            jieba.add_word(name, freq=self.default_freq, tag='cn')

if __name__ == '__main__':

    print __file__
    # ner = SimpleNER()
    start = time.time()
    ner = CompanyNER()
    for x in ner.chunk(u'华文食品是一家基础扎实，发展势头强劲的创业公司，处于行业领先地位的好公司，其董事长周劲松先生为人仁厚诚信，行业经验丰富'):
        print type(x), x.word, x.flag
    print time.time() - start