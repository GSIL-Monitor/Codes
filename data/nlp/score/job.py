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

from math import sqrt
from datetime import datetime, timedelta
import pandas as pd


sector_min_size = 20
outstanding_recruit_ratio = 0.05


class ScorerJob(object):

    def __init__(self):
        pass

    def score(self, db, cid):

        jobs = dbutil.get_jobs(db, cid)
        return min(1, sqrt(float(len(jobs))/10))


# top (default)5% most recruit information of the given round and sector
# def summary_recruit_all():
#
#     global sector_min_size, outstanding_recruit_ratio
#     db = dbcon.connect_torndb()
#     df = pd.DataFrame(db.query('select job.companyId as id, count(*) as counts, company.round as round '
#                                'from job, company where job.startDate>date_add(curdate(), interval -1 month)'
#                                'and company.id=job.companyId group by job.companyId having counts>5;'))
#     df['sector'] = df.apply(__get_sector, 1)
#     for stage, rdf in df.groupby('round'):
#         for sector, sdf in rdf.groupby('sector'):
#             if len(sdf) < sector_min_size:
#                 continue
#             normalizer = sdf.counts.max()
#             outstanding_recruit_count_threshold = sorted(list(sdf.counts), reverse=True)[int(len(sdf)*outstanding_recruit_ratio)]
#             sdf = sdf[sdf.counts >= outstanding_recruit_count_threshold]
#             for item in sdf.iterrows():
#                 yield item[1].id, round(float(item[1].counts)/normalizer, 2)
#    db.close()


# (recruit information in recent [30] days )/(company size) > [0.2]
def summary_recruit_all(days=30, recruit_ratio=0.2, recruit_threshold=50):

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    gte = datetime.now() - timedelta(days=days)
    for cid in dbutil.get_all_company_id(db):
        recruit_ids = dbutil.get_company_recruitments(db, cid)
        if not recruit_ids:
            continue
        recruits = len(list(mongo.job.job.find({'recruit_company_id': {'$in': recruit_ids},
                                                'updateDate': {'$gte': gte}})))
        headcount = dbutil.get_company_headcount_max(db, cid)
        if headcount and headcount > 0:
            ratio = round(recruits / float(headcount), 2)
            if ratio > recruit_ratio:
                yield cid, ratio
        else:
            if recruits > recruit_threshold:
                yield cid, 1
    db.close()


def __get_sector(item):

    dbc = dbcon.connect_torndb()
    viptag = dbc.query('select tag.id as tid from tag, company_tag_rel where company_tag_rel.companyId=%s '
                       'and (company_tag_rel.active is null or company_tag_rel.active="Y") '
                       'and tag.id=company_tag_rel.tagId and tag.type=11012 '
                       'order by company_tag_rel.confidence desc;', item[0])
    dbc.close()
    if not viptag:
        return 0
    return viptag[0].tid


if __name__ == '__main__':

    print __file__
    rg = summary_recruit_all()
    print len(list(rg))
