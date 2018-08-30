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

from abc import abstractmethod
from math import log10
from datetime import datetime, timedelta

from completeness import ScorerCompleteness
from job import ScorerJob
from person import FounderScorer


class EndScorer(object):

    @abstractmethod
    def score(self, db, cid):
        pass


class PushScorer(EndScorer):

    job_weight = 0.1
    founder_weight = 0.8

    def __init__(self):

        self.complete_scorer = ScorerCompleteness()
        self.job_scorer = ScorerJob()
        self.founder_scorer = FounderScorer()

    def score(self, db, cid):

        return self.complete_scorer.score(db, cid) + self.job_weight * self.job_scorer.score(db, cid) + \
               self.founder_weight * self.founder_scorer.score(db, cid)

    def promote_general(self, db):

        # yellow tags with in 3 years
        results = db.query('select distinct companyId from company, company_tag_rel, tag, corporate '
                           'where tag.id=tagId and company.id=companyId and tag.type=11100 '
                           'and (company.active is null or company.active="Y") '
                           'and corporate.id=company.corporateId and corporate.establishDate>"2013-12-31";')
        results = [item.companyId for item in results]
        # fas within 3 months
        results.extend([item.companyId for item in db.query('select distinct companyId from company_fa '
                                                            'where source<13200 and (active is null or active="Y") and '
                                                            'publishDate>date_add(curdate(), interval - 3 month);')])
        # company fa others within 3 years
        results.extend([item.companyId for item in db.query('select distinct companyId '
                                                            'from company_fa, company c, corporate cp'
                                                            'where company_fa.source>=13200 and companyId=c.id '
                                                            'and cp.establishDate>"2013-12-31" and c.corporateId=cp.id '
                                                            'and (company_fa.active is null or company_fa.active="Y") '
                                                            'and (c.active is null or c.active="Y");')])

        # shut down
        results = filter(lambda x: dbutil.get_company_status(db, x) not in (2020, 2025), results)

        # locations = {}
        # for result in set(results):
        #     l = db.get('select locationId from company where id=%s;', result).locationId
        #     locations[l] = locations.get(l, 0) + 1
        # for k, v in sorted(locations.items(), key=lambda x: -x[1])[:10]:
        #     print k, v
        return set(results)


class RankScorer(EndScorer):

    """
    for search
    score = count_of_yellow + 1 - time_deduction + completeness
    """

    def __init__(self):

        self.complete_scorer = ScorerCompleteness()

    def score(self, db, cid):

        s1 = dbutil.get_company_score(db, cid, 37010)
        s1 = 1 if s1 >= 0.5 else s1
        s2 = (len(dbutil.get_company_tags_yellow(db, cid, False)) + 1 -
              dbutil.get_company_yellow_time_deduction(db, cid)) / 9
        month3 = datetime.now() - timedelta(days=90)
        s3 = (log10(len(dbutil.get_company_messages(db, cid, 'Y', month3)) + 1)) / 4
        return round((s1 + s2 + s3), 2)


def score_rank_all():

    db = dbcon.connect_torndb()
    scorer = RankScorer()
    for result in iter(db.query('select distinct id from company where (active is null or active="Y");')):
        score = scorer.score(db, result.id)
        dbutil.update_company_score(db, result.id, score, 37020)
    db.close()


if __name__ == '__main__':

    print __file__
    score_rank_all()