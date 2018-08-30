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
from common import dbutil, dicts
from keywords.key import Extractor
from track.company_track import CompanyNewsTracker

import json
import logging
import socket
from copy import deepcopy
from itertools import chain
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from kafka import KafkaConsumer, KafkaClient, SimpleProducer
from kafka.errors import FailedPayloadsError

# logging
logging.getLogger('news_post').handlers = []
logger_news_post = logging.getLogger('news_post')
logger_news_post.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_news_post.addHandler(stream_handler)

# kafka
consumer_news_task = None
producer_news_task = None


class NewsTagger(object):

    def __init__(self):

        self.mongo = dbcon.connect_mongo()
        self.news_sources = dicts.get_news_sources4tag()
        self.report_author_relatives = dicts.get_report_authors()
        self.wechatIds = dicts.get_wechat4tag()
        self.zhihuCodes = dicts.get_zhihu4tag()

    def label_11800(self, nid):

        record = list(self.mongo.article.news.find({'_id': ObjectId(nid)}))[0]
        return self.label_11800_record(record, nid)

    def label_11800_record(self, record, nid):

        record_source = int(record.get('source', 0))
        # 新闻报道源
        if record_source in self.news_sources:
            return self._label_11801(nid, record)
        # 报告
        elif record_source in (13835, 13836):
            return self._label_report(nid, record)
        # 微信公众号
        elif record_source in (13840, 13841):
            return self._label_11804(nid, record)
        # 知乎
        elif record_source in (13610, 13611, 13613):
            return self._label_11805(nid, record)

    def label_11810(self, nid):

        record = list(self.mongo.article.news.find({'_id': ObjectId(nid)}))[0]
        return self.label_11810_record(record, nid)

    def label_11810_record(self, record, nid):

        # 579402, 阅读10w+
        tag, threshold = 579402, 100000
        if record.get('clicksCount', 0) >= threshold:
            self.mongo.article.news.update({'_id': ObjectId(nid)}, {'$addToSet': {"features": tag}})
            return True

    def _label_11801(self, nid, record):

        tag = self.news_sources.get(int(record.get('source', 0)), False)
        logger_news_post.info('11801 Tag add %s' % tag)
        if tag:
            self.mongo.article.news.update({'_id': ObjectId(nid)}, {'$addToSet': {"features": tag}})
            return True

    def _label_report(self, nid, record):

        record_author = record['author']
        flag = False
        tags = set()
        for authorname in self.report_author_relatives.keys():
            if record_author.find(authorname) != -1:
                tags = tags.union({self.report_author_relatives[authorname]})
        logger_news_post.info('11802-11803 Tag add %s' % tags)
        for tag in tags:
            self.mongo.article.news.update({'_id': ObjectId(nid)}, {'$addToSet': {"features": tag}})
            flag = True
        return flag

    def _label_11804(self, nid, record):

        record_wid = record['wechatId']
        tag = self.wechatIds.get(record_wid, False)
        logger_news_post.info('11804 Tag add %s' % tag)
        if tag:
            self.mongo.article.news.update({'_id': ObjectId(nid)}, {'$addToSet': {"features": tag}})
            return True

    def _label_11805(self, nid, record):

        record_source = int(record.get('source', 0))
        record_author_code = None
        if record_source == 13610:
            record_author_code = u"DAILY"
        elif record_source == 13611:
            record_author_code = record['author_code']
        elif record_source == 13613:
            record_author_code = record['author_code']
            title = record["title"]
            if u"一周融资回顾" in title or u"投融资观察" in title:
                record_author_code += u"_XINIUINSIGHTS"
            elif u"烯牛谍报" in title:
                record_author_code += u"_XINIUDIEBAO"
        tag = self.zhihuCodes.get(record_author_code, False)
        logger_news_post.info('11805 Tag add %s' % tag)
        if tag:
            self.mongo.article.news.update({'_id': ObjectId(nid)}, {'$addToSet': {"features": tag}})
            return True


class NewsTaskPostProcesser(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

        self.company_tagger = Extractor()
        self.news_tagger = NewsTagger()
        self.news_tracker = CompanyNewsTracker()

        self.news_timeliness = 7

    def process(self, tnid, processing_dup=False):

        global producer_news_task
        record = self.mongo.task.news.find({'_id': ObjectId(tnid)}).limit(1)[0]
        section = 'step2' if record.get('type', '') == 'report' else record.get('section', 'step1')
        if section == 'step1':
            self.__process_step1(record)
        else:
            self.__process_step2(record)

    def __process_step1(self, record):

        global producer_news_task

        # not news
        if record.get('processStatus', 0) != 1:
            self.mongo.article.news.update({'_id': ObjectId(record['news_id'])}, {'$set': {'processStatus': -1}})
            return
        if record.get('source', 0) == 'gongshang':
            return

        # update article news
        category = self.__map_category(record.get('categories', []))
        cids = record.get('companyIds', [])
        iids = record.get('investorIds', [])
        if category:
            self.mongo.article.news.update({'_id': ObjectId(record['news_id'])}, {'$set': {'category': category}})
        self.mongo.article.news.update({'_id': ObjectId(record['news_id'])},
                                       {'$set': {'companyIds': cids, 'investorIds': iids,
                                                 'modifyUser': record['modifyUser'],
                                                 'categories': record.get('categories', [])}})

        # prepare features
        features = set()
        features.update(record.get('categories', []))
        features.add(record.get('sentiment'))
        # sector relevant features
        # orginal_features = [int(tid) for tid in
        #                     self.mongo.article.news.find_one({'_id': ObjectId(record['news_id'])}).get('features', [])]
        # industry_tags = [tid for tid in orginal_features if dbutil.get_tag_info(self.db, tid).type < 11050]
        # features.update(industry_tags)
        if {128, 578353, 578349, 578351, 578356, 578351} & set(record.get('categories', [])):
            features.update(record.get('newsTags', []))

        # generate step 2 task
        sector_update_flag = False
        if cids:
            startsups = filter(lambda cid: dbutil.get_company_round(self.db, cid) < 1041, cids)
            if startsups:
                news_tags = list(chain(*[[t.tid for t in dbutil.get_company_tags_info(self.db, cid)
                                          if t.verify and t.verify == "Y"]
                                         for cid in cids]))
                news_sectors = self.__map_sectors(news_tags)
                if len(news_sectors) <= 3:
                    sector_update_flag = True
                    features.update(news_tags)
                    self.mongo.article.news.update({'_id': ObjectId(record['news_id'])},
                                                   {'$set': {'sectors': news_sectors}})
        if not sector_update_flag:
            task2 = {
                'news_id': str(record['news_id']),
                'taskNewsId': str(record['_id']),
                'createTime': datetime.utcnow(),
                'newsTags': record.get('newsTags', []),
                'companyIds': cids,
                'processStatus': int(0),
                'section': 'step2'
            }
            if self.mongo.task.news.find({'taskNewsId': str(record['_id'])}).count() == 0:
                self.mongo.task.news.insert_one(task2)

        # update article news
        self.mongo.article.news.update({'_id': ObjectId(record['news_id'])},
                                       {'$set': {'processStatus': 1, 'modifyTime': datetime.utcnow()}})
        self.__update_news_features(record['news_id'], features, 'skip')
        # re produce tags for mentioned companies
        for cid in cids:
            self.company_tagger.extract(cid, fast=True, update_only=True)
        # 大公司打上大公司标签
        if 578354 in features:
            for cid in cids:
                if self.mongo.article.news.find({'processStatus': 1,
                                                 'companyIds': cid, 'features': 578354}).count() >= 3:
                    dbutil.update_company_tag(self.db, cid, 599843, 0, active='H')

        # track for company message and investor message
        for (feed_back, feed_type) in self.news_tracker.feed_1001_4tasks([record]):
            if feed_back:
                if feed_type == 'cm':
                    self.news_tracker.send_company_message_msg(feed_back)
                elif feed_type == 'im':
                    self.news_tracker.send_investor_message_msg(feed_back)

        # track for topic 30, 首次媒体报道
        self.track_topic_30(record)

        # send message to task company
        source = 'news_funding' if category == 60101 else 'news_regular'
        try:
            producer_news_task.send_messages("task_company",
                                             json.dumps({'source': source, 'id': record['news_id'],
                                                         'posting_time': datetime.now().strftime('%Y-%m-%d:%H:%M:%S')}))
        except FailedPayloadsError, fpe:
            init_kafka()
            producer_news_task.send_messages("task_company",
                                             json.dumps({'source': source, 'id': record['news_id'],
                                                         'posting_time': datetime.now().strftime('%Y-%m-%d:%H:%M:%S')}))

    def __process_step2(self, record):

        global producer_news_task

        # not news
        if record.get('processStatus', 0) != 1:
            self.mongo.article.news.update({'_id': ObjectId(record['news_id'])}, {'$set': {'processStatus': -1}})
            return
        if record.get('source', 0) == 'gongshang':
            return

        # update article news
        news_tags = [int(tid) for tid in record.get('newsTags', [])]
        news_sectors = self.__map_sectors(news_tags)
        orginal_features = [int(tid) for tid in
                            self.mongo.article.news.find_one({'_id': ObjectId(record['news_id'])}).get('features', [])]
        industry_tags = [tid for tid in orginal_features if dbutil.get_tag_info(self.db, tid).type < 11050]
        dup_industry_tags = [tid for tid in industry_tags if tid not in news_tags]
        update_features = [tid for tid in orginal_features if tid not in dup_industry_tags]
        self.mongo.article.news.update({'_id': ObjectId(record['news_id'])},
                                       {'$set': {'sectors': news_sectors, 'processStatus': 1,
                                                 'modifyTime': datetime.utcnow(),
                                                 'features': update_features}})
                                        # '$addToSet': {'features': {'$each': news_tags}}})

        # update tags as features
        features = record.get('newsTags', [])
        self.mongo.article.news.update({'_id': ObjectId(record['news_id'])},
                                       {'$set': {'processStatus': 1, 'modifyTime': datetime.utcnow()}})
        self.__update_news_features(record['news_id'], tn2_features=features)

        # re produce tags for mentioned companies
        # for cid in record.get('companyIds'):
        #     self.company_tagger.extract(cid, fast=True, update_only=True)
        #     # 早期项目加入新闻tag
        #     if dbutil.exist_company_tag(self.db, cid, 579089):
        #         for tid in record.get('newsTags', []):
        #             if dbutil.get_tag_info(self.db, tid, 'sectorType') == 1:
        #                 dbutil.update_company_tag(self.db, cid, tid, 2.9001, verify='Y')
        #             else:
        #                 dbutil.update_company_tag(self.db, cid, tid, 1.9001, verify='Y')

    def __update_news_features(self, nid, tn1_features=None, tn2_features=None):

        features = set()
        if not tn1_features:
            tn1 = self.mongo.task.news.find_one({'news_id': nid, 'processStatus': 1, 'section': 'step1'})
            if tn1:
                features.update(tn1.get('categories', []))
                features.add(tn1.get('sentiment'))
        else:
            features.update(tn1_features)
        if tn2_features == 'skip':
            pass
        elif not tn2_features:
            tn2 = self.mongo.task.news.find_one({'news_id': nid, 'processStatus': 1, 'section': 'step2'})
            if tn2:
                features.update(tn2.get('newsTags', []))
        else:
            features.update(tn2_features)
        features = [int(f) for f in features if f]
        self.mongo.article.news.update({'_id': ObjectId(nid)}, {'$set': {'features': features}})

        # process other features
        self.news_tagger.label_11800(nid)
        self.news_tagger.label_11810(nid)

    def __map_sectors(self, tags):

        if not tags:
            return [int(999)]
        sectors = [int(s.id) for s in self.db.query('select id from sector where tagId in %s and active="Y";', tags)]
        return sectors if sectors else [int(999)]

    def __map_category(self, categories):

        if 578349 in categories:
            return 60101
        elif 578351 in categories or 578350 in categories or 605265 in categories:
            return 60104
        elif 578354 in categories:
            return 60105
        elif 578352 in categories or 578356 in categories or 578357 in categories:
            return 60107
        elif 128 in categories or 578353 in categories:
            return 60102
        elif 605264 in categories:
            return 60103
        return None

    def __process_relevant(self, tnid, relevant):

        global logger_news_post
        logger_news_post.info('Processing relevant news, %s, %s' % (tnid, str(relevant)))
        relevant = [self.mongo.task.news.find_one({'_id': ObjectId(rtnid)}) for rtnid in relevant]
        tn_record = self.mongo.task.news.find_one({'_id': ObjectId(tnid)})
        to_be_copy = [str(r.get('_id')) for r in relevant]
        processed = [r for r in relevant if r.get('processStatus', 0) == 1]
        # logger_news_post.info(processed)
        # logger_news_post.info(tn_record)
        # logger_news_post.info(type(tn_record))
        if processed:
            template = deepcopy(processed[0])
            to_be_copy.append(tnid)
        else:
            template = deepcopy(tn_record)
        # logger_news_post.info(to_be_copy)
        for tnid2copy in to_be_copy:
            template['_id'] = ObjectId(tnid2copy)
            source_record = self.mongo.task.news.find_one({'_id': ObjectId(tnid2copy)})
            template['news_id'] = source_record.get('news_id')
            template['news_date'] = source_record.get('news_date')
            template['createTime'] = source_record.get('createTime')
            template['modifyUser'] = source_record.get('modifyUser', False) or template.get('modifyUser')
            template['relevant'] = source_record.get('relevant')
            self.mongo.task.news.update({'_id': ObjectId(tnid2copy)}, template)
            self.process(tnid2copy, True)

    def track_topic_30(self, task):

        """
        首次媒体报道
        """

        global producer_news_task
        news = list(self.mongo.article.news.find({'_id': ObjectId(task['news_id'])}))[0]
        if news.get('date') and news['date'] < (datetime.now() - timedelta(days=self.news_timeliness)):
            return
        # 融资新闻排除
        if 578349 in news.get('features', []):
            return
        for cid in task.get('companyIds', []):
            # establish date greater than 5 years
            if dbutil.get_company_establish_date(self.db, cid) < (datetime.now() - timedelta(days=365*5)).date():
                continue
            if len(list(self.mongo.article.news.find({'companyIds': cid}))) == 1:
                active = 'Y' if dbutil.get_topic_auto_pubilsh_status(self.db, 30) == 'Y' else 'P'
                # tpm = dbutil.update_topic_message(self.db, 30, u'发现一家新公司', active, 10, task['news_id'])
                tpm = dbutil.update_topic_message(self.db, 30, news.get('title', ''), active, 10, task['news_id'])
                tpc = dbutil.update_topic_company(self.db, 30, cid, active)
                if tpm:
                    dbutil.update_topic_message_company(self.db, tpm, tpc)
                if active == 'Y':
                    try:
                        producer_news_task.send_messages("track_message_v2",
                                                         json.dumps({'id': tpm, 'type': 'topic_message',
                                                                     'action': 'create'}))
                        producer_news_task.send_messages("track_message_v2",
                                                         json.dumps({'id': tpc, 'type': 'topic_company',
                                                                     'action': 'create'}))
                    except FailedPayloadsError, fpe:
                        init_kafka()
                        producer_news_task.send_messages("track_message_v2",
                                                         json.dumps({'id': tpm, 'type': 'topic_message',
                                                                     'action': 'create'}))
                        producer_news_task.send_messages("track_message_v2",
                                                         json.dumps({'id': tpc, 'type': 'topic_company',
                                                                     'action': 'create'}))


def init_kafka():

    global consumer_news_task, producer_news_task

    url = tsbconfig.get_kafka_config()
    # HashedPartitioner is default
    consumer_news_task = KafkaConsumer("task", group_id="news_task_post",
                                       bootstrap_servers=[url], auto_offset_reset='smallest')
    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    producer_news_task = SimpleProducer(kafka)


def process_news_post_incremental():

    global logger_news_post, consumer_news_task, producer_news_task
    logger_news_post.info('Incremental news task post processing initializing')
    processer = NewsTaskPostProcesser()
    socket.setdefaulttimeout(0.5)
    init_kafka()

    while True:
        try:
            logger_news_post.info('Incremental news task post processing starts')
            for message in consumer_news_task:
                try:
                    logger_news_post.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                                         message.offset, message.key,
                                                                         message.value))
                    tnid = json.loads(message.value).get('task_newsId')
                    processer.process(tnid)
                    msg = {'type': 'news', 'newsId': json.loads(message.value).get('newsId')}
                    try:
                        producer_news_task.send_messages("task_news_done", json.dumps(msg))
                    except FailedPayloadsError, fpe:
                        logger_news_post.exception('Kafka Payload Error, re-init')
                        init_kafka()
                        producer_news_task.send_messages("task_news_done", json.dumps(msg))
                    logger_news_post.info('%s done, message sent' % tnid)
                except Exception, e:
                    logger_news_post.exception("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                                              message.offset, message.key,
                                                                              message.value))
                    logger_news_post.exception(e)
        except Exception, e:
            logger_news_post.exception('System Error, %s' % e)


if __name__ == '__main__':

    print __file__
    if sys.argv[1] == 'incr' or sys.argv[1] == 'incremental':
        process_news_post_incremental()
