# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import db as dbcon
import config as tsbconfig
from common import dbutil
from common.dsutil import FixLenList

import time
import json
import fcntl
import logging
from datetime import datetime, timedelta
from kafka import KafkaConsumer, KafkaClient, SimpleProducer
from kafka.errors import FailedPayloadsError


# logging
logging.getLogger('comps').handlers = []
logger_nlp = logging.getLogger('comps')
logger_nlp.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_nlp.addHandler(stream_handler)


class NoCandidatesException(Exception):

    def __init__(self):

        self.message = 'No candidates avaliable'


class CompsRecommender(object):

    def __init__(self):

        self.mongo = dbcon.connect_mongo()
        self.db = dbcon.connect_torndb()

        self.min_num = 3
        self.max_num = 30
        self.promote_threshold = 0.5

    def generate_comps(self, cid):

        # candidates from document similarity
        candidates = self.mongo.comps.candidates.find_one({'company': cid})
        if (not candidates) or (not candidates.get('candidates')):
            raise NoCandidatesException()
        else:
            candidates = {cid: weight for cid, weight in candidates.get('candidates')}
        # candidates from 3rd level sector
        tids = dbutil.get_companies_sector_tag(self.db, [cid], [3])
        for tid in tids:
            cids = dbutil.get_company_from_tag(self.db, tid)
            if len(cids) < 20:
                for cid in cids:
                    candidates[cid] = candidates.get('cid', 0) + 1

        # tag filter
        simis = filter(lambda x: int(x[0]) != int(cid), candidates.items())
        tag_weights = {cid2: self.rank(cid, cid2) for cid2 in map(lambda x: x[0], simis)}
        simis = [(simi[0], round((simi[1] + tag_weights.get(simi[0], 0.01) * 0.25), 2)) for simi in simis]

        # sort
        simis = sorted(simis, key=lambda x: -x[1])

        # normalization
        normalizer = max([weight for cid, weight in simis])
        simis = map(lambda x: (x[0], round(x[1]/normalizer, 2)), simis) if normalizer > 1 else simis
        qualified = filter(lambda x: x[1] > self.promote_threshold, simis)
        # simis = qualified[:self.max_num] if len(qualified) >= self.min_num else simis[:self.min_num]
        simis = qualified[:self.max_num]
        return simis

    def rank(self, cid1, cid2, model='jaccard'):

        return {
            'jaccard': self.__weighted_jaccard_ids
        }[model](cid1, cid2)

    def __weighted_jaccard_ids(self, cid1, cid2):

        """
        weighted jaccard similarity from ids
        """
        tags1, tags2 = dbutil.get_company_tags_info(self.db, cid1), dbutil.get_company_tags_info(self.db, cid2)
        if not (tags1 and tags2):
            return 0
        tags1 = map(lambda x: (x.tid, round((x.conf or 1) * (x.novelty or 1), 2)), tags1)
        tags2 = map(lambda x: (x.tid, round((x.conf or 1) * (x.novelty or 1), 2)), tags2)
        return self.__weighted_jaccard(tags1, tags2)

    def __weighted_jaccard(self, tags1, tags2):

        sum_up, sum_down = 0, 0
        tags1, tags2 = dict(tags1), dict(tags2)
        for tag in (set(tags1.keys()) | set(tags2.keys())):
            sum_up += min(tags1.get(tag, 0), tags2.get(tag, 0))
            sum_down += max(tags1.get(tag, 0), tags2.get(tag, 0))
        return float(sum_up)/sum_down

    def dump(self, fetch_model='default'):

        global logger_nlp
        db = dbcon.connect_torndb()
        if fetch_model == 'makeup':
            all_cids = iter(dbutil.get_all_company_id_makeups(db))
        else:
            all_cids = iter(dbutil.get_all_company_id(db))
        for cid in all_cids:
            try:
                dbutil.update_company_rels(db, cid, self.generate_comps(cid), feedback_threshold=0.5)
                logger_nlp.info('%s has similar companies now' % cid)
            except Exception, e:
                logger_nlp.exception('fail to find similar company for %s, %s' % (cid, e))
        db.close()


def recommend_comps_incremental():

    global logger_nlp
    recommender = CompsRecommender()
    cach = FixLenList(10)

    # init kafka
    url = tsbconfig.get_kafka_config()
    consumer_comps = KafkaConsumer("keyword_v2", group_id="comps", session_timeout_ms=10000,
                                   bootstrap_servers=[url], auto_offset_reset='smallest')
    kafka = KafkaClient(url)
    producer_comps = SimpleProducer(kafka)

    while True:
        try:
            logger_nlp.info('Start to process incremental comps')
            for message in consumer_comps:
                cid = json.loads(message.value).get('id') or json.loads(message.value).get('_id')
                try:
                    locker = open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'comps.incremental.lock'))
                    fcntl.flock(locker, fcntl.LOCK_EX)
                    db = dbcon.connect_torndb()
                    if not cid:
                        consumer_comps.commit()
                        continue
                    if cid in set(cach):
                        logger_nlp.info('Company %s in cach' % cid)
                        consumer_comps.commit()
                        continue
                    cach.append(cid)
                    if not dbutil.get_comps_update_need(db, cid):
                        logger_nlp.info('Company %s has recent update' % cid)
                        continue
                    updates = dbutil.update_company_rels(db, cid, recommender.generate_comps(cid),
                                                         need_feedback=True, feedback_threshold=0.5)
                    logger_nlp.info(message)
                    logger_nlp.info('Company %s has similar companies, updates %s' % (cid, str(updates)))
                    consumer_comps.commit()
                    if updates and isinstance(updates, list) and len(updates) > 0:
                        track_updates(db, producer_comps, cid, updates)
                        # producer_comps.send_messages("track_message",
                        #                              json.dumps({'id': cid, 'type': 'comps', 'comps': updates}))
                except NoCandidatesException, nce:
                    logger_nlp.info('No valiad candidates for %s, try another time 2s later' % cid)
                    time.sleep(2)
                    updates = dbutil.update_company_rels(db, cid, recommender.generate_comps(cid),
                                                         need_feedback=True, feedback_threshold=0.5)
                    logger_nlp.info(message)
                    logger_nlp.info('Company %s has similar companies' % cid)
                    consumer_comps.commit()
                    if updates and isinstance(updates, list) and len(updates) > 0:
                        track_updates(db, producer_comps, cid, updates)
                        # producer_comps.send_messages("track_message",
                        #                              json.dumps({'id': cid, 'type': 'comps', 'comps': updates}))
                except Exception, e:
                    logger_nlp.error('%s failed, %s' % (cid, e))
                finally:
                    # unlock and try to close database
                    fcntl.flock(locker, fcntl.LOCK_UN)
                    locker.close()
                    try:
                        db.close()
                    except Exception:
                        pass
        except Exception, e:
            logger_nlp.error('Outside, %s' % e)
            cach = FixLenList(10)


def track_updates(db, producer_comps, cid, updates):

    if dbutil.get_company_active(db, cid) != 'Y':
        return
    updates = [update for update in updates if __track_comps_match(db, update)]
    if len(updates) < 1:
        return
    # producer_comps.send_messages("track_message", json.dumps({'id': cid, 'type': 'comps', 'comps': updates}))
    comments = ','.join([dbutil.get_company_name(db, c) for c in updates])
    track_msg = u'%s发现了%s个潜在的竞争对手: %s' % (dbutil.get_company_name(db, cid), len(updates), comments)
    cmsg_id = dbutil.update_company_message(db, cid, track_msg, 6001, 60,
                                            ','.join([str(update) for update in updates]), comments=comments)
    if cmsg_id:
        try:
            producer_comps.send_messages("track_message_v2",
                                         json.dumps({'id': cmsg_id, 'type': 'company_message', 'action': 'create'}))
        except FailedPayloadsError, fpe:
            url = tsbconfig.get_kafka_config()
            kafka = KafkaClient(url)
            producer_comps = SimpleProducer(kafka)
            producer_comps.send_messages("track_message_v2",
                                         json.dumps({'id': cmsg_id, 'type': 'company_message', 'action': 'create'}))


def __track_comps_match(db, comps_cid):

    return dbutil.get_company_create_date(db, comps_cid) > (datetime.now() - timedelta(days=30))


def recommend_comps_all():

    global logger_nlp
    logger_nlp.info('Full comps starts')
    db = dbcon.connect_torndb()
    recommender = CompsRecommender()
    recommender.dump()
    db.close()


def recommend_comps_makeup():

    global logger_nlp
    logger_nlp.info('Makeup comps starts')
    recommender = CompsRecommender()
    db = dbcon.connect_torndb()
    for cid in dbutil.get_nocomps_company(db):
        try:
            dbutil.update_company_rels(db, cid, recommender.generate_comps(cid))
            logger_nlp.info('Company %s has similar companies' % cid)
        except Exception, e:
            logger_nlp.exception('Company %s failed, %s' % (cid, e))
    db.close()


def check(cid):

    recommender = CompsRecommender()
    for item in recommender.generate_comps(int(cid)):
        print item[0], item[1]


if __name__ == '__main__':

    if sys.argv[1] == 'incr' or sys.argv[1] == 'incremental':
        recommend_comps_incremental()
    elif sys.argv[1] == 'all' or sys.argv[1] == 'full':
        recommend_comps_all()
    elif sys.argv[1] == 'makeup':
        recommend_comps_makeup()
    elif sys.argv[1] == 'check':
        check(sys.argv[2])
