# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
import config as tsbconfig
from common import dbutil

import time
import json
import logging
import fcntl
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from kafka import KafkaConsumer


# logging
logging.getLogger('task_company').handlers = []
logger_tcg = logging.getLogger('task_company')
logger_tcg.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_tcg.addHandler(stream_handler)


class TaskCompanyGenerator(object):

    def __init__(self):

        global logger_tcg
        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        self.logger = logger_tcg

        self.xiniu_users = dbutil.get_organization_watcher_users(self.db, 51)
        self.no_share_sources = ['company_big', 'track_gongshang', 'company_newcover', 'company_create',
                                 'gongshang_verified_online', 'gongshang_verified_tbc', 'gongshang_verified_offline',
                                 'gongshang_unverified_online', 'gongshang_unverified_offline',
                                 'gongshang_create_online']
        self.no_clear_sources = ['gongshang_verified_online', 'gongshang_verified_tbc', 'gongshang_verified_offline',
                                 'gongshang_unverified_online', 'gongshang_unverified_offline',
                                 'gongshang_create_online', 'news_funding']

    def generate_tc(self, message):

        self.logger.info('Processing, %s' % message)
        message = json.loads(message)
        {
            'news_funding': self.__process_news_funding,
            'news_regular': self.__process_news_regular,
            'company_create': self.__process_company_create,
            'company_split': self.__process_company_split,
            'company_newcover': self.__process_company_newcover,
            'company_job': self.__process_company_job,
            'company_fa': self.__process_company_fa,
            'company_funding': self.__process_company_funding,
            'investor_portfolio': self.__process_investor_portfolio,
            'track_gongshang': self.__process_track_gongshang,
            'track_company': self.__process_track_company,
            'track_topic': self.__process_track_topic,
            'track_industry': self.__process_track_industry,
            'track_saoanzi': self.__process_track_saoanzi,
            'track_user': self.__process_track_user,
            'visit_web': self.__process_visit_web,
            'visit_app': self.__process_visit_app,
            'visit_openapi': self.__process_visit_openapi,
            'gongshang_verified_online': self.__process_gongshang_general,
            'gongshang_verified_tbc': self.__process_gongshang_general,
            'gongshang_verified_offline': self.__process_gongshang_general,
            'gongshang_unverified_online': self.__process_gongshang_general,
            'gongshang_unverified_offline': self.__process_gongshang_general,
            'gongshang_create_online': self.__process_gongshang_general,
        }[message.get('source')](message)

    def __process_news_funding(self, message):

        nid = message.get('id')
        news = self.mongo.article.news.find_one({'_id': ObjectId(nid)})
        if not self.__is_recent_news(news):
            self.logger.info('Not recent news, %s' % nid)
            return
        for cid in news.get('companyIds', []):
            if not self.__is_recent_task(cid):
                self.update_task(cid, 'news_funding', nid)

    def __process_news_regular(self, message):

        nid = message.get('id')
        news = self.mongo.article.news.find_one({'_id': ObjectId(nid)})
        if not self.__is_recent_news(news):
            self.logger.info('Not recent news, %s' % nid)
            return
        for cid in self.mongo.article.news.find_one({'_id': ObjectId(nid)}).get('companyIds', []):
            if self.need_verify(cid):
                if self.__is_big_company(cid):
                    self.update_task(cid, 'company_big', message.get('detail'))
                elif self.__is_bad_news(news):
                    self.update_task(cid, 'company_bad_news', nid)
                else:
                    self.update_task(cid, 'news_regular', nid)

    def __process_company_create(self, message):

        cid = message.get('id')
        if self.need_verify(cid):
            self.update_task(cid, 'company_create', None)

    def __process_company_split(self, message):

        cid = message.get('id')
        if self.need_verify(cid):
            self.update_task(cid, 'company_split', None)

    def __process_company_newcover(self, message):

        cid = message.get('id')
        if self.need_verify(cid):
            self.update_task(cid, 'company_newcover', None, no_update=message.get('no_update', False))

    def __process_company_job(self, message):

        cid = message.get('id')
        # if self.need_verify(cid):
        self.update_task(cid, 'company_job', None, no_update=message.get('no_update', False))

    def __process_company_fa(self, message):

        cid = message.get('id')
        if self.need_verify(cid):
            self.update_task(cid, 'company_fa', message.get('detail'))

    def __process_company_funding(self, message):

        cid = message.get('id')
        if self.need_verify(cid):
            self.update_task(cid, 'company_funding', message.get('detail'))

    def __process_track_gongshang(self, message):

        cid = int(message.get('id'))
        if self.need_verify(cid):
            self.update_task(cid, 'track_gongshang', message.get('detail'))

    def __process_track_industry(self, message):

        cid = int(message.get('id'))
        if self.need_verify(cid):
            self.update_task(cid, 'track_industry', message.get('detail'))

    def __process_track_saoanzi(self, message):

        cid = int(message.get('id'))
        if self.need_verify(cid):
            self.update_task(cid, 'track_saoanzi', message.get('detail'))

    def __process_track_user(self, message):

        cid = int(message.get('id'))
        if self.need_verify(cid):
            self.update_task(cid, 'track_user', message.get('detail'))

    def __process_investor_portfolio(self, message):

        cid = int(message.get('id'))
        self.update_task(cid, 'investor_portfolio', message.get('detail'))

    def __process_track_topic(self, message):

        cid = int(message.get('id'))
        if dbutil.get_topic_company_active(self.db, cid) and self.need_verify(cid):
            if self.__is_big_company(cid):
                self.update_task(cid, 'company_big', message.get('detail'))
            else:
                self.update_task(cid, 'track_topic', message.get('detail'))

    def __process_track_company(self, message):

        cid = int(message.get('id'))
        if self.need_verify(cid):
            if self.__is_big_company(cid):
                self.update_task(cid, 'company_big', message.get('detail'))
            else:
                self.update_task(cid, 'track_company', message.get('detail'))

    def __process_visit_web(self, message):

        cid = dbutil.get_id_from_code(self.db, message.get('id'))
        uid = int(message.get('detail', -1))
        if self.need_verify(cid) and uid != -1 \
                and uid not in self.xiniu_users and dbutil.exist_verified_investor(self.db, uid):
            self.update_task(cid, 'visit_local', message.get('detail'))

    def __process_visit_app(self, message):

        cid = message.get('id')
        uid = int(message.get('detail', -1))
        if self.need_verify(cid) and uid != -1 and uid not in self.xiniu_users \
                and dbutil.exist_verified_investor(self.db, uid):
            self.update_task(cid, 'visit_local', message.get('detail'))

    def __process_visit_openapi(self, message):

        return
        # cid = message.get('id')
        # if self.need_verify(cid):
        #     self.update_task(cid, 'visit_openapi', message.get('detail'))

    def __process_gongshang_general(self, message):

        cid = int(message.get('id'))
        self.update_task(cid, message.get('source'), message.get('detail'))

    def __is_recent_task(self, cid, source='news_funding', recent=15):

        recent_date = datetime.utcnow() - timedelta(days=recent)
        return len(list(self.mongo.task.company.find({'companyId': cid, 'types': source, 'processStatus': {'$ne': 0},
                                                      'modifyTime': {'$gt': recent_date}}))) > 0

    def __is_recent_news(self, news, recent=30):

        recent_date = datetime.utcnow() - timedelta(days=recent)
        return news.get('date', 0) > recent_date

    def __is_bad_news(self, news):

        if 578362 in news.get('features', []):
            return True
        return False

    def __is_big_company(self, cid):

        return dbutil.exist_company_tag(self.db, cid, 599843)

    def update_task(self, cid, source_type, relate_id, comments=None, no_update=False):

        relate_type = {
            'news_funding': 'news',
            'news_regular': 'news',
            'company_create': 'company',
            'company_newcover': 'company',
            'company_split': 'company',
            'company_fa': 'fa',
            'company_big': 'company',
            'company_funding': 'company',
            'company_job': 'company',
            'company_bad_news': 'company',
            'track_topic': 'topic_message',
            'track_company': 'company_message',
            'investor_portfolio': 'company',
            'track_gongshang': 'company',
            'track_industry': 'company',
            'visit_web': 'company',
            'visit_app': 'company',
            'visit_openapi': 'company'
        }.get(source_type, None)
        # special types that does not share task with others
        if source_type in self.no_share_sources:
            if len(list(self.mongo.task.company.find({'companyId': cid, 'processStatus': 0,
                                                      'types': source_type}))) == 0:
                self.mongo.task.company.insert({
                    'companyId': int(cid),
                    'types': [source_type],
                    'comments': relate_id,
                    'description': comments,
                    'relates': [
                        {'type': source_type, 'relateType': relate_type, 'relateId': relate_id}
                    ],
                    'track_subscription': dbutil.get_company_subscription_count(self.db, cid),
                    'createTime': datetime.utcnow(),
                    'modifyTime': datetime.utcnow(),
                    'taskDate': datetime.utcnow().strftime('%Y%m%d'),
                    'no_share': True,
                    'processStatus': 0,
                    'mtProcessStatus': 0
                })
            else:
                return
        else:
            if len(list(self.mongo.task.company.find({'companyId': cid, 'processStatus': 0, 'no_share': False}))) == 0:
                self.mongo.task.company.insert({
                    'companyId': int(cid),
                    'types': [source_type],
                    'relates': [
                        {'type': source_type, 'relateType': relate_type, 'relateId': relate_id}
                    ],
                    'track_subscription': dbutil.get_company_subscription_count(self.db, cid),
                    'createTime': datetime.utcnow(),
                    'modifyTime': datetime.utcnow(),
                    'taskDate': datetime.utcnow().strftime('%Y%m%d'),
                    'no_share': False,
                    'processStatus': 0,
                    'mtProcessStatus': 0
                })
            else:
                if no_update:
                    return
                self.mongo.task.company.update({'companyId': int(cid), 'processStatus': 0, 'no_share': False},
                                               {'$addToSet': {'types': source_type,
                                                              'relates': {'type': source_type,
                                                                          'relateType': relate_type,
                                                                          'relateId': relate_id}},
                                                '$set': {'modifyTime': datetime.utcnow(),
                                                         'track_subscription':
                                                             dbutil.get_company_subscription_count(self.db, cid),
                                                         'taskDate': datetime.utcnow().strftime('%Y%m%d')}})

    def need_verify(self, cid, debug=False):

        if debug:
            if dbutil.get_company_active(self.db, cid) == 'P':
                return False, -2
            if not dbutil.get_company_verified(self.db, cid):
                return True, 0
            # if not dbutil.get_corporate_verified(self.db, cid):
            #     return True, 1
            if not dbutil.get_company_alias_verified(self.db, cid):
                return True, 2
            if not dbutil.get_corporate_alias_verified(self.db, cid):
                return True, 3
            if not dbutil.get_funding_verified(self.db, cid):
                return True, 4
            if not dbutil.get_artifact_verified(self.db, cid):
                return True, 5
            if not dbutil.get_member_verified(self.db, cid):
                return True, 6
            if not dbutil.get_recruit_verified(self.db, cid):
                return True, 7
            return False, -1
        else:
            if dbutil.get_company_active(self.db, cid) == 'P':
                return False
            if not dbutil.get_company_verified(self.db, cid):
                return True
            # if not dbutil.get_corporate_verified(self.db, cid):
            #     return True
            if not dbutil.get_company_alias_verified(self.db, cid):
                return True
            if not dbutil.get_corporate_alias_verified(self.db, cid):
                return True
            if not dbutil.get_funding_verified(self.db, cid):
                return True
            if not dbutil.get_artifact_verified(self.db, cid):
                return True
            if not dbutil.get_member_verified(self.db, cid):
                return True
            if not dbutil.get_recruit_verified(self.db, cid):
                return True
            return False

    def clean_task(self):

        for record in self.mongo.task.company.find({'processStatus': 0, 'types': {'$nin': self.no_clear_sources}}):
            try:
                if not self.need_verify(int(record.get('companyId'))):
                    if record.get('taker', 139) and record.get('taker', 139) != 139:
                        self.mongo.task.company.update({'_id': record['_id']},
                                                       {'$set': {'processStatus': 1, 'finishTime': datetime.utcnow()}})
                    else:
                        self.mongo.task.company.update({'_id': record['_id']},
                                                       {'$set': {'processStatus': 1, 'taker': 139,
                                                                 'finishTime': datetime.utcnow()}})
                    self.logger.info('%s, cleaned' % record.get('companyId'))
            except Exception, e:
                self.logger.exception('%s, failed, %s' % (record.get('companyId'), e))


def generate_task_company_incremental():

    tcg = TaskCompanyGenerator()
    tcg.logger.info('Task Company Generating')
    url = tsbconfig.get_kafka_config()
    consumer_tc = KafkaConsumer("task_company", group_id="tc_generation",
                                bootstrap_servers=[url], auto_offset_reset='smallest')
    while True:
        try:
            tcg.logger.info('TCG restarting')
            for message in consumer_tc:
                locker = open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'tc.lock'))
                fcntl.flock(locker, fcntl.LOCK_EX)
                try:
                    tcg.generate_tc(message.value)
                except Exception, e:
                    tcg.logger.exception('Fail to process %s, %s' % (message, e))
                finally:
                    fcntl.flock(locker, fcntl.LOCK_UN)
                    locker.close()
        except Exception, e:
            tcg.logger.exception('Outside#%s' % e)


def clean_task_company():

    while True:
        tcg = TaskCompanyGenerator()
        tcg.clean_task()
        time.sleep(1800)


def special1_user_track():

    tcg = TaskCompanyGenerator()
    db = dbcon.connect_torndb()
    for c in db.query('select distinct companyId cid from track_group_item_rel '
                      'where active="Y" and companyId is not null and createTime>"2018-08-08";'):
        tcg.generate_tc(json.dumps({'id': c.cid, 'source': 'track_user'}))
    db.close()


if __name__ == '__main__':

    if sys.argv[1] == 'incremental' or sys.argv[1] == 'incr':
        generate_task_company_incremental()
    if sys.argv[1] == 'clean':
        clean_task_company()
    if sys.argv[1] == 'special1':
        special1_user_track()
    if sys.argv[1] == 'check':
        tc = TaskCompanyGenerator()
        print tc.need_verify(449753, True)
