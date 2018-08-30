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


class CompanyTagsRelevance(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()

    def score(self, cid, utags):

        ctags = dbutil.get_company_tags_idname(self.db, cid)
        if ctags:
            ctags = {x[0]: x[2] for x in ctags}
            return round(self.weighted_jaccard(ctags, utags), 4)
        return 0

    def weighted_jaccard(self, tags1, tags2):

        sum_up, sum_down = 0, 0
        for tag in (set(tags1.keys()) | set(tags2.keys())):
            sum_up += (min(tags1.get(tag, 0), tags2.get(tag, 0)) or 0)
            sum_down += (max(tags1.get(tag, 0), tags2.get(tag, 0)) or 1)
        return float(sum_up)/sum_down


class CompanyUserRelevance(CompanyTagsRelevance):

    def __init__(self):

        CompanyTagsRelevance.__init__(self)
        self.non_trusted_source_discount = 0.7
        self.non_yellow_label_discount = 0.5

    def score(self, cid, utags):

        tagscore = CompanyTagsRelevance.score(self, cid, utags)

        if not dbutil.get_company_source(self.db, cid, justify=True):
            tagscore *= self.non_trusted_source_discount

        if not set(x[0] for x in dbutil.get_company_tags_idname(self.db, cid)) & set(dbutil.get_yellow_tags(self.db)):
            tagscore *= self.non_yellow_label_discount

        return round(tagscore, 4)


def test(uid):

    db = dbcon.connect_torndb()
    cur = CompanyUserRelevance()
    utags = dict.fromkeys(dbutil.get_user_sectors(db, uid, True), 5)
    print cur.score(240552, utags)

if __name__ == '__main__':

    test(sys.argv[1])