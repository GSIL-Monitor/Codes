# -*- encoding=utf-8 -*-
__author__ = "kailu"

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil

import logging
from numpy import mean
from datetime import datetime, timedelta


# logging
logging.getLogger('activation').handlers = []
logger_activation = logging.getLogger('activation')
logger_activation.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_activation.addHandler(stream_handler)


class ActivationScorer(object):

    """
    evaluate company from following aspects,
        news media within six months
        verified artifact updates within three months
        recruitment within six months
    """

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

        self.three_month = datetime.now() - timedelta(days=90)
        self.six_month = datetime.now() - timedelta(days=180)

    def score(self, cid):

        score = mean([self.__score_media(cid), self.__score_artifact(cid), self.__score_recruitment(cid)])
        dbutil.update_company_score(self.db, cid, score, 37030)

    def __score_media(self, cid):

        if len(list(self.mongo.article.news.find({'companyIds': cid, 'date': {'$gte': self.six_month}}))) > 0:
            return 1
        return 0

    def __score_artifact(self, cid):

        if dbutil.get_company_latest_artifact_date(self.db, cid) > self.three_month:
             return 1
        return 0

    def __score_recruitment(self, cid):

        recruits = dbutil.get_company_recruitments(self.db, cid)
        if recruits and len(list(self.mongo.job.job.find({'recruit_company_id': {'$in': recruits},
                                                          'updateDate': {'$gte': self.six_month}}))) > 0:
            return 1
        return 0


class TrackActivationScorer(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()

    def score(self, cid):

        cms = [cm.active for cm in dbutil.get_company_messages(self.db, cid)]
        return cms.count('Y'), cms.count('P')


def score_activation_full():

    global logger_activation
    db = dbcon.connect_torndb()
    scorer = ActivationScorer()
    for cid in dbutil.get_all_company_id(db):
        scorer.score(cid)
        logger_activation.info('%s scored' % cid)
    db.close()

if __name__ == '__main__':

    if sys.argv[1] == 'activation':
        score_activation_full()
