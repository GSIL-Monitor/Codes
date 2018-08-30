# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil
from task.tc import TaskCompanyGenerator
from email_helper import send_mail_file

import json
import logging
import codecs
import pandas
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from collections import defaultdict
from itertools import chain


# logging
logging.getLogger('sourcing').handlers = []
logger_sourcing = logging.getLogger('sourcing')
logger_sourcing.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_sourcing.addHandler(stream_handler)


class SourcingTracker(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

        self.check_gap = 5
        today = datetime.now()
        self.today = datetime(today.year, today.month, today.day)
        self.last_check_time = datetime.now() - timedelta(hours=self.check_gap)
        self.utc_last_check_time = self.last_check_time - timedelta(hours=8)
        self.current_check_time = self.last_check_time + timedelta(hours=self.check_gap)

        self.tcg = TaskCompanyGenerator()

    def generate_items(self):

        self.__generate_c1_3()
        self.__generate_c1_5()
        self.__generate_c1_6()
        self.__generate_c1_7()
        self.__generate_c2_101()  # 1 included
        # self.__generate_c2_102()  # 2 included
        self.__generate_c2_103()
        self.__generate_c2_104()
        self.__general_c2_105()  # 4 included
        self.__generate_c2_106()
        self.__generate_c3_201()
        self.__generate_c3_202()
        self.__generate_c3_203()
        # self.__generate_c3_204()

    def __generate_c1_3(self):

        # 发布新的应用
        for cm in dbutil.get_all_company_messages(self.db, 2001, self.last_check_time):
            if self.__valid_company(cm.companyId):
                siid = dbutil.get_saoanzi_item(self.db, cm.companyId, self.today)
                dbutil.update_saoanzi_item_source(self.db, siid, 3, 91, cm.id)
                dbutil.update_saoanzi_item_cate(self.db, siid, cateid=1)

    def __generate_c1_5(self):

        # 新招聘
        for tc in self.mongo.task.company.find({'processStatus': {'$gte': 1}, 'types': 'company_job',
                                                'finishTime': {'$gte': self.utc_last_check_time}}):
            if self.__valid_company(tc.get('companyId')):
                cmid = dbutil.get_new_company_message(self.db, tc.get('companyId'), u'今日招聘网站上出现的新公司', 10002)
                siid = dbutil.get_saoanzi_item(self.db, tc.get('companyId'), self.today)
                dbutil.update_saoanzi_item_source(self.db, siid, 5, 91, cmid)
                dbutil.update_saoanzi_item_cate(self.db, siid, cateid=1)

    def __generate_c1_6(self):

        for tpm in dbutil.get_topic_messages(self.db, 30, self.last_check_time):
            # source 6 第一次媒体播报
            news = self.mongo.article.news.find_one({'_id': ObjectId(tpm.relateId)})
            if news:
                for cid in news.get('companyIds', []):
                    if self.__valid_company(cid):
                        siid = dbutil.get_saoanzi_item(self.db, cid, self.today)
                        dbutil.update_saoanzi_item_source(self.db, siid, 6, 90, tpm.id)
                        dbutil.update_saoanzi_item_cate(self.db, siid, cateid=1)

    def __generate_c1_7(self):

        # 新收录
        for tc in self.mongo.task.company.find({'processStatus': {'$gte': 1},
                                                'finishTime': {'$gte': self.utc_last_check_time},
                                                'types': {'$in': ['company_create', 'company_newcover']}}):
            if self.__valid_company(tc.get('companyId')):
                cmid = dbutil.get_new_company_message(self.db, tc.get('companyId'), u'今日新收录公司', 10001)
                siid = dbutil.get_saoanzi_item(self.db, tc.get('companyId'), self.today)
                dbutil.update_saoanzi_item_source(self.db, siid, 7, 91, cmid)
                dbutil.update_saoanzi_item_cate(self.db, siid, cateid=1)
        # for cid in dbutil.get_company_ids_by_create(self.db, self.last_check_time):
        #     siid = dbutil.get_saoanzi_item(self.db, cid, self.today)
        #     dbutil.update_saoanzi_item_source(self.db, siid, 7)
        #     dbutil.update_saoanzi_item_cate(self.db, siid, cateid=1)

    def __generate_c2_101(self):

        for tpm in dbutil.get_topic_messages(self.db, 26, self.last_check_time):
            # source 101 获得新一轮融资
            cid = dbutil.get_funding(self.db, tpm.relateId).companyId
            if self.__valid_company(cid):
                siid = dbutil.get_saoanzi_item(self.db, cid, self.today)
                dbutil.update_saoanzi_item_source(self.db, siid, 101, 90, tpm.id)
                dbutil.update_saoanzi_item_cate(self.db, siid, cateid=2)
                # source 1, 第一次获得融资
                if len(dbutil.get_company_funding(self.db, cid)) == 1:
                    dbutil.update_saoanzi_item_source(self.db, siid, 1, 90, tpm.id)
                    dbutil.update_saoanzi_item_cate(self.db, siid, cateid=1)

    def __generate_c2_102(self):

        for cm in dbutil.get_all_company_messages(self.db, 8001, self.last_check_time):
            # source 102 开启新一轮融资
            if self.__valid_company(cm.companyId):
                siid = dbutil.get_saoanzi_item(self.db, cm.companyId, self.today)
                dbutil.update_saoanzi_item_source(self.db, siid, 102, 91, cm.id)
                dbutil.update_saoanzi_item_cate(self.db, siid, cateid=2)
                # source 2 第一次开启融资
                if len([ccm.id for ccm in dbutil.get_company_messages(self.db, cm.companyId, 'Y')
                        if ccm.trackDimension == 8001]) == 1:
                    dbutil.update_saoanzi_item_source(self.db, siid, 2, 91, cm.id)
                    dbutil.update_saoanzi_item_cate(self.db, siid, cateid=1)

    def __generate_c2_103(self):

        # 每日退出
        for tpm in dbutil.get_topic_messages(self.db, 27, self.last_check_time):
            cid = dbutil.get_funding(self.db, tpm.relateId).companyId
            if self.__valid_company(cid):
                siid = dbutil.get_saoanzi_item(self.db, cid, self.today)
                dbutil.update_saoanzi_item_source(self.db, siid, 103, 90, tpm.id)
                dbutil.update_saoanzi_item_cate(self.db, siid, cateid=2)

    def __generate_c2_104(self):

        # 下载激增
        for tpm in dbutil.get_topic_messages(self.db, 8, self.last_check_time):
            for cid in dbutil.get_topic_message_companies(self.db, tpm.id):
                if self.__valid_company(cid):
                    siid = dbutil.get_saoanzi_item(self.db, cid, self.today)
                    dbutil.update_saoanzi_item_source(self.db, siid, 104, 90, tpm.id)
                    dbutil.update_saoanzi_item_cate(self.db, siid, cateid=2)

    def __general_c2_105(self):

        for cm in dbutil.get_all_company_messages(self.db, 3107, self.last_check_time):
            if self.__valid_company(cm.companyId):
                # source 105 今日入榜的公司
                siid = dbutil.get_saoanzi_item(self.db, cm.companyId, self.today)
                dbutil.update_saoanzi_item_source(self.db, siid, 105, 91, cm.id)
                dbutil.update_saoanzi_item_cate(self.db, siid, cateid=2)
                # source 4 第一次入榜的公司
                domain = dbutil.get_artifact_info(self.db, cm.relateId, 'domain')
                genre, atype = int(cm.detailId.split(',')[0]), cm.detailId.split(',')[1]
                previous = self.mongo.trend.appstore_rank.find({'trackId': domain, 'genre': genre, 'type': atype,
                                                                'rank': {'$lt': 100}}).count()
                if previous == 1:
                    dbutil.update_saoanzi_item_source(self.db, siid, 4, 91, cm.id)
                    dbutil.update_saoanzi_item_cate(self.db, siid, cateid=1)

    def __generate_c2_106(self):

        # 工商变更
        for tpm in dbutil.get_topic_messages(self.db, 44, self.last_check_time):
            for cid in dbutil.get_topic_message_companies(self.db, tpm.id):
                if self.__valid_company(cid):
                    siid = dbutil.get_saoanzi_item(self.db, cid, self.today)
                    dbutil.update_saoanzi_item_source(self.db, siid, 106, 90, tpm.id)
                    dbutil.update_saoanzi_item_cate(self.db, siid, cateid=2)

    def __generate_c3_201(self):

        # 负面新闻
        # for tpm in dbutil.get_topic_messages(self.db, 37, self.last_check_time):
        #     for cid in dbutil.get_topic_message_companies(self.db, tpm.id):
        #         if self.__valid_company(cid):
        #             siid = dbutil.get_saoanzi_item(self.db, cid, self.today)
        #             dbutil.update_saoanzi_item_source(self.db, siid, 201, 90, tpm.id)
        #             dbutil.update_saoanzi_item_cate(self.db, siid, cateid=3)
        for news in self.mongo.article.news.find({'date': {'$gte': self.today, '$lte': self.today + timedelta(days=1)},
                                                  'processStatus': 1, 'features': 578362}):
            for cid in news.get('companyIds', []):
                if self.__valid_company(cid):
                    cm = dbutil.get_news_company_message(self.db, cid, str(news['_id']))
                    print 'bad', cm
                    if cm:
                        siid = dbutil.get_saoanzi_item(self.db, cid, self.today)
                        dbutil.update_saoanzi_item_source(self.db, siid, 201, 91, cm.id)
                        dbutil.update_saoanzi_item_cate(self.db, siid, cateid=3)

    def __generate_c3_202(self):

        # 热议
        tpms = []
        for tpid in [16, 20, 21, 22, 38]:
            tpms.extend(dbutil.get_topic_messages(self.db, tpid, self.last_check_time))
        for tpm in tpms:
            for cid in dbutil.get_topic_message_companies(self.db, tpm.id):
                if self.__valid_company(cid):
                    siid = dbutil.get_saoanzi_item(self.db, cid, self.today)
                    dbutil.update_saoanzi_item_source(self.db, siid, 202, 90, tpm.id)
                    dbutil.update_saoanzi_item_cate(self.db, siid, cateid=3)

    def __generate_c3_203(self):

        # 新闻
        for cm in dbutil.get_all_company_messages(self.db, 1001, self.last_check_time):
            if self.__valid_company(cm.companyId):
                siid = dbutil.get_saoanzi_item(self.db, cm.companyId, self.today)
                dbutil.update_saoanzi_item_source(self.db, siid, 203, 91, cm.id)
                dbutil.update_saoanzi_item_cate(self.db, siid, cateid=3)

    def __generate_c3_204(self):

        # 大公司
        for tpm in dbutil.get_topic_messages(self.db, 46, self.last_check_time):
            for cid in dbutil.get_topic_message_companies(self.db, tpm.id):
                if self.__valid_company(cid):
                    siid = dbutil.get_saoanzi_item(self.db, cid, self.today)
                    dbutil.update_saoanzi_item_source(self.db, siid, 204, 90, tpm.id)
                    dbutil.update_saoanzi_item_cate(self.db, siid, cateid=3)

    def clear_items(self):

        global logger_sourcing
        file_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], u'dumps/saoanzi.csv')
        data = []
        for anzi in dbutil.get_daily_saoanzi_sources(self.db, self.today):
            cactive = dbutil.get_company_active(self.db, anzi.companyId)
            need_verify = self.tcg.need_verify(anzi.companyId)
            if need_verify or (cactive != 'Y'):
                self.tcg.generate_tc(json.dumps({'id': anzi.companyId, 'source': 'track_saoanzi'}))
                dbutil.update_saoanzi_item_status(self.db, anzi.saoanziItemId, 'P')
            elif not self.__valid_message(anzi):
                dbutil.update_saoanzi_item_status(self.db, anzi.saoanziItemId, 'N')
            else:
                dbutil.update_saoanzi_item_status(self.db, anzi.saoanziItemId, 'Y')
            url = "http://pro.xiniudata.com/validator/#/company/%s/overview" \
                  % dbutil.get_company_code(self.db, anzi.companyId)
            # sources = ';'.join([s.name for s in dbutil.get_saoanzi_item_sources(self.db, anzi.id)])
            source = anzi.source
            need_verify = u'需要检查' if (need_verify or (cactive != 'Y')) else u'不需要检查'
            data.append([dbutil.get_company_name(self.db, anzi.companyId), url, need_verify, anzi.createTime, source])
        if not data:
            return
        # send email
        data = pandas.DataFrame(data)
        data.to_csv(file_path, encoding='utf_8_sig')
        # stat_verify = {title: len(set(detail[0])) for title, detail in data.groupby(3)}
        stat_verify = '<br/>'.join(['%s\t%s' % (title, len(set(detail[0]))) for title, detail in data.groupby(2)])
        # stat_source = {title: len(detail) for title, detail in data.groupby(5)}
        stat_source = '<br/>'.join(['%s\t%s' % (title, len(detail)) for title, detail in data.groupby(4)])
        stat = u'去重公司数<br/>%s<br/>每个源下的公司数<br/>%s\n' % (stat_verify, stat_source)
        receivers = ['victor', 'erin', 'weiguangxiao', 'gewei']
        receivers = ';'.join(['%s@xiniudata.com' % r for r in receivers])
        title = u'扫案子项目列表 %s' % self.current_check_time.strftime('%Y-%m-%d %H')
        content = u'%s检查，今天共有%s个扫案子条目<br/>%s' % \
                  (self.current_check_time.strftime('%Y-%m-%d %H:%M'), len(data), stat)
        send_mail_file(u'烯牛扫案子后台', u'烯牛扫案子后台', "noreply@xiniudata.com", receivers, title, content, file_path)

    def __valid_company(self, cid):

        lid = dbutil.get_company_location(self.db, cid)[0]
        if lid and lid > 370:
            return False
        return True

    def __valid_message(self, anzi):

        if anzi.relateType and anzi.relateType == 90:
            if dbutil.get_topic_message(self.db, anzi.relateId).active != "Y":
                return False
            return True
        if anzi.relateType and anzi.relateType == 91:
            cm = dbutil.get_company_message(self.db, anzi.relateId)
            if cm.relateType and cm.relateType == 10:
                return cm.active == 'Y'
            elif cm.relateType and cm.relateType in (20, 30):
                if cm.active != 'Y':
                    return False
                active = dbutil.get_artifact_info(self.db, cm.relateId, 'active')
                if active and active != 'Y':
                    return False
                return True
        if anzi.relateType and anzi.relateType == 10:
            return False
        return True

    def summarize_items(self):

        dbutil.update_saoanzi_source_summary(self.db, self.today, self.current_check_time)
        dbutil.update_saoanzi_cate_summary(self.db, self.today, self.current_check_time)
        # user relevant
        anzis = defaultdict(set)
        for anzi in dbutil.get_daily_saoanzi_items(self.db, self.today):
            for tid in dbutil.get_company_sector_tag(self.db, anzi.companyId):
                anzis[tid].add(anzi.id)
        for user in dbutil.get_saoanzi_users(self.db):
            user_anzis = set(chain(*[anzis.get(tid, set()) for tid in dbutil.get_user_sanaozi_sectors(self.db, user)]))
            user_sources = set(dbutil.get_user_sanaozi_sources(self.db, user))
            user_anzis = [anzi for anzi in user_anzis
                          if set([s.id for s in dbutil.get_saoanzi_item_sources(self.db, anzi)]) & user_sources]
            # total
            dbutil.update_saoanzi_user_summary(self.db, user, len(user_anzis), self.current_check_time)
            # each source
            if user_anzis:
                dbutil.update_saoanzi_user_source_summary(self.db, user, user_anzis,
                                                          self.current_check_time, self.today)
            else:
                dbutil.update_saoanzi_user_source_summary(self.db, user, [], self.current_check_time, self.today)

    def process_progress(self):

        pass

    def source(self):

        global logger_sourcing
        logger_sourcing.info('Start to process sourcing items')
        self.generate_items()
        logger_sourcing.info('Start to clear invalid sourcing items')
        self.clear_items()
        logger_sourcing.info('Start to summarize sourcing items')
        self.summarize_items()
        logger_sourcing.info('Start to process progress')
        self.process_progress()

    def test(self):

        anzis = defaultdict(set)
        for anzi in dbutil.get_daily_saoanzi_items(self.db, self.today):
            for tid in dbutil.get_company_sector_tag(self.db, anzi.companyId):
                anzis[tid].add(anzi.id)
        for tid in dbutil.get_user_sanaozi_sectors(self.db, 215):
            print tid, anzis.get(tid, set())


if __name__ == '__main__':

    if sys.argv[1] == 'source':
        st = SourcingTracker()
        st.source()
    elif sys.argv[1] == 'summarize':
        st = SourcingTracker()
        st.summarize_items()
    elif sys.argv[1] == 'test':
        st = SourcingTracker()
        st.test()
