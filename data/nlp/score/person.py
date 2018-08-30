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

import codecs

class FounderScorer(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()

        self.bat = self.__load_namelist('bat')
        self.famousit = self.__load_namelist('company_famous')
        self.u985 = self.__load_namelist('university_985')
        self.u211 = self.__load_namelist('university_211')
        self.uQBFJ = [u'清华', u'北京大学', u'复旦', u'上海交通大学', u'上海交大']
        self.uoverseas = self.__load_namelist('university_overseas')

    def __load_namelist(self, file):
        namelist = set()
        for name in codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../common/dict/', file)):
            namelist |= set(name.replace('\n', '').split('#'))
        return namelist

    def __get_member_from_company(self, cid):
        return {member.memberId for member in
                self.db.query('select distinct memberId from company_member_rel where companyId=%s and'
                         ' (active is null or active="Y") and company_member_rel.type in (5010, 5020);', cid)}

    def score_person(self, pid):

        item = self.db.get('select education, work from member where id=%s and (active is null or active="Y");', pid)
        edus, works = item and str(item.education), item and str(item.work)
        return any(edu in edus for edu in self.u985) * 0.5 + any(edu in edus for edu in self.u211) * 0.3 + \
               any(work in works for work in self.bat) * 0.5 + any(work in works for work in self.famousit) * 0.3 if item else 0

    def score(self, cid):

        mids = self.__get_member_from_company(cid)
        return min(round(max(self.score_person(mid) for mid in mids), 2), 1) if mids else 0

    # 是清北复交；北大是北京大学，但东北大学，西北大学等不是北京大学，需要包含"北大"但去掉"北大学"，数据库已查：没有同时包含"北大"和"北大学"的条目
    def has_QBFJ(self, cid):
        mids = self.__get_member_from_company(cid)
        for mid in mids:
            item = self.db.get('select education from member where id=%s and (active is null or active="Y");', mid)
            item = item and str(item.education)
            if item and any(edu in item or (u'北大' in item and u'北大学' not in item) for edu in self.uQBFJ): return True
        return False

    def has_overseas(self, cid):
        mids = self.__get_member_from_company(cid)
        for mid in mids:
            item = self.db.get('select education from member where id=%s and (active is null or active="Y");', mid)
            if item and any(edu in str(item.education) for edu in self.uoverseas): return True
        return False

    def has_serial_entrepreneur(self, cid):
        mids = tuple(self.__get_member_from_company(cid))
        sql = 'select count(*) as count from member where id in %s and (active is null or active="Y") and description like %s;'
        return bool(mids and self.db.get(sql, mids, '%连续创业者%').count)


if __name__ == '__main__':

    fs = FounderScorer()
    print fs.score_person(253)
    print fs.score_person(7596)
    print fs.score(262)
    print fs.score_person(162562)