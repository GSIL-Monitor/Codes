# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../score'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbconn
import loghelper
from common import dbutil, dicts
from score.end import PushScorer
from score.company_comp import CompanyTagsRelevance, CompanyUserRelevance
from score.activation import TrackActivationScorer

import logging
import codecs
import random
from copy import copy
from abc import abstractmethod
from itertools import chain
from datetime import datetime, timedelta

from numpy.random import choice

# logging
logging.getLogger('push').handlers = []
logger_push = logging.getLogger('push')
logger_push.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_push.addHandler(stream_handler)


class Pusher(object):

    @abstractmethod
    def push(self, uid):
        pass

    # def generate_deal(self, db, cid, uid):
    #
    #     oid = dbutil.get_user_organization(db, uid)
    #     did = dbutil.get_deal(db, cid, oid)
    #     dbutil.update_deal_user(db, did, uid)


class TaskPusher(Pusher):

    TASK_CANDIDATES_VOLUM = 4000

    def __init__(self, method='default'):

        self.db = dbconn.connect_torndb()
        self.mongo = dbconn.connect_mongo()
        # self.scorer = CompanyTagsRelevance()
        self.scorer = CompanyUserRelevance()

        self.daily_recommendation_size = 2
        self.pool_size = 100

        if method == 'controlled':
            self.general_pusher = PushScorer()
            self.candidates = dbutil.get_all_push_pool(self.db)
            self.__update_push_pool()
        if method == 'default':
            self.general_pusher = PushScorer()
            self.candidates = self.general_pusher.promote_general(self.db)
            self.__update_push_pool()

        # rounds and locations
        self.rounds = {cid: dbutil.get_company_round(self.db, cid) for cid in self.candidates}
        self.locations = {cid: dbutil.get_company_location(self.db, cid)[0] for cid in self.candidates}

    def __update_push_pool(self):

        dbutil.clear_push_pool(self.db)
        # sector = {dbutil.get_tag_id(self.db, v[0])[0]: dbutil.get_sector_id(self.db, k)
        #           for k, v in dicts.get_sector_extend().items()}
        sectors = dbutil.get_sector_tags(self.db)

        for cid in self.candidates:
            for sid, tags in sectors.items():
                if dbutil.exist_company_tag(self.db, cid, tags[0]):
                    dbutil.update_push_pool(self.db, cid, sid)
                    break

    def push(self, uid):

        """
        :return: results' company ids and a flag
        flag=0, no need to push
        flag=1, user didn't specify sector
        flag=2, regular
        flag=3, run out
        """
        global logger_push

        not_read = dbutil.get_recommendation_waste(self.db, uid)
        if not_read == self.__get_push_volumn():
            return [], 0

        utags = dbutil.get_user_profile(self.db, uid)
        if not utags:
            return [], 1

        update_count = self.__get_push_volumn() - not_read

        # half from push pool
        usectors = dbutil.get_user_sectors(self.db, uid, False)
        push_pool = dbutil.get_push_pool(self.db, usectors)
        push_pool = [cid for cid in push_pool if dbutil.could_recommend(self.db, uid, cid)]
        push_pool = random.sample(push_pool, min(update_count/2, len(push_pool)))
        for cid in push_pool:
            dbutil.update_recommendation(self.db, uid, cid, confidence=random.choice([0.96, 0.97]))
        logger_push.info('Generate %s recommendation from pool for %s' % (len(push_pool), uid))

        # some from portfolio
        portfolio = filter(lambda cid: dbutil.could_recommend(self.db, uid, cid),
                           chain(*[record.get('companyIds', [])
                                   for record in self.mongo.fellowplus.investor.find({'userId': int(uid)})]))
        if len(portfolio) >= 2:
            portfolio = random.sample(portfolio, 2)
            for cid in portfolio:
                dbutil.update_recommendation(self.db, uid, cid, confidence=0.97)
            logger_push.info('Generate portfolio recommendation for %s' % uid)
        else:
            portfolio = []

        results = [(cid, self.scorer.score(cid, utags)) for cid in self.__user_filter(uid) if
                   dbutil.could_recommend(self.db, uid, cid) and (self.scorer.score(cid, utags) > 0)]
        logger_push.info('Record: %s has %s left' % (uid, len(results)))
        if len(results) == 0:
            return [], 3
        results = sorted(results, key=lambda x: x[1], reverse=True)[:self.pool_size]
        results = [result[0] for result in random.sample(results, (update_count - len(push_pool) - len(portfolio)))]
        for cid in results:
            dbutil.update_recommendation(self.db, uid, cid)
        return results, 2

    def __get_push_volumn(self):

        return 16
        # return random.randint(1, self.daily_recommendation_size+1)

    def __user_filter(self, uid):

        rounds = [int(r.preference) for r in self.db.query('select preference from user_preference '
                                                           'where userId=%s and type=1;', uid)]
        locations = [int(l.preference) for l in self.db.query('select preference from user_preference '
                                                              'where userId=%s and type=2;', uid)]
        # did not specify round or location
        if not (rounds or locations):
            return self.candidates

        candidates = copy(self.candidates)
        # print 'init', len(candidates)
        # round filter
        rounds = [{
            1010: [1000, 1010, 1011],
            1020: [1011, 1020],
            1030: [1020, 1030],
            1040: [1030, 1031, 1039, 1040],
            1050: [1040, 1041, 1050],
            1060: [1050, 1060, 1070, 1080, 1090, 1100, 1105, 1106, 1110, 1120, 1130]
        }[r] for r in rounds]
        rounds = set(chain(*rounds))
        if rounds:
            candidates = [candidate for candidate in candidates if self.rounds.get(candidate) in rounds]
        # location filter
        if locations:
            if -1 in locations:
                out_locations = [l for l in [1, 2, 63, 360, 52, 296, 185, 146] if l not in locations]
                if out_locations:
                    candidates = [candidate for candidate in candidates if
                                  self.locations.get(candidate) not in out_locations]
            else:
                candidates = [candidate for candidate in candidates if self.locations.get(candidate) in locations]
        return candidates


class SourcingPusher(object):

    def __init__(self, start=None):

        self.db = dbconn.connect_torndb()
        if not start:
            start = datetime.now() - timedelta(days=1)
        self.scorer = CompanyUserRelevance()
        self.user_company_threshold = 0
        self.candidates = dbutil.get_sourcing_company(self.db, start)
        self.custom_candidates = {}
        for cid, comments in dbutil.get_sourcing_company(self.db, start, 'full'):
            for module in comments.split(','):
                self.custom_candidates.setdefault(int(module), []).append(cid)

    def push(self, oid=51):

        global logger_push
        # users = {uid: dbutil.get_user_profile(self.db, uid)
        #          for uid in dbutil.get_organization_watcher_users(self.db, oid, 'coldcall')}
        users = {uid: dict.fromkeys(dbutil.get_user_sectors(self.db, uid, True), 5)
                 for uid in dbutil.get_organization_watcher_users(self.db, oid, 'coldcall')}
        custom_candidates = chain(*[self.custom_candidates.get(module, []) for module in
                                    dbutil.get_organization_sourcing_modules(self.db, oid)])
        if oid in {139}:
            org_candidates = set(custom_candidates)
        else:
            org_candidates = set(self.candidates) | set(custom_candidates)
        for cid in org_candidates:
            candidates = sorted([(uid, self.scorer.score(cid, utags)) for uid, utags in users.items()
                                 if self.scorer.score(cid, utags) > self.user_company_threshold
                                 and dbutil.could_recommend(self.db, uid, cid)],
                                key=lambda x: x[1], reverse=True)
            gs = 'Y' if dbutil.exist_extract_source(self.db, cid) else 'N'
            if not candidates:
                uid = choice(users.keys())
                dbutil.update_sourcing_user(self.db, cid, uid, gongshang=gs)
                logger_push.info('Random push %s for %s' % (cid, uid))
            for uid, _ in candidates:
                dbutil.update_sourcing_user(self.db, cid, uid, gongshang=gs)
                logger_push.info('Push %s for %s' % (cid, uid))

            # candidates = [u[0] for u in candidates] if candidates else [choice(users.keys())]
            # dbutil.update_sourcing_user(self.db, cid, choice(candidates))

    def push_sb(self, uid=215):

        for cid in self.candidates:
            gs = 'Y' if dbutil.exist_extract_source(self.db, cid) else 'N'
            dbutil.update_sourcing_user(self.db, cid, uid, gongshang=gs)
        for cid in self.custom_candidates.get(71001, []):
            gs = 'Y' if dbutil.exist_extract_source(self.db, cid) else 'N'
            dbutil.update_sourcing_user(self.db, cid, uid, gongshang=gs)


def push_all(db):

    global logger_push
    dbutil.mark_read_recommendations(db)
    logger_push.info('Read recommendations marked')
    logger_push.info('Examine following funding')
    dbutil.update_recommedation_following_fundings(db)
    logger_push.info('Start to push recommendations')
    push_people(*list(dbutil.get_all_user(db)))
    logger_push.info('Push Task Done')


def push_people(*uids):

    global logger_push
    pusher = TaskPusher(method='controlled')
    logger_push.info('Start to push recommendations for people')
    for uid in uids:
        try:
            cids, flag = pusher.push(uid)
            if cids:
                logger_push.info('%s pushed # %s' % (uid, ','.join([str(cid) for cid in cids])))
            elif flag == 0:
                logger_push.info('%s no need to push' % uid)
            elif flag == 1:
                logger_push.info('%s not a valid user' % uid)
            elif flag == 3:
                logger_push.info('%s run out' % uid)
        except Exception, e:
            logger_push.exception('%s %s' % (uid, e))


def push_someone(uid):

    pusher = TaskPusher()
    pusher.push(uid)


def update_pool():

    db = dbconn.connect_torndb()
    dbutil.clear_push_pool(db)
    for cid in open('files/pool'):
        cid = int(cid.strip())
        sids = [x.tid for x in dbutil.get_company_tags_info(db, cid, [11012])][:2]
        for sid in [s.id for s in db.query('select id from sector where tagId in %s', sids)]:
            db.execute('insert into push_pool (companyId, sectorId, createTime, verify) '
                       'values (%s, %s, now(), "Y")', cid, sid)
    db.close()


def fellowplus():

    db = dbconn.connect_torndb()
    mongo = dbconn.connect_mongo()
    uids = chain(*[record.get('userId', []) for record in mongo.fellowplus.investor.find({'userId': {'$ne': None}})])
    pusher = TaskPusher()
    for uid in set(uids):
        db.execute('delete from recommendation where userId=%s and hasRead="N";', uid)
        try:
            cids, flag = pusher.push(uid)
            if cids:
                logger_push.info('%s pushed # %s' % (uid, ','.join([str(cid) for cid in cids])))
            elif flag == 0:
                logger_push.info('%s no need to push' % uid)
            elif flag == 1:
                logger_push.info('%s not a valid user' % uid)
            elif flag == 3:
                logger_push.info('%s run out' % uid)
        except Exception, e:
            logger_push.exception('%s %s' % (uid, e))


def debug():

    pusher = SourcingPusher()
    custom_candidates = chain(*[pusher.custom_candidates.get(module, []) for module in
                                dbutil.get_organization_sourcing_modules(pusher.db, 243)])
    print set(custom_candidates)
    org_candidates = set(pusher.candidates) | set(custom_candidates)
    print set(custom_candidates)
    print org_candidates


if __name__ == '__main__':

    print __file__

    if sys.argv[1] == 'push':
        db = dbconn.connect_torndb()
        push_all(db)
        db.close()
    elif sys.argv[1] == 'pushorg':
        db = dbconn.connect_torndb()
        # dbutil.mark_read_recommendations(db)
        # 烯牛资本 51
        push_people(*dbutil.get_organization_watcher_users(db, sys.argv[2]))
        db.close()
    elif sys.argv[1] == 'pushsb':
        db = dbconn.connect_torndb()
        dbutil.mark_read_recommendations(db, sys.argv[2])
        # 我自己烯牛 215
        push_people(sys.argv[2])
        db.close()
    elif sys.argv[1] == 'pushpart':
        push_someone(sys.argv[2])
    elif sys.argv[1] == 'pool':
        update_pool()
    elif sys.argv[1] == 'fellowplus':
        fellowplus()
    elif sys.argv[1] == 'debug':
        debug()
    elif sys.argv[1] == 'sourcing':
        sp = SourcingPusher()
        db = dbconn.connect_torndb()
        logger_push.info('Pusher inited')
        for oid in dbutil.get_sourcing_organizations(db):
            sp.push(oid)
    # tp = TaskPusher()
    # tp.tmp_check()
    # push_someone(223)