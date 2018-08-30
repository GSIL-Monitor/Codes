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
from company_track import CompanyRecruitTracker, CompanyGongshangTracker, CompanyProductTracker
from company_news_track import NewsFundingCompanyTracker
from company_funding_track import OnFundingCompanyTracker
from trend_track import AppStoreRankCompanyTracker
from special_track import fa_relevant_track

import time
import logging
from datetime import datetime

from kafka import KafkaClient, SimpleProducer
from kafka.errors import FailedPayloadsError

# logging
logging.getLogger('track').handlers = []
logger_track = logging.getLogger('track')
logger_track.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_track.addHandler(stream_handler)


producer_track = None


# init kafka
def init_kafka():

    global producer_track
    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    producer_track = SimpleProducer(kafka)


def c2001():

    """
    2001 新产品上线
    """

    global logger_track
    cpt = CompanyProductTracker()
    cpt.track_2001(logger_track)


def c2002_2003():

    """
    2002 重要版本发布
    2003 版本更新
    """

    global logger_track
    cpt = CompanyProductTracker()
    cpt.track_2002_2003(logger_track)


def c2004():

    """
    2004 iOS产品下架
    """

    global logger_track
    cpt = CompanyProductTracker()
    cpt.track_2004(logger_track)


def c2005():

    """
    2005 产品长期无更新
    """

    global logger_track
    cpt = CompanyProductTracker()
    cpt.track_2005(logger_track)


def c3107():

    """
    3107 and 3108, App Store 进出榜
    """
    t3100 = AppStoreRankCompanyTracker()
    for dimension, feedbacks in t3100.update_app_rank().items():
        for feedback in feedbacks:
            if feedback:
                t3100.send_company_message_msg(feedback)


def c3109():

    """
    3109 AppStore 榜单表现出彩
    """
    t3109 = AppStoreRankCompanyTracker()
    t3109.update_3109()


def c4002():

    """
    4002 长期无新职位发布, update every week
    """

    global logger_track
    crt = CompanyRecruitTracker()
    db = dbcon.connect_torndb()
    today = datetime.today()
    for cid in dbutil.get_all_company_id(db):
        feed_back = crt.feed_4002(cid, today)
        if feed_back:
            crt.send_company_message_msg(feed_back)
            logger_track.info('4002 %s' % cid)
    db.close()


def c4004():

    """
    4004 招聘CTO, COO等核心职位, update every day
    """

    global logger_track
    crt = CompanyRecruitTracker()
    db = dbcon.connect_torndb()
    today = datetime.today()
    for cid in dbutil.get_all_company_id(db):
        for feed_back in crt.feed_4004(cid, today):
            if feed_back:
                crt.send_company_message_msg(feed_back)
                logger_track.info('4004 %s' % cid)
    db.close()


def c5001_5002():

    """
    5001 股东变更
    5002 注册资本变更
    update every day
    """

    global logger_track
    cgt = CompanyGongshangTracker()
    db = dbcon.connect_torndb()
    logger_track.info('Processing gongshang change')
    for cid in dbutil.get_all_company_id(db):
        cgt.feed(cid, logger_track)
    db.close()


def c7002():

    """
    新的一轮融资
    """
    global logger_track
    init_kafka()
    nft = NewsFundingCompanyTracker()
    logger_track.info('News Funding Tracker inited')
    while True:
        nft.feed_incremental()
        logger_track.info('Finish one round')
        time.sleep(60)


def c8001():

    """
    开始融资
    """
    global logger_track
    init_kafka()
    logger_track.info('Start to track 8001')
    oft = OnFundingCompanyTracker()
    oft.update_all_onfunding()
    logger_track.info('Start to track for topic 52')
    fa_relevant_track()


def newgs():

    """"
    process new names mentioned in gongshang tracking
    """
    gst = CompanyGongshangTracker()
    gst.feed_invests()


if __name__ == '__main__':

    print __file__
    # 1001 in news postprocess
    # 6001 in comps
    if sys.argv[1] == '2001':
        c2001()
    elif sys.argv[1] == '2002' or sys.argv[1] == '2003':
        c2002_2003()
    elif sys.argv[1] == '2004':
        c2004()
    elif sys.argv[1] == '2005':
        c2005()
    elif sys.argv[1] == '3100':
        c3107()
    elif sys.argv[1] == '4002':
        c4002()
    elif sys.argv[1] == '4004':
        c4004()
    elif sys.argv[1] == '5001' or sys.argv[1] == '5002':
        c5001_5002()
    elif sys.argv[1] == '7002':
        c7002()  # 7005 included
    elif sys.argv[1] == '8001':
        c8001()
    elif sys.argv[1] == 'newgs':
        newgs()
