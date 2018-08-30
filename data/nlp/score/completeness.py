# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
from common import dbutil, dicts


class ScorerCompleteness(object):

    """
    compute the completeness score of a company, from following points of view
    site: whether company has website/app url
    infos: the completeness of company properties such as location, funding, etc. normalize to 1
    intro: the quality of company description, normalize to 1
    member: the completeness of member infos, normalize to 1
    news: the quality of company news, normalize to 1
    """

    def __init__(self):

        self.points = ['infos', 'intro']
        self.lack_trusted_source_discount = 0.75
        self.non_truested_source_discount = 0.5

    def score(self, db, cid):

        return self.__score_infos(db, cid)

    def __score_infos(self, db, cid):

        aspects, total = 0.0, 0.0
        num_aspects = 0

        # description
        count = db.get('select count(*) c from company where id=%s and description is not null;', cid).c
        aspects += (count > 0)
        total += count
        num_aspects += 1

        # verified
        count = db.get('select count(*) c from company where id=%s and modifyUser is not null;', cid).c
        aspects += (count > 0)
        total += count
        num_aspects += 1

        # artifact
        count = db.get('select count(distinct type) as count from artifact where companyId=%s', cid).count
        aspects += (count > 0)
        total += count
        num_aspects += 1

        # member
        count = db.get('select count(*) as count from company_member_rel where companyId=%s', cid).count
        aspects += (count > 0)
        total += count
        num_aspects += 1

        sources = dbutil.get_company_source(db, cid)
        if (len(set(sources)) == 1 and 13050 in sources) or len(sources) > 5:
            discount = self.non_truested_source_discount
        else:
            discount = 1 if dbutil.get_company_source(db, cid, justify=True) else self.lack_trusted_source_discount
        return round((aspects/(2 * num_aspects) + min(0.5, total/10)) * discount, 3)


class ScorerVerifiedCompleteness(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()

    def score(self, cid):

        verified = sum([dbutil.get_company_verified(self.db, cid),
                        dbutil.get_company_alias_verified(self.db, cid),
                        dbutil.get_corporate_alias_verified(self.db, cid),
                        dbutil.get_funding_verified(self.db, cid),
                        dbutil.get_artifact_verified(self.db, cid),
                        dbutil.get_member_verified(self.db, cid),
                        dbutil.get_recruit_verified(self.db, cid)]) / 7.0
        return round(verified, 2)

    def score_all(self):

        dbb = dbcon.connect_torndb()
        for company in dbb.iter('select distinct id from company where (active is null or active="Y");'):
            dbutil.update_company_score(self.db, company.id, self.score(company.id), 37011)


def score_all():

    db = dbcon.connect_torndb()
    scorer = ScorerCompleteness()
    for result in iter(db.query('select distinct id from company where (active is null or active="Y");')):
        score = scorer.score(db, result.id)
        dbutil.update_company_score(db, result.id, score)
    db.close()


def score_one():

    db = dbcon.connect_torndb()
    scorer = ScorerCompleteness()
    score = scorer.score(db, 196799)
    dbutil.update_company_score(db, 196799, score)
    score = scorer.score(db, 153537)
    dbutil.update_company_score(db, 153537, score)
    db.close()


def score_verify():

    scorer = ScorerVerifiedCompleteness()
    scorer.score_all()

if __name__ == '__main__':

    print __file__
    # score_verify()
    # score_one()
    score_all()


